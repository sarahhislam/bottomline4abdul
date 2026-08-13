from flask import Flask, send_from_directory, redirect, request, jsonify, Response, abort
import importlib
import os
import time
import threading
from collections import defaultdict

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Whitelist of modules we expose via the API to avoid arbitrary imports
ALLOWED_MODULES = {
    'endorsement_engine', 'financial_simulator', 'halal_economy', 'hazard_lookup',
    'myth_buster', 'policy_deep_dive', 'senior_engagement', 'simulation_history',
    'tax_calculator', 'youth_amanah'
}


# ─── Translation engine import (with graceful fallback) ───
try:
    from logic_modules.translator import (
        translate_batch, LANGUAGES, is_rtl,
        RateLimitError, TransientError, PermanentError, CircuitOpenError,
        translation_status, clear_circuit_breaker, MAX_BATCH_SIZE,
    )
    _TRANSLATOR_AVAILABLE = True
except ImportError:
    _TRANSLATOR_AVAILABLE = False
    LANGUAGES = {}
    MAX_BATCH_SIZE = 200

    def is_rtl(_code):
        return False

    def translate_batch(texts, _target):
        raise RuntimeError('deep-translator is not installed')

    def translation_status():
        return {'available': False}

    def clear_circuit_breaker():
        pass

    class RateLimitError(Exception):
        pass

    class TransientError(Exception):
        pass

    class PermanentError(Exception):
        pass

    class CircuitOpenError(Exception):
        pass


# ─── API-level rate limiting (protects upstream translator from abuse) ───
# Simple in-memory sliding window per client IP.
_RATE_WINDOW_SECONDS = float(os.environ.get('API_RATE_WINDOW', '10'))
_RATE_MAX_REQUESTS = int(os.environ.get('API_RATE_MAX', '30'))
_rate_lock = threading.Lock()
_rate_hits = defaultdict(list)   # ip → [timestamps]


def _rate_limited(ip):
    """
    Sliding-window rate check. Returns remaining seconds to wait
    if limited, else None.
    """
    now = time.monotonic()
    with _rate_lock:
        hits = _rate_hits[ip]
        # Drop timestamps outside the window
        _rate_hits[ip] = [t for t in hits if now - t < _RATE_WINDOW_SECONDS]
        if len(_rate_hits[ip]) >= _RATE_MAX_REQUESTS:
            oldest = _rate_hits[ip][0]
            return _RATE_WINDOW_SECONDS - (now - oldest)
        _rate_hits[ip].append(now)
        return None


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/languages')
def api_languages():
    """Return the list of supported languages."""
    if not _TRANSLATOR_AVAILABLE:
        return jsonify({'error': 'Translation unavailable (install deep-translator)'}), 503
    return jsonify({
        code: {"name": name, "rtl": is_rtl(code)}
        for code, name in LANGUAGES.items()
    })


