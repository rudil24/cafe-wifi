"""
WorkBrew seed script — populate the database with the 21 original London cafes.

Usage (local):
    python seed.py

Usage (Render one-off job):
    Set DATABASE_URL env var, then run via Render dashboard → Shell or Jobs.

Coordinates were geocoded via Nominatim on 2026-02-27 and are baked in here
so no external API calls are needed at seed time.
"""
from app import app
from extensions import db
from models import Cafe

CAFES = [
    dict(name="Science Gallery London",
         map_url="https://g.page/scigallerylon?share",
         img_url="https://atlondonbridge.com/wp-content/uploads/2019/02/Pano_9758_9761-Edit-190918_LTS_Science_Gallery-Medium-Crop-V2.jpg",
         location="London Bridge", has_sockets=True, has_toilet=True,
         has_wifi=False, can_take_calls=True, seats="50+", coffee_price="£2.40",
         lat=51.508049, lng=-0.0876715),
    dict(name="Social - Copeland Road",
         map_url="https://g.page/CopelandSocial?share",
         img_url="https://images.squarespace-cdn.com/content/v1/5734f3ff4d088e2c5b08fe13/1555848382269-9F13FE1WQDNUUDQOAOXF/ke17ZwdGBToddI8pDm48kAeyi0pcxjZfLZiASAF9yCBZw-zPPgdn4jUwVcJE1ZvWQUxwkmyExglNqGp0IvTJZUJFbgE-7XRK3dMEBRBhUpzV8NE8s7067ZLWyi1jRvJklJnlBFEUyq1al9AqaQ7pI4DcRJq_Lf3JCtFMXgpPQyk/copeland-park-bar-peckham",
         location="Peckham", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="20-30", coffee_price="£2.75",
         lat=51.4698658, lng=-0.0666424),
    dict(name="One & All Cafe Peckham",
         map_url="https://g.page/one-all-cafe?share",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOMzXpKAQNyUvrjTGHqCgWk8spwnzwP8Ml2aDKt=s0",
         location="Peckham", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="20-30", coffee_price="£2.75",
         lat=51.4657692, lng=-0.0665633),
    dict(name="Old Spike",
         map_url="https://www.google.com/maps/place/Old+Spike+Roastery/@51.4651552,-0.0666088,17z",
         img_url="https://lh3.googleusercontent.com/p/AF1QipPBAt6bYna7pv5c7e_PhCDPMKPb6oFf6kMT2VQ1=s0",
         location="Peckham", has_sockets=True, has_toilet=False,
         has_wifi=True, can_take_calls=False, seats="0-10", coffee_price="£2.80",
         lat=51.4734122, lng=-0.0699321),
    dict(name="Fuckoffee Bermondsey",
         map_url="https://goo.gl/maps/ugP2B1AV7FELHSgn6",
         img_url="https://lh3.googleusercontent.com/p/AF1QipM9Dz_QMkOF2da1aNLuTzS_vPvVWBnE84rZLK_G=s0",
         location="Bermondsey", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="20-30", coffee_price="£2.65",
         lat=51.4993407, lng=-0.0811767),
    dict(name="Mare Street Market",
         map_url="https://goo.gl/maps/DWnwaeeiwdYsBkEH9",
         img_url="https://lh3.googleusercontent.com/p/AF1QipN-C650VmJ1XZhzOIBTg1bUu3_to_GHpyrmUplt=s0",
         location="Hackney", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="50+", coffee_price="£2.80",
         lat=51.5377896, lng=-0.0572261),
    dict(name="Ace Hotel Shoreditch",
         map_url="https://g.page/acehotellondon?share",
         img_url="https://lh3.googleusercontent.com/p/AF1QipP_NbZH7A1fIQyp5pRm1jOGwzKsDWewaxka6vDt=s0",
         location="Shoreditch", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="50+", coffee_price="£3.00",
         lat=51.5256536, lng=-0.0772199),
    dict(name="Goswell Road Coffee",
         map_url="https://goo.gl/maps/D9nXNYK3fa1cxwpK8",
         img_url="https://lh3.googleusercontent.com/p/AF1QipPnOfo7wTICdiAyybF3iFhD3l5aoQjSO-GErma1=s0",
         location="Clerkenwell", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="10-20", coffee_price="£2.10",
         lat=51.5257484, lng=-0.0994778),
    dict(name="The Southwark Cathedral Cafe",
         map_url="https://goo.gl/maps/LU1imQzBCRLFBxKUA",
         img_url="https://lh3.googleusercontent.com/p/AF1QipMrdTyRRozGBltwxAseQ4QeuNhbED6meQXlCPsx=s0",
         location="London Bridge", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=True, seats="20-30", coffee_price="£2.30",
         lat=51.508049, lng=-0.0876715),
    dict(name="Trade Commercial Road",
         map_url="https://goo.gl/maps/v5tzRBVhPFueYp4x6",
         img_url="https://lh3.googleusercontent.com/p/AF1QipNtHqqIc3kwhpjknrVcMdkhmpA77LDYKmpOJlxf=s0",
         location="Whitechapel", has_sockets=False, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="20-30", coffee_price="£2.70",
         lat=51.5174861, lng=-0.0659685),
    dict(name="The Tate Modern Cafe",
         map_url="https://goo.gl/maps/6RvPHyhsDDUPs1ox8",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOFimpFQmUORVGg0ER3lrfEiEnKpnYJck5guFqC=s0",
         location="Bankside", has_sockets=False, has_toilet=True,
         has_wifi=True, can_take_calls=True, seats="30-40", coffee_price="£2.70",
         lat=51.508176, lng=-0.0991338),
    dict(name="Forage Cafe",
         map_url="https://goo.gl/maps/HC4e9FJL48kLRH8W9",
         img_url="https://lh3.googleusercontent.com/p/AF1QipPyJHFtVzxor4RyQrT-ZEk7ej7OxvmIQYZUHe6G=s0",
         location="Clerkenwell", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=True, seats="20-30", coffee_price="£2.50",
         lat=51.5237268, lng=-0.1055555),
    dict(name="Citizen M Hotel Shoreditch",
         map_url="https://g.page/citizenm-london-shoreditch?share",
         img_url="https://lh3.googleusercontent.com/p/AF1QipNJQIg-6YTOZhbLu12yGPN3klDxygs7cNAjEo0C=s0",
         location="Shoreditch", has_sockets=True, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="30-40", coffee_price="£2.80",
         lat=51.5266694, lng=-0.0798926),
    dict(name="Barbican Centre",
         map_url="https://goo.gl/maps/XPrcFj91LsQBvUa27",
         img_url="https://images.adsttc.com/media/images/5014/ec99/28ba/0d58/2800/0d0f/large_jpg/stringio.jpg?1414576924",
         location="Barbican", has_sockets=False, has_toilet=True,
         has_wifi=True, can_take_calls=True, seats="50+", coffee_price="£3.00",
         lat=51.5206514, lng=-0.0938065),
    dict(name="The Slaughtered Lamb",
         map_url="https://goo.gl/maps/mwAG272nQwSUc9bn8",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOL6jxxpE_D3YS-Zzih61DqNXJKvRIDFiP6ieUI=s0",
         location="Clerkenwell", has_sockets=False, has_toilet=True,
         has_wifi=True, can_take_calls=False, seats="20-30", coffee_price="£2.60",
         lat=51.5233142, lng=-0.101209),
    dict(name="Fernandez and Wells Exhibition Road",
         map_url="https://goo.gl/maps/GPFSEuGEiDvQG8BH7",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOchpT9ipgb7tpqglcTKpp2E8kZhsKvlYjUZ4e1=s0",
         location="South Kensington", has_sockets=False, has_toilet=False,
         has_wifi=True, can_take_calls=False, seats="10-20", coffee_price="£1.80",
         lat=51.4955817, lng=-0.1831368),
    dict(name="Whitechapel Grind",
         map_url="https://goo.gl/maps/xv29seioiETAAZgN9",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOZ3WDAAxphLu657afVVATJ5TGxtturIOr8gt8u=s0",
         location="Whitechapel", has_sockets=True, has_toilet=False,
         has_wifi=True, can_take_calls=True, seats="30-40", coffee_price="£2.60",
         lat=51.5174861, lng=-0.0659685),
    dict(name="The Peckham Pelican",
         map_url="https://goo.gl/maps/qpcpX7MWhFSS1qxH9",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOutkI7wjWNXiPSTdf8CX0jXwyVHFTwFnVhyVJE=s0",
         location="Peckham", has_sockets=True, has_toilet=False,
         has_wifi=True, can_take_calls=True, seats="0-10", coffee_price="£2.60",
         lat=51.4734122, lng=-0.0699321),
    dict(name="Natural History Museum Library",
         map_url="https://goo.gl/maps/VU2PwnDDtH1WqCnK7",
         img_url="https://www.nhm.ac.uk/content/dam/nhmwww/business-services/filming/Earth-Sciences-Library-1.jpg",
         location="South Kensington", has_sockets=True, has_toilet=False,
         has_wifi=True, can_take_calls=False, seats="40-50", coffee_price="£2.00",
         lat=51.4955817, lng=-0.1831368),
    dict(name="The Bike Shed",
         map_url="https://goo.gl/maps/gYX271NxyuawiMcK8",
         img_url="https://lh3.googleusercontent.com/p/AF1QipNlBWFgXBiP9YjKARy4dgjHGePOmtsfuQPRwGvb=s0",
         location="Shoreditch", has_sockets=True, has_toilet=False,
         has_wifi=True, can_take_calls=False, seats="10-20", coffee_price="£2.80",
         lat=51.5270214, lng=-0.0786762),
    dict(name="FORA Borough",
         map_url="https://g.page/fora---borough?share",
         img_url="https://lh3.googleusercontent.com/p/AF1QipOhkJk2MBtFW1RydPU0zf3bf8upGkTQWyhDpXzZ=s0",
         location="Borough", has_sockets=True, has_toilet=False,
         has_wifi=True, can_take_calls=True, seats="20-30", coffee_price="£2.40",
         lat=51.5210206, lng=-0.0763506),
]


def run() -> None:
    with app.app_context():
        db.create_all()
        existing = Cafe.query.count()
        if existing:
            print(f"DB already has {existing} cafe(s) — skipping seed to avoid duplicates.")
            return
        db.session.add_all([Cafe(**c) for c in CAFES])
        db.session.commit()
        print(f"Seeded {len(CAFES)} cafes successfully.")


if __name__ == "__main__":
    run()
