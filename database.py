from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for exclusion pairs
exclusion_pairs = db.Table(
    "exclusion_pairs",
    db.Column("person1_id", db.Integer, db.ForeignKey("participants.id")),
    db.Column("person2_id", db.Integer, db.ForeignKey("participants.id")),
)


class MatchingSession(db.Model):
    __tablename__ = "matching_sessions"

    id = db.Column(db.Integer, primary_key=True)
    is_finalized = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    access_code = db.Column(db.String(4), unique=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("participants.id"))
    matching_session_id = db.Column(db.Integer, db.ForeignKey("matching_sessions.id"))

    # Relationship for exclusions (bidirectional)
    excluded_pairs = db.relationship(
        "Participant",
        secondary=exclusion_pairs,
        primaryjoin=id == exclusion_pairs.c.person1_id,
        secondaryjoin=id == exclusion_pairs.c.person2_id,
        backref="excluded_by",
    )
