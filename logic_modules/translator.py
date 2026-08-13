"""
Multi-language translation engine for the Abdul for Senate platform.
Uses deep-translator (Google Translate backend, no API key required)
with JSON file caching to avoid redundant translations and stay
within rate limits.

Resilience features for cloud deployments:
  - Error classification (rate-limit, transient, permanent)
  - Exponential backoff + jitter retry for rate limits / transient errors
  - Circuit breaker: after repeated failures, stop calling upstream for
    a cooldown window so a blocked cloud IP doesn't get hammered
  - Per-process throttle: minimum interval between upstream calls
  - Bounded on-disk cache + in-memory overlay so disk-write failures
    never lose in-process entries
  - Graceful per-item fallback: a hard failure returns the original text
    rather than raising, while still surfacing status for the API layer

Supported languages:
  ar → Arabic            zh-CN → Chinese (Simplified)
  pl → Polish            iw   → Hebrew (Chaldean Aramaic)
  vi → Vietnamese        de   → German
  hi → Hindi             gu   → Gujarati
  pa → Punjabi           ur   → Urdu
  bn → Bengali           es   → Spanish
  fr → French            bs   → Bosnian
  fa → Farsi / Persian
"""

import json
import os
import time
import random
import hashlib
import threading

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translation_cache.json')

# Language codes supported
LANGUAGES = {
    "ar": "Arabic",
    "zh-CN": "Chinese (Simplified)",
    "pl": "Polish",
    "iw": "Chaldean Aramaic (Hebrew)",
    "vi": "Vietnamese",
    "de": "German",
    "hi": "Hindi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "bn": "Bengali",
    "es": "Spanish",
    "fr": "French",
    "bs": "Bosnian",
    "fa": "Farsi / Persian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
}

# Direction: RTL languages
RTL_LANGUAGES = {"ar", "ur", "fa", "iw"}

# ─── Resilience tunables (env-overridable for cloud tuning) ───

# Max items accepted in a single translate_batch() call.
MAX_BATCH_SIZE = int(os.environ.get('TRANSLATE_MAX_BATCH', '200'))

# Minimum seconds between upstream (deep-translator) calls.
MIN_REQUEST_INTERVAL = float(os.environ.get('TRANSLATE_MIN_INTERVAL', '0.35'))

# Retry policy (exponential backoff with jitter).
MAX_RETRIES = int(os.environ.get('TRANSLATE_MAX_RETRIES', '3'))
BASE_BACKOFF = float(os.environ.get('TRANSLATE_BASE_BACKOFF', '1.0'))   # seconds
MAX_BACKOFF = float(os.environ.get('TRANSLATE_MAX_BACKOFF', '12.0'))    # seconds

# Circuit breaker: after this many consecutive upstream failures, enter
# cooldown and refuse upstream calls for COOLDOWN_SECONDS.
CIRCUIT_FAIL_THRESHOLD = int(os.environ.get('TRANSLATE_CIRCUIT_THRESHOLD', '5'))
CIRCUIT_COOLDOWN = float(os.environ.get('TRANSLATE_CIRCUIT_COOLDOWN', '60.0'))

# On-disk cache cap (approx entries). 0 disables the cap.
CACHE_MAX_ENTRIES = int(os.environ.get('TRANSLATE_CACHE_MAX', '20000'))


# ─── Error taxonomy ───

class TranslationError(Exception):
    """Base class for all translation-engine errors."""


class RateLimitError(TranslationError):
    """Upstream (Google) rejected us for exceeding allowed request volume."""


class TransientError(TranslationError):
    """Temporary upstream / network failure — safe to retry."""


class PermanentError(TranslationError):
    """Unrecoverable failure — retrying will not help."""


class CircuitOpenError(TranslationError):
    """Circuit breaker is open; upstream calls are paused for cooldown."""


# ─── Module state (protected by a lock for multi-threaded gunicorn) ───

_lock = threading.RLock()

_cache = None            # on-disk cache (loaded lazily)
_memory_cache = {}       # in-memory overlay for entries not yet persisted
_persisted_keys = set()  # keys already written to disk (for memory overlay lookup)

_circuit_failures = 0
_circuit_open_until = 0.0
_last_upstream_call = 0.0


