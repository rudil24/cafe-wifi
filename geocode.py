"""
One-time script: populate lat/lng for all Cafe records using Nominatim (OpenStreetMap).

Usage:
    python geocode.py

Rate limit: Nominatim requires max 1 request/second.
21 cafes ≈ ~30 seconds total. Run once before first deployment.
"""
import time

import requests
from app import app
from extensions import db
from models import Cafe

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "WorkBrew/1.0 (portfolio project, no commercial use)"}


def geocode(name: str, location: str) -> tuple[float, float] | None:
    """Return (lat, lng) for a cafe name + neighbourhood, or None on failure."""
    for query in [f"{name}, {location}, London, UK", f"{location}, London, UK"]:
        try:
            resp = requests.get(
                NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1, "countrycodes": "gb"},
                headers=HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json()
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
        except requests.RequestException as exc:
            print(f"  ⚠ Request error for '{query}': {exc}")
        time.sleep(1)  # Nominatim rate limit
    return None


def run() -> None:
    with app.app_context():
        cafes_missing = Cafe.query.filter(Cafe.lat.is_(None)).all()
        print(f"Found {len(cafes_missing)} cafe(s) missing coordinates.\n")

        for cafe in cafes_missing:
            print(f"Geocoding: {cafe.name} ({cafe.location}) …", end=" ", flush=True)
            result = geocode(cafe.name, cafe.location)
            if result:
                cafe.lat, cafe.lng = result
                print(f"✅ {cafe.lat:.4f}, {cafe.lng:.4f}")
            else:
                print("❌ not found — skipped")
            time.sleep(1)

        db.session.commit()
        print("\n✅ Geocoding complete. Coordinates saved.")

        # Summary
        total   = Cafe.query.count()
        mapped  = Cafe.query.filter(Cafe.lat.isnot(None)).count()
        print(f"   {mapped}/{total} cafes now have coordinates.")


if __name__ == "__main__":
    run()
