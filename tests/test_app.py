"""
Vera (QA) — WorkBrew test suite.

Coverage areas:
  - Route availability (GET 200 / redirect)
  - Filter logic (wifi, sockets, calls, location, combinations)
  - Add-cafe form (valid submission, missing fields, bad URLs)
  - Admin auth (correct creds, wrong creds, session persistence)
  - Admin delete (authenticated, unauthenticated → 403)
  - CSRF protection (POST without token → 400)
  - Empty-state rendering (no cafes match filters)
"""
import os
import tempfile

import pytest

from app import create_app
from extensions import db
from models import Cafe

# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def app():
    # Temp-file SQLite: file-based DB means all connections (outer test context,
    # request contexts) see committed state independently — no shared-connection
    # transaction ambiguity that plagues in-memory SQLite in multi-context tests.
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,           # disable CSRF in tests; tested separately
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SECRET_KEY": "test-secret",
    })
    with test_app.app_context():
        db.create_all()
        _seed()
        yield test_app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()      # release pool connections → suppress ResourceWarning
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client):
    """Client with an active admin session."""
    with client.session_transaction() as sess:
        sess["is_admin"] = True
    return client


def _seed():
    """Insert a small set of known cafes for predictable filter tests."""
    cafes = [
        Cafe(name="WiFi Only",     map_url="http://g.co/1", img_url="http://img/1.jpg",
             location="Peckham",    has_wifi=True,  has_sockets=False,
             has_toilet=False, can_take_calls=False, seats="10", coffee_price="£2.00",
             lat=51.47, lng=-0.07),
        Cafe(name="Sockets Only",  map_url="http://g.co/2", img_url="http://img/2.jpg",
             location="Hackney",    has_wifi=False, has_sockets=True,
             has_toilet=True,  can_take_calls=False, seats="20", coffee_price="£2.50",
             lat=51.54, lng=-0.06),
        Cafe(name="Full House",    map_url="http://g.co/3", img_url="http://img/3.jpg",
             location="Shoreditch", has_wifi=True,  has_sockets=True,
             has_toilet=True,  can_take_calls=True,  seats="50+", coffee_price="£3.00",
             lat=51.52, lng=-0.08),
        Cafe(name="No Amenities",  map_url="http://g.co/4", img_url="http://img/4.jpg",
             location="Peckham",    has_wifi=False, has_sockets=False,
             has_toilet=False, can_take_calls=False, seats="5",  coffee_price="£1.50",
             lat=51.47, lng=-0.07),
    ]
    db.session.add_all(cafes)
    db.session.commit()


# ── Helper ────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ROUTE AVAILABILITY
# ═══════════════════════════════════════════════════════════════════════════════


class TestRoutes:
    def test_homepage_ok(self, client):
        assert client.get("/").status_code == 200

    def test_add_cafe_get_ok(self, client):
        assert client.get("/add").status_code == 200

    def test_admin_login_get_ok(self, client):
        assert client.get("/admin/login").status_code == 200

    def test_admin_logout_redirects(self, client):
        resp = client.get("/admin/logout", follow_redirects=False)
        assert resp.status_code == 302

    def test_homepage_lists_all_cafes(self, client):
        resp = client.get("/")
        # All 4 seeded cafes should appear
        assert b"WiFi Only" in resp.data
        assert b"Full House" in resp.data
        assert b"No Amenities" in resp.data

    def test_admin_login_redirects_if_already_admin(self, admin_client):
        resp = admin_client.get("/admin/login", follow_redirects=False)
        assert resp.status_code == 302
        assert "/" in resp.headers["Location"]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. FILTER LOGIC
# ═══════════════════════════════════════════════════════════════════════════════


