from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import Base, init_db, Participant, MatchingSession
from matching import generate_matches
import random
import string
import os
from functools import wraps

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")

# Initialize database
db = init_db(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


def generate_access_code():
    while True:
        code = "".join(random.choices(string.digits, k=4))
        # Check if code already exists
        exists = db.query(Participant).filter_by(access_code=code).first()
        if not exists:
            return code


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please login first")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def home():
    return render_template("participant_entry.html")


@app.route("/view_match", methods=["POST"])
def view_match():
    code = request.form.get("access_code")
    participant = db.query(Participant).filter_by(access_code=code).first()

    if not participant:
        flash("Invalid access code")
        return redirect(url_for("home"))

    assigned_to = db.query(Participant).get(participant.assigned_to_id)
    return render_template(
        "participant_result.html", participant=participant, assigned_to=assigned_to
    )


@app.route("/admin")
@admin_required
def admin():
    participants = db.query(Participant).all()
    current_session = (
        db.query(MatchingSession).order_by(MatchingSession.created_at.desc()).first()
    )
    return render_template(
        "admin.html", participants=participants, current_session=current_session
    )


@app.route("/admin/add_participant", methods=["POST"])
@admin_required
def add_participant():
    name = request.form.get("name")

    participant = Participant(name=name)
    db.add(participant)
    db.commit()

    flash(f"Added participant: {name}")
    return redirect(url_for("admin"))


@app.route("/admin/generate_matches", methods=["POST"])
@admin_required
def generate_matches_route():
    # Create new matching session
    session = MatchingSession()
    db.add(session)
    db.commit()

    participants = db.query(Participant).all()
    participant_ids = [p.id for p in participants]

    # Get exclusion pairs
    exclusions = []
    for p in participants:
        for excluded in p.excluded_pairs:
            exclusions.append((p.id, excluded.id))

    try:
        matches = generate_matches(participant_ids, exclusions)

        # Assign matches and generate codes
        for giver_id, receiver_id in matches.items():
            participant = db.query(Participant).get(giver_id)
            participant.assigned_to_id = receiver_id
            participant.matching_session_id = session.id
            participant.access_code = generate_access_code()

        db.commit()
        flash("Successfully generated new matches!")

    except ValueError as e:
        db.rollback()
        flash(
            "Failed to generate matches. Please check exclusions and try again.",
            "error",
        )

    return redirect(url_for("admin"))


@app.route("/admin/add_exclusion", methods=["POST"])
@admin_required
def add_exclusion():
    person1_id = request.form.get("person1_id")
    person2_id = request.form.get("person2_id")

    person1 = db.query(Participant).get(person1_id)
    person2 = db.query(Participant).get(person2_id)

    if person1 and person2:
        person1.excluded_pairs.append(person2)
        db.commit()
        flash(f"Added exclusion: {person1.name} ↔ {person2.name}")

    return redirect(url_for("admin"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == app.config["ADMIN_PASSWORD"]:
            session["is_admin"] = True
            return redirect(url_for("admin"))
        flash("Invalid password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
