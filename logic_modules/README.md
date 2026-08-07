# Frontend demo for logic modules

Static UI (Abdul for Senate aesthetic) that runs the policy tools in-browser.

## Run locally

**Option A — static (same as GitHub Pages):**

```bash
cd frontend
python3 -m http.server 8000
```

**Option B — Flask (optional Python API):**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python web_app.py
```

Open http://127.0.0.1:8000

Buttons use `data-module-run` → `js/modules.js` (client-side ports of the Python `run()` functions). Flask `/api/<module>` remains available for Option B.
