# LOCAL_LOG.md — Cafe & WiFi Finder

Project log maintained by Cap (OPST Team Lead). Updated at every stage gate.

---

## Phase 0: Scope & Design (2026-02-27)

__Status:__ Complete

### Actions Taken

- Ran `sync-opst-assets` workflow — symlinks for `.agent/rules`, `.agent/workflows`, `CLAUDE.md` confirmed at workspace root.
- Ran `setup-project-files` workflow on `cafe-wifi/` — `.env.example`, `.gitattributes`, `.gitignore` copied; `git init` complete.
- Ran `project-kickoff` workflow:
  - Inspected `instance/cafes.db` — 21 cafes, London area; schema fields confirmed.
  - Discovery interview conducted with Product Owner.
  - Complexity triage: 12 MVP requirements, 4 UI views → __Path B (Heavy)__.
  - Generated `docs/PRD.md`, `docs/Design.md`, `README.md`.

### Key Decisions

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

## Phase 1: Development — (pending)

---

## Phase 2: QA — (pending)

---

## Phase 3: Deployment — (pending)

---

## Phase 4: Retro — (pending)