class TestFilters:
    def test_filter_wifi(self, client):
        resp = client.get("/?wifi=1")
        assert b"WiFi Only" in resp.data
        assert b"Full House" in resp.data
        assert b"Sockets Only" not in resp.data
        assert b"No Amenities" not in resp.data

    def test_filter_sockets(self, client):
        resp = client.get("/?sockets=1")
        assert b"Sockets Only" in resp.data
        assert b"Full House" in resp.data
        assert b"WiFi Only" not in resp.data

    def test_filter_calls(self, client):
        resp = client.get("/?calls=1")
        assert b"Full House" in resp.data
        assert b"WiFi Only" not in resp.data
        assert b"Sockets Only" not in resp.data

    def test_filter_location(self, client):
        resp = client.get("/?location=Peckham")
        assert b"WiFi Only" in resp.data
        assert b"No Amenities" in resp.data
        assert b"Sockets Only" not in resp.data  # Hackney
        assert b"Full House" not in resp.data    # Shoreditch

    def test_filter_combined_wifi_and_sockets(self, client):
        resp = client.get("/?wifi=1&sockets=1")
        assert b"Full House" in resp.data
        assert b"WiFi Only" not in resp.data
        assert b"Sockets Only" not in resp.data

    def test_filter_no_match_shows_empty_state(self, client):
        resp = client.get("/?wifi=1&location=Hackney")
        # Hackney only has "Sockets Only" (no wifi) → no results
        assert b"No cafes match" in resp.data

    def test_filter_clear_all_returns_all(self, client):
        resp = client.get("/")
        assert b"WiFi Only" in resp.data
        assert b"No Amenities" in resp.data


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ADD CAFE FORM
# ═══════════════════════════════════════════════════════════════════════════════


