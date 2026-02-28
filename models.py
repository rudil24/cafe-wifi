"""SQLAlchemy ORM model for the Cafe entity."""
from extensions import db


class Cafe(db.Model):
    __tablename__ = "cafe"

    id             = db.Column(db.Integer,      primary_key=True)
    name           = db.Column(db.String(250),  unique=True, nullable=False)
    map_url        = db.Column(db.String(500),  nullable=False)
    img_url        = db.Column(db.String(500),  nullable=False)
    location       = db.Column(db.String(250),  nullable=False)
    has_sockets    = db.Column(db.Boolean,      nullable=False, default=False)
    has_toilet     = db.Column(db.Boolean,      nullable=False, default=False)
    has_wifi       = db.Column(db.Boolean,      nullable=False, default=False)
    can_take_calls = db.Column(db.Boolean,      nullable=False, default=False)
    seats          = db.Column(db.String(250),  nullable=True)
    coffee_price   = db.Column(db.String(250),  nullable=True)
    lat            = db.Column(db.Float,        nullable=True)
    lng            = db.Column(db.Float,        nullable=True)

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dict for Leaflet map consumption."""
        return {
            "id":            self.id,
            "name":          self.name,
            "location":      self.location,
            "lat":           self.lat,
            "lng":           self.lng,
            "has_wifi":      self.has_wifi,
            "has_sockets":   self.has_sockets,
            "can_take_calls": self.can_take_calls,
        }
