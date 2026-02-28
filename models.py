from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime


class Animal(Base):
    __tablename__ = "animals"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    rfid = Column(String, unique=True, index=True, nullable=True)
    breed = Column(String)
    birth_date = Column(Date)
    entry_date = Column(Date, default=datetime.date.today)
    initial_weight = Column(Float)
    current_weight = Column(Float)
    status = Column(String)  # active, sold, dead, quarantine
    paddock_id = Column(Integer, ForeignKey("paddocks.id"), nullable=True)

    paddock = relationship("Paddock", back_populates="animals")
    events = relationship("Event", back_populates="animal")


class Paddock(Base):
    __tablename__ = "paddocks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    area = Column(Float)  # in hectares
    capacity = Column(Integer)  # max heads
    geometry = Column(Text)  # JSON string for map coordinates
    current_load = Column(Integer, default=0)

    animals = relationship("Animal", back_populates="paddock")
    scores = relationship("Score", back_populates="paddock")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"))
    date = Column(Date, default=datetime.date.today)
    event_type = Column(String)  # weight, vaccine, move, illness, death
    value = Column(Float, nullable=True)  # e.g. weight value, cost
    details = Column(String, nullable=True)

    animal = relationship("Animal", back_populates="events")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String)
    category = Column(String)  # feed, medicine, other
    quantity = Column(Float)
    unit = Column(String)
    cost_per_unit = Column(Float)
    expiry_date = Column(Date, nullable=True)


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    paddock_id = Column(Integer, ForeignKey("paddocks.id"), nullable=True)
    date = Column(Date, default=datetime.date.today)
    score_type = Column(String)  # pasture, stool, bcs, bunk
    value = Column(Float)
    notes = Column(Text, nullable=True)

    paddock = relationship("Paddock", back_populates="scores")


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    assignee = Column(String)
    status = Column(String)  # pending, in_progress, completed
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.datetime.now)
