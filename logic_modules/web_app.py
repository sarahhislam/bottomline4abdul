from flask import Flask, send_from_directory, redirect, request, jsonify, Response, abort
import os
import importlib

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Whitelist of modules we expose via the API to avoid arbitrary imports
ALLOWED_MODULES = {
    'endorsement_engine', 'financial_simulator', 'halal_economy', 'hazard_lookup',
    'myth_buster', 'policy_deep_dive', 'senior_engagement', 'simulation_history',
    'tax_calculator', 'youth_amanah'
}


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


try:
    from translator import translate_batch, LANGUAGES, is_rtl
    _TRANSLATOR_AVAILABLE = True
except ImportError:
    _TRANSLATOR_AVAILABLE = False
    LANGUAGES = {}
    def is_rtl(_code):
        return False
    def translate_batch(texts, _target):
        raise RuntimeError('deep-translator is not installed')


@app.route('/api/languages')
def api_languages():
    """Return the list of supported languages."""
    if not _TRANSLATOR_AVAILABLE:
        return jsonify({'error': 'Translation unavailable (install deep-translator)'}), 503
    return jsonify({
        code: {"name": name, "rtl": is_rtl(code)}
        for code, name in LANGUAGES.items()
    })


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """
    Translate a batch of texts.

    POST JSON body: { "texts": [...], "target": "ar" }
    Response: { "translations": [...] }
    """
    if not _TRANSLATOR_AVAILABLE:
        return jsonify({'error': 'Translation unavailable (install deep-translator)'}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    texts = data.get('texts', [])
    target = data.get('target', 'en')

    if target not in LANGUAGES and target != 'en':
        return jsonify({'error': f'Unsupported language: {target}'}), 400

    if target == 'en':
        return jsonify({'translations': texts})

    try:
        result = translate_batch(texts, target)
        return jsonify({'translations': result})
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
        mod = importlib.import_module(module_name)
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
