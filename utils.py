# utils.py
from db import SessionLocal
from models import Event, Artist, Format, Resource, Promoter, User
from datetime import date, datetime, timedelta
from sqlalchemy.orm import joinedload

# ---------- EVENTS ----------
def create_event(title, date_, format_obj=None, promoter_obj=None, location=None, notes=None, status="proposta", artist_objs=None, resource_objs=None):
    db = SessionLocal()
    try:
        ev = Event(date=date_, title=title, format=format_obj, promoter=promoter_obj, location=location, notes=notes, status=status)
        if artist_objs:
            for a in artist_objs:
                ev.artists.append(a)
        if resource_objs:
            for r in resource_objs:
                ev.resources.append(r)
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
    finally:
        db.close()

def update_event(event_id, **kwargs):
    db = SessionLocal()
    try:
        ev = db.query(Event).get(event_id)
        for k, v in kwargs.items():
            setattr(ev, k, v)
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
    finally:
        db.close()

def delete_event(event_id):
    db = SessionLocal()
    try:
        ev = db.query(Event).get(event_id)
        db.delete(ev)
        db.commit()
    finally:
        db.close()

def list_events_by_month(year, month):
    db = SessionLocal()
    try:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        q = db.query(Event).filter(Event.date >= start, Event.date < end).options(joinedload(Event.artists), joinedload(Event.format))
        return q.order_by(Event.date).all()
    finally:
        db.close()

def list_all_events():
    db = SessionLocal()
    try:
        return db.query(Event).options(joinedload(Event.artists), joinedload(Event.format)).order_by(Event.date.desc()).all()
    finally:
        db.close()

def get_event(event_id):
    db = SessionLocal()
    try:
        return db.query(Event).get(event_id)
    finally:
        db.close()

def list_upcoming_events(limit=10):
    db = SessionLocal()
    try:
        today = date.today()
        return db.query(Event).filter(Event.date >= today).order_by(Event.date).limit(limit).all()
    finally:
        db.close()

# ---------- ARTISTS ----------
def create_artist(name, bio=None, calendar_color="#2b8cbe", active=True):
    db = SessionLocal()
    try:
        a = Artist(name=name, bio=bio, calendar_color=calendar_color, active=active)
        db.add(a)
        db.commit()
        db.refresh(a)
        return a
    finally:
        db.close()

def list_artists():
    db = SessionLocal()
    try:
        return db.query(Artist).order_by(Artist.name).all()
    finally:
        db.close()

def get_artist(artist_id):
    db = SessionLocal()
    try:
        return db.query(Artist).get(artist_id)
    finally:
        db.close()

def update_artist(artist_id, **kwargs):
    db = SessionLocal()
    try:
        a = db.query(Artist).get(artist_id)
        for k, v in kwargs.items():
            setattr(a, k, v)
        db.add(a)
        db.commit()
        db.refresh(a)
        return a
    finally:
        db.close()

def delete_artist(artist_id):
    db = SessionLocal()
    try:
        a = db.query(Artist).get(artist_id)
        db.delete(a)
        db.commit()
    finally:
        db.close()

# ---------- FORMATS ----------
def create_format(name, description=None, default_duration_days=1):
    db = SessionLocal()
    try:
        f = Format(name=name, description=description, default_duration_days=default_duration_days)
        db.add(f)
        db.commit()
        db.refresh(f)
        return f
    finally:
        db.close()

def list_formats():
    db = SessionLocal()
    try:
        return db.query(Format).order_by(Format.name).all()
    finally:
        db.close()

def get_format(format_id):
    db = SessionLocal()
    try:
        return db.query(Format).get(format_id)
    finally:
        db.close()

def update_format(format_id, **kwargs):
    db = SessionLocal()
    try:
        f = db.query(Format).get(format_id)
        for k, v in kwargs.items():
            setattr(f, k, v)
        db.add(f)
        db.commit()
        db.refresh(f)
        return f
    finally:
        db.close()

def delete_format(format_id):
    db = SessionLocal()
    try:
        f = db.query(Format).get(format_id)
        db.delete(f)
        db.commit()
    finally:
        db.close()

# ---------- PROMOTERS ----------
def create_promoter(name, contact=None):
    db = SessionLocal()
    try:
        p = Promoter(name=name, contact=contact)
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    finally:
        db.close()

def list_promoters():
    db = SessionLocal()
    try:
        return db.query(Promoter).order_by(Promoter.name).all()
    finally:
        db.close()

def get_promoter(promoter_id):
    db = SessionLocal()
    try:
        return db.query(Promoter).get(promoter_id)
    finally:
        db.close()

def update_promoter(promoter_id, **kwargs):
    db = SessionLocal()
    try:
        p = db.query(Promoter).get(promoter_id)
        for k, v in kwargs.items():
            setattr(p, k, v)
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    finally:
        db.close()

def delete_promoter(promoter_id):
    db = SessionLocal()
    try:
        p = db.query(Promoter).get(promoter_id)
        db.delete(p)
        db.commit()
    finally:
        db.close()

# ---------- RESOURCES ----------
def create_resource(name, type, contact=None, availability=None):
    db = SessionLocal()
    try:
        r = Resource(name=name, type=type, contact=contact, availability=availability)
        db.add(r)
        db.commit()
        db.refresh(r)
        return r
    finally:
        db.close()

def list_resources(resource_type=None):
    db = SessionLocal()
    try:
        q = db.query(Resource)
        if resource_type:
            q = q.filter(Resource.type == resource_type)
        return q.order_by(Resource.name).all()
    finally:
        db.close()

def get_resource(resource_id):
    db = SessionLocal()
    try:
        return db.query(Resource).get(resource_id)
    finally:
        db.close()

def update_resource(resource_id, **kwargs):
    db = SessionLocal()
    try:
        r = db.query(Resource).get(resource_id)
        for k, v in kwargs.items():
            setattr(r, k, v)
        db.add(r)
        db.commit()
        db.refresh(r)
        return r
    finally:
        db.close()

def delete_resource(resource_id):
    db = SessionLocal()
    try:
        r = db.query(Resource).get(resource_id)
        db.delete(r)
        db.commit()
    finally:
        db.close()
