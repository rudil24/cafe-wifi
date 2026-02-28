# LOCAL_LOG.md — Cafe & WiFi Finder

Project log maintained by Cap (OPST Team Lead). Updated at every stage gate.

---

## Phase 0: Scope & Design (2026-02-27)

__Status:__ Complete

### Kickoff Actions

- Ran `sync-opst-assets` workflow — symlinks for `.agent/rules`, `.agent/workflows`, `CLAUDE.md` confirmed at workspace root.
- Ran `setup-project-files` workflow on `cafe-wifi/` — `.env.example`, `.gitattributes`, `.gitignore` copied; `git init` complete.
- Ran `project-kickoff` workflow:
  - Inspected `instance/cafes.db` — 21 cafes, London area; schema fields confirmed.
  - Discovery interview conducted with Product Owner.
  - Complexity triage: 12 MVP requirements, 4 UI views → __Path B (Heavy)__.
  - Generated `docs/PRD.md`, `docs/Design.md`, `README.md`.

### Architecture Decisions

- __Access control:__ Hybrid. Public add, admin-only delete. Credentials via env vars (no User table for MVP).
- __Map:__ Leaflet.js + OpenStreetMap tiles. Requires `lat`/`lng` columns on `cafe` table. One-time Nominatim geocode migration needed for all 21 existing records.
- __UI:__ Tailwind CSS (CDN). Server-rendered Jinja2 templates. No JS framework.
- __Auth:__ Flask session (`session['is_admin']`). No Flask-Login. `SECRET_KEY` env var required.
- __Filters:__ URL query params (`?wifi=1&sockets=1&location=Peckham`). Backend filter, not JS-driven.
- __Deploy:__ Render.com Web Service (Gunicorn), existing `rudil24_db` PostgreSQL partition.

### Open Items Carried to Phase 1

- Nominatim geocode script must be written and run before first map render.
- `DATABASE_URL` env var switching pattern must be verified (SQLite dev → Postgres prod).
- Broken image URL fallback: implement CSS `onerror` on `<img>` tags.

---

## Phase 1: Development (2026-02-27)

__Status:__ Complete

### Development Actions

- Stella (Python Developer) built full Flask app: `app.py`, `models.py`, `extensions.py`, `forms.py`.
- Implemented `GET /` with filter logic (wifi, sockets, calls, location) via URL query params.
- Built `GET/POST /add` with WTForms + CSRF, `GET/POST /admin/login`, `GET /admin/logout`, `POST /cafe/<id>/delete`.
- Added Leaflet/OpenStreetMap map to `index.html`; cafes serialized to JSON context for pin rendering.
- Ran `geocode.py` via Nominatim — all 21 cafes geocoded and lat/lng baked into `seed.py`.
- Tailwind CSS responsive grid (mobile-first, single-column small / two-column large).

### Development Decisions

- `create_app()` factory pattern chosen from the start — enables clean test isolation.
- Filters are server-side (GET params → SQLAlchemy query), not JS-driven — fully shareable URLs.
- `seed.py` with hardcoded coordinates avoids Nominatim API calls at deploy time.

### Development Issues

- `instance/cafes.db` was tracked by git before `instance/` was added to `.gitignore` — removed with `git rm --cached`.
- Geocoded SQLite data lost when `db.drop_all()` was committed in test fixture; restored from `cafes_orig.db` and re-geocoded.

---

## Phase 2: QA (2026-02-27)

__Status:__ Complete

### QA Actions

- Vera (QA) wrote `tests/test_app.py` — 35 tests across 6 test classes.
- Fixture: `tempfile.mkstemp()` SQLite + `db.engine.dispose()` in teardown for clean request-level isolation.
- 35/35 passing, 97% coverage. Uncovered: Postgres URL rewrite (prod-only) and `__main__` block.

### QA Issues

- `test_cafe_removed_from_homepage_after_delete` required 3 fix cycles. Root cause: flash message `'"Full House" has been removed.'` caused `b"Full House"` to appear in the response body. Fixed by asserting `b"Full House</h3>"` with `follow_redirects=True`.
- StaticPool was tried first — does not provide request-level isolation. Switched to temp-file SQLite.

---

## Phase 3: Deployment (2026-02-27)

__Status:__ Complete

### Deployment Actions

- Nexus (DevOps) created `render.yaml` Blueprint config.
- `startCommand: python seed.py && gunicorn app:app` — seeds DB on cold start; idempotency guard skips if data exists.
- `DB_SCHEMA=workbrew` env var added; `CREATE SCHEMA IF NOT EXISTS workbrew` runs at cold start via `sqlalchemy.text`.
- `runtime.txt` pins Python 3.12 for psycopg2-binary pre-built wheel.
- Deployed to Render.com free tier at [https://workbrew-m517.onrender.com/](https://workbrew-m517.onrender.com/).
- 21 cafes seeded automatically on first cold start.

### Deployment Decisions

- Used existing `rudil24_db` shared Postgres instance — `DB_SCHEMA=workbrew` isolates tables.
- `sync: false` for secrets (ADMIN_USER, ADMIN_PASS, DATABASE_URL), `generateValue: true` for SECRET_KEY.

---

## Phase 4: Retro (2026-02-27)

__Status:__ Complete

### Retro Actions

- Cap generated `.agents/retros/2026-02-27-workbrew_TEAM_RETRO.md` — all team members contributed perspectives.
- Product Owner (Rudi) reviewed and added comments to all three sections.
- 10 learnings extracted to `.agents/learnings/2026-02-27-workbrew.md`.
- Retro summary written to `.agents/retros/2026-02-27-workbrew.md`.
- GLOBAL_EVOLUTION.md updated: step 4 skill resolution rule added; mockup tooling guidance added.

### Top Learnings

- L1: OPST skills must be read from `_OPST/assets/SKILLS/<skill>/SKILL.md` directly.
- L2: LOCAL_LOG.md must be updated at every phase gate.
- L9: Use Excalidraw/Figma/Claude Artifacts — not ASCII — for UI mockups.
- Full list: `.agents/learnings/2026-02-27-workbrew.md`
