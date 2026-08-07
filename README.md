# Bottomline for Abdul — Policy Tools

Interactive policy calculators and research tools for the Abdul for Senate campaign. Companion to [Cliposition](https://tools4abdul.com/cliposition/): Cliposition shows positions via video + sources; this site lets constituents run the numbers.

## Live site (GitHub Pages)

Preferred setup: **Settings → Pages → Source: GitHub Actions**. The workflow deploys `logic_modules/frontend/` on every push to `main`.

Live URL:

`https://sarahhislam.github.io/bottomline4abdul/`

If Pages is still set to “Deploy from a branch” (`main` / `/`), a root `index.html` redirects into `logic_modules/frontend/` so the site URL does not 404.

The live site is behind a **beta passcode gate** (client-side; keeps casual visitors out, not real auth). Unlock lasts for the browser tab session.

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
| Polling / Ballot / Deadlines / Voter ID | Voter navigation helpers |
| Candidate Comparison / Mail Ballot | Additional voter tools |

## Architecture

- **Static frontend** (`logic_modules/frontend/`) — HTML/CSS + `js/modules.js` (ported logic) + `js/main.js` (UI wiring). This is what GitHub Pages serves.
- **Optional Flask API** (`web_app.py`) — same Python modules via `/api/<module>` for local experimentation.
