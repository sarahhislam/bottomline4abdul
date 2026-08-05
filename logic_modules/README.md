# Frontend demo for logic modules

This folder contains a static frontend scaffold that mirrors the aesthetic of https://abdulforsenate.com/ and links to each of your logic modules as placeholder pages.

How to run (macOS / zsh):

1. Create a virtualenv and install requirements

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the dev server

```bash
python web_app.py
```

Open http://127.0.0.1:8000 in your browser.

Next steps:
- Wire interactive frontend controls to the Python modules (e.g., create API endpoints in `web_app.py` that call functions from the `.py` modules).
- Add assets (fonts, images) and further polish to match the original site exactly.
