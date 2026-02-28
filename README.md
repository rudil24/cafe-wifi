# Cafe & WiFi Finder — @rudil24

A community-maintained, filterable web app for remote workers to discover London cafes with the amenities that actually matter: WiFi, power sockets, and call-friendly environments.

## Estimated Cost

| Category | Description | Cost |
| --- | --- | --- |
| Development Labor | ~20 hrs @ $100/hr (OPST Agentic Team) | $2,000 |
| AI Tokens | Claude Pro subscription | ~$5.00 |
| Production Hosting | Render.com Web Service (free tier) + PostgreSQL | $0.00 |
| Other | n/a | $0.00 |
| __TOTAL__ | | __$2,005__ |

## Mockup

See [docs/Design.md](./docs/Design.md) for full wireframes.

## To Run

### On The Web

__[https://workbrew-m517.onrender.com/](https://workbrew-m517.onrender.com/)__

### In Your Local Environment

1. `git clone` this repo to a local project folder
2. `pip install -r requirements.txt`
3. Consult `.env.example` for required environment variables; create your own `.env` file
4. `python geocode.py` — populates lat/lng for existing cafes (run once)
5. `flask run` or `python app.py`
6. Built in __Python 3.11__ — should work on any 3.8+

## Product Roadmap

See [docs/PRD.md](./docs/PRD.md) for full user stories and acceptance criteria.

### MVP (Must Do)

- [x] Browse all cafes — interactive Leaflet/OpenStreetMap map + responsive card grid
- [x] Filter cafes by WiFi, sockets, call-friendliness, and neighborhood
- [x] Add a new cafe via public submission form (WTForms + CSRF)
- [x] Admin login (env var credentials, session-based)
- [x] Admin delete cafe (protected POST route)
- [x] Tailwind CSS responsive design (mobile-first, single-column on small screens)
- [x] PostgreSQL-compatible SQLAlchemy models (SQLite dev → Postgres prod)
- [x] Deploy to Render.com with Gunicorn

### Stretch Goals (Should Do)

- [ ] Honeypot field on add form to reduce spam submissions
- [ ] Broken image URL fallback placeholder
- [ ] Shareable filter links (URL query params reflect active filters)
- [ ] Animate map → card cross-highlight on pin click

### Super-Stretch Goals (Could Do)

- [ ] Search cafes by name
- [ ] Thumbs-up / thumbs-down community rating per cafe
- [ ] Multiple city support beyond London

### Out of Scope (Won't Do)

- User accounts or registration for regular visitors
- Cafe owner login or claimed listings
- Reservation or booking features
- Payment or monetization

## Design

See [docs/Design.md](./docs/Design.md) for architecture diagram, data model, route map, wireframes, and deployment plan.

### Program Logic Flow

```mermaid
flowchart TD
    A[User visits /] --> B{Filters applied?}
    B -->|No| C[Query all cafes]
    B -->|Yes| D[Query with filter params]
    C --> E[Render index.html — Map + Cards]
    D --> E

    F[User visits /add] --> G[Render add_cafe.html]
    G --> H{Form valid?}
    H -->|No| G
    H -->|Yes| I[Insert Cafe to DB]
    I --> J[Geocode name+location via Nominatim]
    J --> K[Redirect to / with success flash]

    L[User visits /admin/login] --> M[Render admin_login.html]
    M --> N{Credentials match env vars?}
    N -->|No| M
    N -->|Yes| O[Set session is_admin=True]
    O --> P[Redirect to / — delete buttons visible]

    Q[Admin clicks Delete] --> R[POST /cafe/id/delete]
    R --> S{is_admin in session?}
    S -->|No| T[403 Forbidden]
    S -->|Yes| U[Delete Cafe from DB]
    U --> V[Redirect to / with success flash]
```

## Development Workflow

- [x] 1. Initialize Flask app, SQLAlchemy config, `.env` wiring
- [x] 2. Define `Cafe` model in `models.py` with `lat`/`lng` columns
- [x] 3. Run `geocode.py` to populate lat/lng for existing 21 cafes
- [x] 4. Build `GET /` route with filter logic and `index.html` template (cards only first)
- [x] 5. Add Leaflet map to `index.html` with cafe pins from JSON context
- [x] 6. Wire up filter chip bar (GET params → backend filter → template re-render)
- [x] 7. Build `GET/POST /add` route and `add_cafe.html` with WTForms
- [x] 8. Build `GET/POST /admin/login` and `GET /admin/logout` routes
- [x] 9. Wire up `POST /cafe/<id>/delete` with admin session guard
- [x] 10. Sentinel review — CSRF, input validation, session security
- [x] 11. Stella polish — Tailwind responsive grid, amenity icons, flash banners, mobile layout
- [x] 12. Vera QA — 35/35 tests passing, 97% coverage
- [x] 13. Switch to PostgreSQL on Render (`DATABASE_URL` + `DB_SCHEMA=workbrew`)
- [x] 14. Deploy to Render.com — web service + env vars + DB seed
- [x] 15. END-TO-END TEST on live Render URL
- [x] 16. FULL DEPLOYMENT — portfolio ready

## Reflection

| DATE | COMMENTS |
| --- | --- |
| 2026-02-27 | Great deployment led by Claude Code and great design by Stella. It was fast to have the team fully build a prototype in tailwind css than mess with mocks. That's probably why Figma's stock is in the tank. 😟 But seriously it will be interesting to gauge trade-offs in tokens by mocking vs building. |
| 2026-02-27 | Project kickoff complete. PRD, Design, README generated. Git initialized. Ready for Phase 1 development. |
| 2026-02-27 | Full build complete. Flask app, Leaflet map, admin auth, CSRF, 35-test QA suite (97% coverage). Deployed to Render.com at [https://workbrew-m517.onrender.com/](https://workbrew-m517.onrender.com/) using shared rudil24_db Postgres instance with workbrew schema isolation. |

## References

- [Laptop Friendly London](https://laptopfriendly.co/london) — UX inspiration
- [Leaflet.js](https://leafletjs.com/) — open-source interactive maps
- [Nominatim](https://nominatim.openstreetmap.org/) — free geocoding API
- [Tailwind CSS](https://tailwindcss.com/) — utility-first CSS framework
- [Flask-WTF](https://flask-wtf.readthedocs.io/) — WTForms Flask integration
- [Render.com Docs](https://render.com/docs) — deployment reference
