# seed_data.py
from db import engine, Base, SessionLocal
from models import Artist, Format, Resource, Promoter, User, Event
from auth import hash_password
from datetime import date, timedelta

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Users
        if not db.query(User).first():
            db.add_all([
                User(username="admin", hashed_password=hash_password("adminpass"), role="admin"),
                User(username="manager", hashed_password=hash_password("managerpass"), role="manager"),
                User(username="viewer", hashed_password=hash_password("viewerpass"), role="viewer"),
            ])
            db.commit()

        # Artists
        if not db.query(Artist).first():
            a1 = Artist(name="Artista A", calendar_color="#1f77b4")
            a2 = Artist(name="Artista B", calendar_color="#ff7f0e")
            db.add_all([a1, a2])
            db.commit()

        # Formats
        if not db.query(Format).first():
            f1 = Format(name="Format 1", description="Show principale")
            f2 = Format(name="Format 2", description="Set acustico")
            db.add_all([f1, f2])
            db.commit()

        # Promoters
        if not db.query(Promoter).first():
            p1 = Promoter(name="Promoter X", contact="promoterx@example.com")
            p2 = Promoter(name="Promoter Y", contact="promotory@example.com")
            db.add_all([p1, p2])
            db.commit()

        # Resources: DJ, Vocalist, Ballerine, Service, Tour Manager, Mascotte
        if not db.query(Resource).first():
            r1 = Resource(name="DJ Marco", type="DJ", contact="djmarco@example.com")
            r2 = Resource(name="Vocalist Anna", type="Vocalist", contact="anna@example.com")
            r3 = Resource(name="Ballerina Squad", type="Ballerina", contact="dance@example.com")
            r4 = Resource(name="Service Impianti 1", type="Service", contact="service@example.com")
            r5 = Resource(name="Tour Manager Luca", type="Tour Manager", contact="luca@example.com")
            r6 = Resource(name="Mascotte M", type="Mascotte", contact="mascotte@example.com")
            db.add_all([r1, r2, r3, r4, r5, r6])
            db.commit()

        # Events sample
        if not db.query(Event).first():
            artists = db.query(Artist).all()
            formats = db.query(Format).all()
            promoter = db.query(Promoter).first()
            today = date.today()
            e1 = Event(date=today, title="Evento Demo 1", format=formats[0], promoter=promoter, location="Rimini", notes="Note demo", status="confermato")
            e1.artists.append(artists[0])
            e2 = Event(date=today + timedelta(days=3), title="Evento Demo 2", format=formats[1], promoter=promoter, location="Bologna", notes="Note 2", status="proposta")
            e2.artists.append(artists[1])
            # assign resources
            res = db.query(Resource).filter(Resource.type == "DJ").first()
            if res:
                e1.resources.append(res)
            db.add_all([e1, e2])
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
    print("DB seeded.")