class TestAddCafe:
    VALID = {
        "name":        "Test Cafe",
        "location":    "Brixton",
        "map_url":     "http://maps.google.com/test",
        "img_url":     "http://example.com/photo.jpg",
        "seats":       "15",
        "coffee_price": "£2.50",
        "has_wifi":    "y",
        "has_sockets": "y",
    }

    def test_valid_submission_redirects(self, client):
        resp = client.post("/add", data=self.VALID, follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/"

    def test_valid_submission_persisted(self, client, app):
        client.post("/add", data=self.VALID)
        # Expire outer session cache so the query hits the DB (where the
        # request's commit is now visible).
        db.session.expire_all()
        cafe = Cafe.query.filter_by(name="Test Cafe").first()
        assert cafe is not None
        assert cafe.location == "Brixton"
        assert cafe.has_wifi is True
        assert cafe.has_sockets is True

    def test_valid_submission_flash_success(self, client):
        resp = client.post("/add", data=self.VALID, follow_redirects=True)
        assert b"added" in resp.data.lower() or b"live" in resp.data.lower()

    def test_missing_name_rejected(self, client, app):
        data = {**self.VALID, "name": ""}
        resp = client.post("/add", data=data)
        assert resp.status_code == 200          # re-renders form
        assert Cafe.query.filter_by(location="Brixton").count() == 0

    def test_missing_location_rejected(self, client):
        data = {**self.VALID, "location": ""}
        resp = client.post("/add", data=data)
        assert resp.status_code == 200

    def test_invalid_map_url_rejected(self, client):
        data = {**self.VALID, "map_url": "not-a-url"}
        resp = client.post("/add", data=data)
        assert resp.status_code == 200

    def test_invalid_img_url_rejected(self, client):
        data = {**self.VALID, "img_url": "not-a-url"}
        resp = client.post("/add", data=data)
        assert resp.status_code == 200

    def test_boolean_fields_default_false(self, client, app):
        data = {k: v for k, v in self.VALID.items()
                if k not in ("has_wifi", "has_sockets", "has_toilet", "can_take_calls")}
        data["name"] = "Minimal Cafe"
        client.post("/add", data=data)
        db.session.expire_all()
        cafe = Cafe.query.filter_by(name="Minimal Cafe").first()
        assert cafe is not None
        assert cafe.has_wifi is False
        assert cafe.has_sockets is False


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ADMIN AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdminAuth:
    def test_correct_credentials_redirect(self, client, monkeypatch):
        monkeypatch.setenv("ADMIN_USER", "admin")
        monkeypatch.setenv("ADMIN_PASS", "secret")
        resp = client.post("/admin/login",
                           data={"username": "admin", "password": "secret"},
                           follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/"

    def test_correct_credentials_sets_session(self, client, monkeypatch):
        monkeypatch.setenv("ADMIN_USER", "admin")
        monkeypatch.setenv("ADMIN_PASS", "secret")
        client.post("/admin/login",
                    data={"username": "admin", "password": "secret"})
        with client.session_transaction() as sess:
            assert sess.get("is_admin") is True

    def test_wrong_password_rejected(self, client, monkeypatch):
        monkeypatch.setenv("ADMIN_USER", "admin")
        monkeypatch.setenv("ADMIN_PASS", "secret")
        resp = client.post("/admin/login",
                           data={"username": "admin", "password": "wrong"},
                           follow_redirects=True)
        assert b"Invalid" in resp.data
        with client.session_transaction() as sess:
            assert not sess.get("is_admin")

    def test_wrong_username_rejected(self, client, monkeypatch):
        monkeypatch.setenv("ADMIN_USER", "admin")
        monkeypatch.setenv("ADMIN_PASS", "secret")
        resp = client.post("/admin/login",
                           data={"username": "hacker", "password": "secret"},
                           follow_redirects=True)
        assert b"Invalid" in resp.data

    def test_logout_clears_session(self, admin_client):
        admin_client.get("/admin/logout")
        with admin_client.session_transaction() as sess:
            assert not sess.get("is_admin")

    def test_delete_buttons_visible_to_admin(self, admin_client):
        resp = admin_client.get("/")
        assert b"Delete Listing" in resp.data

    def test_delete_buttons_hidden_from_public(self, client):
        resp = client.get("/")
        assert b"Delete Listing" not in resp.data


# ═══════════════════════════════════════════════════════════════════════════════
# 5. DELETE ROUTE
# ═══════════════════════════════════════════════════════════════════════════════


class TestDelete:
    def _get_cafe_id(self, name="WiFi Only"):
        # We're already inside the fixture's app context; no nested push needed.
        return Cafe.query.filter_by(name=name).first().id

    def test_admin_can_delete(self, admin_client):
        cafe_id = self._get_cafe_id()
        resp = admin_client.post(f"/cafe/{cafe_id}/delete", follow_redirects=False)
        assert resp.status_code == 302
        assert db.session.get(Cafe, cafe_id) is None

    def test_public_delete_returns_403(self, client):
        cafe_id = self._get_cafe_id()
        resp = client.post(f"/cafe/{cafe_id}/delete")
        assert resp.status_code == 403

    def test_delete_nonexistent_cafe_returns_404(self, admin_client):
        resp = admin_client.post("/cafe/99999/delete")
        assert resp.status_code == 404

    def test_cafe_removed_from_homepage_after_delete(self, admin_client):
        cafe_id = self._get_cafe_id("Full House")
        # follow_redirects=True → response IS the post-delete homepage
        resp = admin_client.post(f"/cafe/{cafe_id}/delete", follow_redirects=True)
        assert resp.status_code == 200
        assert b"has been removed" in resp.data      # success flash shown
        # The cafe *card* title is rendered as: >Full House</h3>
        # The flash message contains "Full House" but not this pattern
        assert b"Full House</h3>" not in resp.data


# ═══════════════════════════════════════════════════════════════════════════════
# 6. CSRF PROTECTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestCSRF:
    """Re-enables CSRF protection to verify the middleware is active."""

    @pytest.fixture
    def csrf_client(self, app):
        app.config["WTF_CSRF_ENABLED"] = True
        return app.test_client()

    def test_post_add_without_csrf_returns_400(self, csrf_client):
        resp = csrf_client.post("/add", data={
            "name": "No CSRF Cafe",
            "location": "Soho",
            "map_url": "http://maps.google.com/x",
            "img_url": "http://example.com/x.jpg",
        })
        assert resp.status_code == 400

    def test_post_login_without_csrf_returns_400(self, csrf_client):
        resp = csrf_client.post("/admin/login",
                                data={"username": "admin", "password": "secret"})
        assert resp.status_code == 400

    def test_delete_without_csrf_returns_400(self, csrf_client):
        # Set admin session first
        with csrf_client.session_transaction() as sess:
            sess["is_admin"] = True
        resp = csrf_client.post("/cafe/1/delete")
        assert resp.status_code == 400