# ─── Cache helpers ───

def _load_cache():
    """Load the on-disk cache once. Returns {} on any failure."""
    global _cache, _persisted_keys
    if _cache is not None:
        return _cache
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        _persisted_keys = set(data.keys())
        _cache = data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        _cache = {}
        _persisted_keys = set()
    return _cache


def _trim_cache_locked():
    """Trim the on-disk cache to CACHE_MAX_ENTRIES (oldest removed)."""
    if not CACHE_MAX_ENTRIES or _cache is None:
        return
    if len(_cache) <= CACHE_MAX_ENTRIES:
        return
    # dicts preserve insertion order → pop oldest
    overflow = len(_cache) - CACHE_MAX_ENTRIES
    for _ in range(overflow):
        try:
            _cache.pop(next(iter(_cache)))
        except (StopIteration, KeyError):
            break


def _save_cache():
    """Persist cache + memory overlay to disk. Never raises."""
    global _cache
    with _lock:
        if _cache is None:
            _cache = _load_cache()
        # Merge memory overlay into the disk-backed dict
        if _memory_cache:
            _cache.update(_memory_cache)
            _persisted_keys.update(_memory_cache.keys())
            _memory_cache.clear()
        _trim_cache_locked()
        try:
            with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            # Keep in-memory overlay so we still serve these this process.
            pass


def _cache_get(key):
    with _lock:
        if key in _memory_cache:
            return _memory_cache[key]
        cache = _load_cache()
        return cache.get(key)


def _cache_set(key, value):
    """Store a translated value. If disk write fails, entry lives in memory."""
    with _lock:
        if _cache is None:
            _cache = _load_cache()
        if key in _persisted_keys:
            _cache[key] = value
        else:
            _memory_cache[key] = value
        _save_cache()


def _cache_key(text, target):
    """Generate a deterministic cache key from text + target language."""
    raw = f"{text}||{target}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


# ─── Circuit breaker / throttle ───

def _record_success():
    global _circuit_failures
    with _lock:
        _circuit_failures = 0


def _record_failure():
    global _circuit_failures, _circuit_open_until
    with _lock:
        _circuit_failures += 1
        if _circuit_failures >= CIRCUIT_FAIL_THRESHOLD:
            _circuit_open_until = time.monotonic() + CIRCUIT_COOLDOWN


def _circuit_open():
    global _circuit_open_until, _circuit_failures
    with _lock:
        if _circuit_open_until and time.monotonic() < _circuit_open_until:
            return True
        if _circuit_open_until and time.monotonic() >= _circuit_open_until:
            # Cooldown expired → allow one probe request
            _circuit_open_until = 0.0
            _circuit_failures = CIRCUIT_FAIL_THRESHOLD - 1  # one more failure trips it again
        return False


def _throttle():
    """Space out upstream calls to stay under Google's per-second limit."""
    global _last_upstream_call
    with _lock:
        now = time.monotonic()
        delta = now - _last_upstream_call
        if delta < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - delta)
        _last_upstream_call = time.monotonic()


def _classify_error(exc):
    """Map an upstream exception to one of our error types."""
    msg = str(exc).lower()

    # Rate limiting — deep-translator raises these when Google blocks us
    if any(token in msg for token in (
        'too many requests', 'rate limit', 'rate-limit', 'quota',
        '429', 'u\'too_many', 'http 429', 'retry'
    )):
        return RateLimitError(str(exc))

    # Captcha / bot detection / blocked IP — permanent until IP changes
    if any(token in msg for token in (
        'captcha', 'not allowed', 'forbidden', '403', 'blocked',
        'unusual traffic', 'access denied'
    )):
        return PermanentError(str(exc))

    # Network-level / temporary
    if any(token in msg for token in (
        'timeout', 'timed out', 'connection', 'socket', 'ssl',
        'http 5', '500', '502', '503', '504', 'temporar',
        'unavailable', 'network', 'eof', 'reset', 'refused',
        'max retries exceeded', 'dns', 'resolve'
    )):
        return TransientError(str(exc))

    # Unknown — assume transient so we retry once, but don't loop forever
    return TransientError(str(exc))


