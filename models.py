# models.py
from sqlalchemy import Column, Integer, String, Date, Text, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

# association tables
event_artist = Table(
    "event_artist", Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)

event_resource = Table(
    "event_resource", Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
    Column("resource_id", Integer, ForeignKey("resources.id"), primary_key=True),
)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    title = Column(String, index=True)
    format_id = Column(Integer, ForeignKey("formats.id"))
    promoter_id = Column(Integer, ForeignKey("promoters.id"), nullable=True)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, default="proposta")  # proposta / confermato / cancellato

    format = relationship("Format", back_populates="events")
    artists = relationship("Artist", secondary=event_artist, back_populates="events")
    resources = relationship("Resource", secondary=event_resource, back_populates="events")
    promoter = relationship("Promoter", back_populates="events")

class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    bio = Column(Text, nullable=True)
    calendar_color = Column(String, default="#2b8cbe")
    active = Column(Boolean, default=True)

    events = relationship("Event", secondary=event_artist, back_populates="artists")

class Format(Base):
    __tablename__ = "formats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    default_duration_days = Column(Integer, default=1)

    events = relationship("Event", back_populates="format")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)  # DJ, Vocalist, Ballerina, Service, Tour Manager, Mascotte
    contact = Column(String, nullable=True)
    availability = Column(Text, nullable=True)

    events = relationship("Event", secondary=event_resource, back_populates="resources")

class Promoter(Base):
    __tablename__ = "promoters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    contact = Column(String, nullable=True)

    events = relationship("Event", back_populates="promoter")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")  # admin, manager, viewer
