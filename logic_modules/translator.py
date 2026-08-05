"""
Multi-language translation engine for the Abdul for Senate platform.
Uses deep-translator (Google Translate backend, no API key required)
with JSON file caching to avoid redundant translations and stay
within rate limits.

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
import hashlib
from deep_translator import GoogleTranslator

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
}

# Direction: RTL languages
RTL_LANGUAGES = {"ar", "ur", "fa", "iw"}

_cache = None


def _load_cache():
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            _cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _cache = {}
    return _cache


def _save_cache():
    global _cache
    if _cache is None:
        return
    try:
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(_cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # silently fail on cache writes


def _cache_key(text, target):
    """Generate a deterministic cache key from text + target language."""
    raw = f"{text}||{target}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


def translate(text, target):
    """
    Translate a single text string to the target language.
    Returns the translated text (or original if translation fails).
    """
    if not text or not text.strip():
        return text

    # Normalize — don't translate pure numbers, short codes, or ASCII-only machine output
    text_stripped = text.strip()
    if text_stripped.isdigit():
        return text
    if len(text_stripped) <= 2:
        return text

    cache = _load_cache()
    key = _cache_key(text, target)

    if key in cache:
        return cache[key]

    try:
        translator = GoogleTranslator(source='auto', target=target)
        translated = translator.translate(text)
        if translated:
            cache[key] = translated
            _save_cache()
            return translated
    except Exception:
        pass  # fallback to original on error

    return text


def translate_batch(texts, target):
    """
    Translate a list of texts. Returns a list of translated strings
    in the same order. Uses caching and falls back to original on error.
    """
    return [translate(t, target) for t in texts]


def is_rtl(lang_code):
    """Check if a language is right-to-left."""
    return lang_code in RTL_LANGUAGES


def get_language_name(code):
    """Get the human-readable name for a language code."""
    return LANGUAGES.get(code, code)