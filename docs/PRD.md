# Product Requirements Document: Cafe & WiFi Finder

| Metadata | Details |
| :--- | :--- |
| __Status__ | `Draft` |
| __Owner__ | @rudil24 |
| __Team__ | OPST (Cap, Stella, Nexus, Schema, Sentinel, Vera) |
| __Target Date__ | 2026-03-14 |
| __Last Updated__ | 2026-02-27 |
| __Repo__ | `cafe-wifi/` |

---

## 1. Context & Problem Statement

- __The "Why":__ Remote workers in London lack a reliable, filterable resource to find cafes that offer the specific combination of WiFi, power sockets, and a call-friendly environment.
- __Current State:__ Users cross-reference Google Maps, Instagram, and word-of-mouth, with no guarantee of amenity accuracy. Wasted commutes to socketless cafes are a common frustration.
- __Desired State:__ A beautiful, community-maintained web app where remote workers can browse, filter, and contribute cafe listings — verified for the amenities that actually matter.

---

## 2. User Personas

### Persona 1: Alex — The Remote Worker

- __Age:__ 28–38
- __Role:__ Software engineer / freelance consultant working 4–6 hours at a cafe
- __Goal:__ Find a cafe with reliable WiFi, power sockets, and a quiet enough environment to take client calls
- __Pain Point:__ Generic review platforms don't surface amenity-level detail; wasted trips to unsuitable locations
- __Key Behavior:__ Filters by `has_wifi + has_sockets` before leaving home; checks price range and seat count

### Persona 2: Jordan — The Explorer / Contributor

- __Age:__ 22–32
- __Role:__ Digital nomad or remote-first employee constantly discovering new spots
- __Goal:__ Share great cafe discoveries with the community; help build the map over time
- __Pain Point:__ No frictionless way to contribute to existing databases; Google reviews are scattered and generic
- __Key Behavior:__ Adds new cafes immediately after discovering them; expects a fast, simple submission form

---

## 3. User Stories & Acceptance Criteria

### Story 1: Browse Cafes (Map + Cards)

- __User Story:__ As a remote worker, I want to see all cafes on an interactive map and in a scrollable card grid so that I can quickly survey my options visually.
- __Acceptance Criteria:__
  - `GIVEN` I navigate to the homepage
  - `WHEN` the page loads
  - `THEN` I see a Leaflet/OpenStreetMap map with a pin for each cafe AND a scrollable card grid below
  - `AND` each card shows: cafe photo, name, location tag, amenity icons (WiFi, Sockets, Calls), seat count, and coffee price
- __Priority:__ P0

### Story 2: Filter by Amenity and Location

- __User Story:__ As a remote worker, I want to filter cafes by WiFi, sockets, call-friendliness, and neighborhood so that I only see cafes that fit my needs.
- __Acceptance Criteria:__
  - `GIVEN` I am on the homepage
  - `WHEN` I toggle one or more filter chips (e.g., "WiFi", "Sockets", "Calls") or select a location from the dropdown
  - `THEN` the card grid and map pins update to show only matching cafes
  - `AND` the URL query string reflects the active filters (enabling shareable links)
- __Priority:__ P0

### Story 3: Add a New Cafe

- __User Story:__ As a contributor, I want to submit a new cafe with its amenity details so that other remote workers can find it.
- __Acceptance Criteria:__
  - `GIVEN` I navigate to `/add`
  - `WHEN` I fill out and submit the form with valid data
  - `THEN` the new cafe is saved and I am redirected to the homepage with a success flash message
  - `AND` the new cafe appears on the map and card grid immediately
  - `WHEN` I submit invalid or missing required data
  - `THEN` field-level validation errors display inline; no database write occurs
- __Priority:__ P0

### Story 4: Admin Login

- __User Story:__ As an admin, I want to log in securely so that I can access cafe management functions.
- __Acceptance Criteria:__
  - `GIVEN` I navigate to `/admin/login`
  - `WHEN` I submit valid credentials
  - `THEN` I am redirected to the homepage in admin mode (delete buttons visible on all cafe cards)
  - `WHEN` I submit invalid credentials
  - `THEN` an error flash message appears and I remain on the login page
- __Priority:__ P0

### Story 5: Admin Delete a Cafe

- __User Story:__ As an admin, I want to delete inaccurate or duplicate cafe entries so that the database remains accurate.
- __Acceptance Criteria:__
  - `GIVEN` I am logged in as admin on the homepage
  - `WHEN` I click the Delete button on a cafe card
  - `THEN` the cafe is removed from the database, disappears from the card grid and map, and a success flash message is shown
- __Priority:__ P0

### Story 6: Mobile-Responsive Experience