@app.route('/api/translate/status')
def api_translate_status():
    """Health/status of the translation engine (circuit breaker state, cache, etc.)."""
    if not _TRANSLATOR_AVAILABLE:
        return jsonify({'available': False,
                        'error': 'Translation unavailable (install deep-translator)'}), 503
    return jsonify(translation_status())


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """
    Translate a batch of texts.

    POST JSON body: { "texts": [...], "target": "ar" }
    Response: { "translations": [...] }

    Error responses:
      400 — malformed body, unsupported language, empty batch
      413 — batch exceeds MAX_BATCH_SIZE
      429 — request rate limit exceeded (Retry-After set)
      503 — translation engine unavailable / circuit open (Retry-After set)
    """
    if not _TRANSLATOR_AVAILABLE:
        return jsonify({'error': 'Translation unavailable (install deep-translator)'}), 503

    # API-level rate limit per client IP
    client_ip = request.remote_addr or 'unknown'
    retry_after = _rate_limited(client_ip)
    if retry_after is not None:
        resp = jsonify({
            'error': 'Too many translation requests. Please wait a moment and try again.',
            'retry_after': retry_after
        })
        resp.status_code = 429
        resp.headers['Retry-After'] = str(int(retry_after) + 1)
        return resp

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    texts = data.get('texts', [])
    target = data.get('target', 'en')

    if not isinstance(texts, list):
        return jsonify({'error': '"texts" must be an array'}), 400

    if not texts:
        return jsonify({'error': '"texts" must not be empty'}), 400

    if not isinstance(target, str):
        return jsonify({'error': '"target" must be a string'}), 400

    if target not in LANGUAGES and target != 'en':
        return jsonify({'error': f'Unsupported language: {target}'}), 400

    if len(texts) > MAX_BATCH_SIZE:
        return jsonify({
            'error': f'Batch of {len(texts)} exceeds maximum of {MAX_BATCH_SIZE}. '
                     f'Please reduce the batch size.',
            'max_batch_size': MAX_BATCH_SIZE
        }), 413

    if target == 'en':
        return jsonify({'translations': texts})

    try:
        result = translate_batch(texts, target)
        return jsonify({'translations': result})
    except RateLimitError as e:
        # Upstream rate-limited us — let the client back off and retry
        retry_after = getattr(e, 'retry_after', 5)
        resp = jsonify({
            'error': 'Translation service is rate limited. Please try again shortly.',
            'retry_after': retry_after,
            'partial': False
        })
        resp.status_code = 429
        resp.headers['Retry-After'] = str(retry_after)
        return resp
    except CircuitOpenError as e:
        # Circuit breaker is open — tell the client to wait for cooldown
        resp = jsonify({
            'error': 'Translation service is temporarily unavailable. Please try again shortly.',
            'retry_after': 60
        })
        resp.status_code = 503
        resp.headers['Retry-After'] = '60'
        return resp
    except (TransientError, PermanentError) as e:
        # We already retried internally; surface a friendly 502/503
        status = 503 if isinstance(e, TransientError) else 502
        resp = jsonify({
            'error': 'Translation service encountered an error. Please try again.',
            'details': str(e)
        })
        resp.status_code = status
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Supporter Map API ───
@app.route('/api/supporters', methods=['GET'])
def api_supporters_list():
    """GET /api/supporters → list all supporters."""
    try:
        from logic_modules.supporter_map import handle_get
        result = handle_get()
        return jsonify({'supporters': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/supporters', methods=['POST'])
def api_supporters_add():
    """POST /api/supporters → add a new supporter pin."""
    data = request.get_json(silent=True) or {}
    try:
        from logic_modules.supporter_map import handle_add
        result, status = handle_add(data)
        if status >= 400:
            return jsonify(result), status
        return jsonify({'supporter': result}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/supporters/search')
def api_supporters_search():
    """GET /api/supporters/search?q=det → type-ahead city suggestions."""
    q = request.args.get('q', '')
    try:
        from logic_modules.supporter_map import search_cities
        results = search_cities(q)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/supporters/vibes')
def api_supporters_vibes():
    """GET /api/supporters/vibes → list of vibe badge definitions."""
    try:
        from logic_modules.supporter_map import VIBES
        return jsonify({'vibes': VIBES})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/<path:filename>')
def static_files(filename):
    # Serve files from frontend folder
    safe_path = os.path.join(app.static_folder, filename)
    if os.path.isdir(safe_path):
        return redirect('/')
    return send_from_directory(app.static_folder, filename)


@app.route('/api/<module_name>')
def api_module(module_name):
    """Generic API bridge to call the module's run() function.

    Example: /api/hazard_lookup?val=48005
    """
    if module_name not in ALLOWED_MODULES:
        abort(404)

    try:
        # import the module from the local package / path
        mod = importlib.import_module(f'logic_modules.{module_name}')
    except Exception as e:
        return jsonify({'error': f'Cannot import module: {e}'}), 500

    run_fn = getattr(mod, 'run', None)
    if not callable(run_fn):
        return jsonify({'error': 'module has no run() function'}), 400

    # Convert query params to a dict and pass as kwargs where possible
    params = request.args.to_dict()

    try:
        if params:
            result = run_fn(**params)
        else:
            # some modules expect no args
            result = run_fn()
    except TypeError:
        # fallback: try calling with no args if signature doesn't accept kwargs
        try:
            result = run_fn()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Return text responses directly, otherwise JSON-serialize
    if isinstance(result, str):
        return Response(result, mimetype='text/plain')
    else:
        return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=8000)