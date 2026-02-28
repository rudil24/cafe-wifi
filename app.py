"""WorkBrew — Flask application entry point and route definitions."""
import os

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import text

from extensions import csrf, db
from forms import AdminLoginForm, CafeForm
from models import Cafe

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Core config ──────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")

    db_url = os.getenv("DATABASE_URL", "").strip() or "sqlite:///cafes.db"
    # Render.com supplies postgres:// — SQLAlchemy 2 requires postgresql+psycopg2://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Schema isolation (Postgres only) ─────────────────────────────────────
    # DB_SCHEMA scopes all tables to a named schema (e.g. "workbrew") so this
    # app's data stays isolated from other apps sharing the same Postgres
    # instance. Unset locally — SQLite doesn't use schemas.
    db_schema = os.getenv("DB_SCHEMA", "").strip()
    if db_schema and not db_url.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"options": f"-csearch_path={db_schema},public"},
        }

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)
    csrf.init_app(app)

    # ── Routes ───────────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        wifi     = request.args.get("wifi")
        sockets  = request.args.get("sockets")
        calls    = request.args.get("calls")
        location = request.args.get("location")

        query = Cafe.query
        if wifi:     query = query.filter_by(has_wifi=True)
        if sockets:  query = query.filter_by(has_sockets=True)
        if calls:    query = query.filter_by(can_take_calls=True)
        if location: query = query.filter_by(location=location)

        cafes     = query.order_by(Cafe.name).all()
        locations = [r[0] for r in db.session.query(Cafe.location).distinct().order_by(Cafe.location)]
        cafes_data = [c.to_dict() for c in cafes]

        return render_template(
            "index.html",
            cafes=cafes,
            cafes_data=cafes_data,
            locations=locations,
            is_admin=session.get("is_admin", False),
            active_wifi=wifi,
            active_sockets=sockets,
            active_calls=calls,
            active_location=location,
        )

    @app.route("/add", methods=["GET", "POST"])
    def add_cafe():
        form = CafeForm()
        if form.validate_on_submit():
            cafe = Cafe(
                name=form.name.data,
                map_url=form.map_url.data,
                img_url=form.img_url.data,
                location=form.location.data,
                has_sockets=form.has_sockets.data,
                has_toilet=form.has_toilet.data,
                has_wifi=form.has_wifi.data,
                can_take_calls=form.can_take_calls.data,
                seats=form.seats.data,
                coffee_price=form.coffee_price.data,
            )
            db.session.add(cafe)
            db.session.commit()
            flash("Cafe added! ☕ It's now live on the map.", "success")
            return redirect(url_for("index"))
        return render_template("add_cafe.html", form=form)

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if session.get("is_admin"):
            return redirect(url_for("index"))
        form = AdminLoginForm()
        if form.validate_on_submit():
            if (
                form.username.data == os.getenv("ADMIN_USER")
                and form.password.data == os.getenv("ADMIN_PASS")
            ):
                session["is_admin"] = True
                flash("Welcome back, Admin. ☕", "success")
                return redirect(url_for("index"))
            flash("Invalid username or password.", "danger")
        return render_template("admin_login.html", form=form)

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("is_admin", None)
        flash("Logged out successfully.", "info")
        return redirect(url_for("index"))

    @app.route("/cafe/<int:cafe_id>/delete", methods=["POST"])
    def delete_cafe(cafe_id: int):
        if not session.get("is_admin"):
            abort(403)
        cafe = db.get_or_404(Cafe, cafe_id)
        db.session.delete(cafe)
        db.session.commit()
        flash(f'"{cafe.name}" has been removed.', "success")
        return redirect(url_for("index"))

    return app


app = create_app()

# Bootstrap schema + tables on every cold start (both steps are idempotent).
with app.app_context():
    db_schema = os.getenv("DB_SCHEMA", "").strip()
    if db_schema:
        # Ensure the schema exists before create_all() tries to place tables in it.
        with db.engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {db_schema}"))
            conn.commit()
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
