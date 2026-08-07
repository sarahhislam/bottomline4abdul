# Bottomline for Abdul — Policy Tools

Interactive policy calculators and research tools for the Abdul for Senate campaign. Companion to [Cliposition](https://tools4abdul.com/cliposition/): Cliposition shows positions via video + sources; this site lets constituents run the numbers.

## Live site (GitHub Pages)

After enabling Pages (Settings → Pages → Source: **GitHub Actions**), the site deploys from `logic_modules/frontend/` on every push to `main`:

`https://tools4abdul.github.io/bottomline4abdul/`

## Local development

```bash
cd logic_modules
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python web_app.py
```

Open http://127.0.0.1:8000

You can also open `logic_modules/frontend/index.html` via any static file server (no Python required) — the tools run entirely in the browser.

## Tools

| Tool | What it does |
|------|----------------|
| Endorsement Engine | Topic → tailored policy response |
| Financial Simulator / Tax Calculator | Corporate vs Abdul pocketbook models |
| Hazard Lookup | Michigan ZIP → environmental hazard report |
| Myth Buster / Policy Deep Dive | Campaign Q&A and policy briefs |
| Halal Economy | Interest-free financing + partner directory |
| Senior Engagement / Youth Amanah | Audience-specific commitments |
| Simulation History | Vault easter egg (`ABDU-2026`) |

## Architecture

- **Static frontend** (`logic_modules/frontend/`) — HTML/CSS + `js/modules.js` (ported logic) + `js/main.js` (UI wiring). This is what GitHub Pages serves.
- **Optional Flask API** (`web_app.py`) — same Python modules via `/api/<module>` for local experimentation.
