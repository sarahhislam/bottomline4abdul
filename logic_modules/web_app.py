from flask import Flask, send_from_directory, redirect, request, jsonify, Response, abort
import os
import importlib
import re

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


# ─── SMS Reminder Sign-Up ───
# Sends an SMS via Twilio when credentials are configured.
# If Twilio is not configured, it falls back to a functional
# simulated send (logs the message) so the feature always works.
try:
    from twilio.rest import Client as TwilioClient
    _TWILIO_AVAILABLE = True
except ImportError:
    _TWILIO_AVAILABLE = False


def _normalize_phone(raw):
    """Return E.164 phone number or None if invalid."""
    digits = re.sub(r'\D', '', raw or '')
    if len(digits) == 10:
        return '+1' + digits
    if len(digits) == 11 and digits.startswith('1'):
        return '+' + digits
    return None


@app.route('/api/sms/send', methods=['POST'])
def api_sms_send():
    """
    Send an SMS reminder sign-up confirmation.

    POST JSON body: { "phone": "...", "zip": "..." }
    Response: { "status": "sent" | "simulated", "message": "..." }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    phone = _normalize_phone(data.get('phone', ''))
    if not phone:
        return jsonify({'error': 'Please enter a valid 10-digit phone number.'}), 400

    zip_code = re.sub(r'\D', '', data.get('zip', '') or '')[:5]

    message_body = (
        "Abdul for Senate: You're signed up for election deadline SMS reminders! "
        "We'll text you before each important Michigan voting deadline. "
        "Reply STOP to opt out anytime."
    )

    # Try real Twilio send if configured
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_FROM_NUMBER')

    if _TWILIO_AVAILABLE and account_sid and auth_token and from_number:
        try:
            client = TwilioClient(account_sid, auth_token)
            client.messages.create(
                to=phone,
                from_=from_number,
                body=message_body
            )
            return jsonify({'status': 'sent', 'message': 'SMS sent successfully.'})
        except Exception as e:
            return jsonify({'error': f'SMS send failed: {e}'}), 500

    # Fallback: simulated send (logs to console) so the feature is functional
    print(f"[SMS-SIMULATED] To: {phone} | Zip: {zip_code} | Body: {message_body}")
    return jsonify({
        'status': 'simulated',
        'message': "SMS queued (simulated). Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER to send real texts."
    })


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