- __User Story:__ As a user on a mobile device, I want the site to work smoothly on my phone so I can check cafes on the go.
- __Acceptance Criteria:__
  - `GIVEN` I access the site on a screen width ≤ 640px
  - `WHEN` I view the homepage
  - `THEN` the card grid collapses to single-column, the map scales to full width, and filter chips scroll horizontally without overflow
- __Priority:__ P0

---

## 4. Technical Specifications (AI Context)

### 4.1 Data Model

Minimal schema change required: add `lat` and `lng` columns to support Leaflet map pins.

```sql
-- Existing table (no changes to existing columns)
CREATE TABLE cafe (
  id             INTEGER PRIMARY KEY,
  name           VARCHAR(250) NOT NULL UNIQUE,
  map_url        VARCHAR(500) NOT NULL,
  img_url        VARCHAR(500) NOT NULL,
  location       VARCHAR(250) NOT NULL,
  has_sockets    BOOLEAN NOT NULL,
  has_toilet     BOOLEAN NOT NULL,
  has_wifi       BOOLEAN NOT NULL,
  can_take_calls BOOLEAN NOT NULL,
  seats          VARCHAR(250),
  coffee_price   VARCHAR(250),
  lat            FLOAT,   -- NEW: for Leaflet map pin
  lng            FLOAT    -- NEW: for Leaflet map pin
);
```

A one-time Nominatim geocoding script will populate `lat`/`lng` for existing records.
SQLite for local dev. PostgreSQL via `DATABASE_URL` env var on Render.com.

### 4.2 Route Logic

| Method | Route | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | Browse cafes with optional filter params (`?wifi=1&sockets=1&location=Peckham`) |
| `GET` | `/add` | Public | Render add cafe form |
| `POST` | `/add` | Public | Validate form, insert `Cafe` record, redirect to `/` with flash |
| `GET` | `/admin/login` | Public | Render admin login form |
| `POST` | `/admin/login` | Public | Validate env var credentials, set `session['is_admin']`, redirect to `/` |
| `GET` | `/admin/logout` | Admin | Clear session, redirect to `/` |
| `POST` | `/cafe/<int:id>/delete` | Admin | Delete `Cafe` record, redirect to `/` with flash |

### 4.3 Dependencies & Constraints

- __Backend:__ Python 3.11+, Flask, Flask-SQLAlchemy, Flask-WTF, python-dotenv, requests (geocoding)
- __Frontend:__ Tailwind CSS (CDN), Leaflet.js (CDN), vanilla JS (filter chips, map sync)
- __Database:__ SQLite (dev) → PostgreSQL on `rudil24_db` partition (prod)
- __Auth:__ Session-based (Flask `session` + `SECRET_KEY`). Admin credentials in env vars (`ADMIN_USER`, `ADMIN_PASS`). No Flask-Login needed.
- __Deployment:__ Render.com Web Service, Gunicorn WSGI, existing `rudil24_db` PostgreSQL

---

## 5. UI/UX Design

See `docs/Design.md` for wireframes and component breakdown.

- __Empty State:__ "No cafes match your filters." with a "Clear Filters" button.
- __Loading State:__ Native browser loading (server-rendered Jinja2; no async skeleton needed for MVP).
- __Error State:__ Flask flash messages rendered as dismissible Tailwind alert banners.
- __Broken Image Fallback:__ CSS `onerror` handler swaps broken `img_url` to a gray placeholder.

---

## 6. Open Questions / Risks

- [x] __Admin credentials:__ Stored as `ADMIN_USER` / `ADMIN_PASS` environment variables. Acceptable for a portfolio MVP.
- [x] __Image hosting:__ Cafes use external `img_url`. No upload infrastructure required.
- [x] __Map coordinates:__ Existing `map_url` values are Google Business links. Resolved by adding `lat`/`lng` columns and running a one-time Nominatim geocode script.
- [ ] __Spam on public add form:__ WTForms CSRF token active by default. Honeypot field is a stretch goal.
- [ ] __Broken image URLs:__ External images may 404 over time. CSS `onerror` fallback mitigates user-visible impact.
- [ ] __Geocoding rate limits:__ Nominatim requires a max of 1 req/sec. One-time script for 21 records is fine; new submissions should geocode on the backend at add time.

---

## 7. Rollout Plan

- [x] __Phase 0:__ Project setup — config files, git init, `docs/` *(complete)*
- [x] __Phase 1:__ Local dev — Flask app, SQLAlchemy models, geocode migration, all routes, Tailwind UI, Leaflet map
- [x] __Phase 2:__ QA — Vera runs tests, validates forms, checks mobile responsiveness and admin flows
- [x] __Phase 3:__ Deploy to Render.com — PostgreSQL migration, Gunicorn config, environment variables
- [x] __Phase 4:__ Portfolio review & retro
