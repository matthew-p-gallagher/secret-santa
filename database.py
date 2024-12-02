from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Table,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from datetime import datetime
from flask import current_app

Base = declarative_base()

# Association table for exclusion pairs
exclusion_pairs = Table(
    "exclusion_pairs",
    Base.metadata,
    Column("person1_id", Integer, ForeignKey("participants.id")),
    Column("person2_id", Integer, ForeignKey("participants.id")),
)


class MatchingSession(Base):
    __tablename__ = "matching_sessions"

    id = Column(Integer, primary_key=True)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    access_code = Column(String(4), unique=True)
    assigned_to_id = Column(Integer, ForeignKey("participants.id"))
    matching_session_id = Column(Integer, ForeignKey("matching_sessions.id"))

    # Relationship for exclusions (bidirectional)
    excluded_pairs = relationship(
        "Participant",
        secondary=exclusion_pairs,
        primaryjoin=id == exclusion_pairs.c.person1_id,
        secondaryjoin=id == exclusion_pairs.c.person2_id,
        backref="excluded_by",
    )


def init_db(app):
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session