def _translate_with_retry(translator_factory, text, retries=0):
    """
    Perform one upstream translation with exponential backoff + jitter.
    Raises TranslationError subclasses; caller decides fallback.
    """
    if _circuit_open():
        raise CircuitOpenError(
            f'Translation upstream paused for cooldown '
            f'({CIRCUIT_COOLDOWN:.0f}s) after repeated failures.'
        )

    try:
        _throttle()
        translator = translator_factory()
        result = translator.translate(text)
        _record_success()
        return result
    except TranslationError:
        raise  # already classified
    except Exception as exc:  # noqa: BLE001 — deep-translator raises heterogeneous types
        err = _classify_error(exc)

        if isinstance(err, RateLimitError):
            _record_failure()
            if retries < MAX_RETRIES:
                delay = min(
                    MAX_BACKOFF,
                    BASE_BACKOFF * (2 ** retries) + random.uniform(0, 0.5)
                )
                time.sleep(delay)
                return _translate_with_retry(
                    translator_factory, text, retries=retries + 1
                )
            raise err

        if isinstance(err, TransientError) and retries < MAX_RETRIES:
            _record_failure()
            delay = min(
                MAX_BACKOFF,
                BASE_BACKOFF * (2 ** retries) + random.uniform(0, 0.5)
            )
            time.sleep(delay)
            return _translate_with_retry(
                translator_factory, text, retries=retries + 1
            )

        # Permanent error (or retries exhausted)
        _record_failure()
        raise err


# ─── Public API ───

def translate(text, target):
    """
    Translate a single text string to the target language.

    Returns the translated text, or the original text if translation
    cannot be completed (rate limit, circuit open, permanent error…).
    Never raises.
    """
    if not text or not text.strip():
        return text

    text_stripped = text.strip()
    if text_stripped.isdigit():
        return text
    if len(text_stripped) <= 2:
        return text

    key = _cache_key(text, target)
    cached = _cache_get(key)
    if cached is not None:
        return cached

    try:
        from deep_translator import GoogleTranslator

        def factory():
            return GoogleTranslator(source='auto', target=target)

        translated = _translate_with_retry(factory, text)
        if translated:
            _cache_set(key, translated)
            return translated
    except TranslationError:
        pass  # graceful fallback to original
    except Exception:
        pass  # anything else (e.g. import-time) — fall back

    return text


def translate_batch(texts, target):
    """
    Translate a list of texts.

    Returns a list of translated strings in the same order, falling back
    to the original text for any item that cannot be translated.

    If `texts` exceeds MAX_BATCH_SIZE, raises RateLimitError so the API
    layer can respond with an appropriate status code.
    """
    if not texts:
        return []

    if len(texts) > MAX_BATCH_SIZE:
        raise RateLimitError(
            f'Batch of {len(texts)} exceeds maximum of {MAX_BATCH_SIZE}. '
            f'Please reduce the batch size.'
        )

    return [translate(t, target) for t in texts]


def translation_status():
    """
    Return a dict describing the health of the translation engine.
    Useful for a /api/translate/status endpoint and debugging.
    """
    with _lock:
        open_until = None
        if _circuit_open_until:
            remaining = _circuit_open_until - time.monotonic()
            open_until = max(0.0, remaining) if remaining > 0 else 0.0

        return {
            'available': True,
            'circuit_open': _circuit_open_until > time.monotonic(),
            'circuit_cooldown_remaining': open_until,
            'consecutive_failures': _circuit_failures,
            'failure_threshold': CIRCUIT_FAIL_THRESHOLD,
            'min_request_interval': MIN_REQUEST_INTERVAL,
            'max_batch_size': MAX_BATCH_SIZE,
            'cache_entries': len(_load_cache()) + len(_memory_cache),
        }


def clear_circuit_breaker():
    """Manually reset the circuit breaker (useful for ops/debugging)."""
    global _circuit_failures, _circuit_open_until
    with _lock:
        _circuit_failures = 0
        _circuit_open_until = 0.0


def is_rtl(lang_code):
    """Check if a language is right-to-left."""
    return lang_code in RTL_LANGUAGES


def get_language_name(code):
    """Get the human-readable name for a language code."""
    return LANGUAGES.get(code, code)