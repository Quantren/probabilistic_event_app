import os
import sys
import json

import session_settings
from events import event_factory
from collections import Counter
from flask import Flask, flash, redirect, render_template, request, url_for
import database

app = Flask(__name__)
# For DB integration https://flask.palletsprojects.com/en/stable/config/
app.config['DATABASE'] = 'database.sqlite'
database.init_app(app)
# Apparently Flask needs a secret key for session management, included below
app.secret_key = "secret-key-required-for-session-management"

@app.before_request
def _ensure_session():
    session_settings.initialize_session()

@app.route('/')
def index():
    # Route to the homepage, which will display the probabilistic events available
    return render_template('index.html',
                           tracking=session_settings.is_track_enabled(),
                           history=session_settings.all_history())

@app.route('/perform', methods=['POST'])
def perform():
    # Perform an event based on form data submitted in session
    # Default event type is coin, suppose this makes sense as a die as it is the probabilistic event with the least amount of sides
    # which is a common attribute between the different types of events
    event_type = request.form.get("kind", "coin")
    times = int(request.form.get("times", 1))

    # Params kept simple, p_heads is probability of obtaining a heads result for a coin, faces is the number of faces for a die
    params = {
        "p_heads": float(request.form.get("p_heads", 0.5)),
        "faces": int(request.form.get("faces", 6))
    }

    # Try, except to capture errors and output as str
    try:
        event = event_factory(event_type, params)
    except ValueError as e:
        return str(e), 400
    
    # List comprehension to perform event a specified number of times - not the most Pythonic way to do this tbh
    outcomes = [event.perform() for _ in range(times)]

    # Taking all outcomes just run and creating a list of records
    records = [event.to_record(outcome) for outcome in outcomes]

    # Tracking fix - check the input provided by the form
    is_tracked = request.form.get("track") == "on"

    # Store the records if tracking is enabled
    if is_tracked:
        database.save_records(records)
        for record in records:
            session_settings.record(record)
        stored = True

    else:
        stored = False

    # Create a simple summary of outcomes by counting occurrences of each outcome
    summary = dict(Counter(str(outcome) for outcome in outcomes))

    # Once the event(s) have been performed, render the result template
    return render_template(
        "result.html",
        event_type=event_type,
        params=params,
        outcomes=outcomes,
        summary=summary,
        stored=stored
    )


@app.route("/tracking", methods=["POST"])
def tracking():
    # Set session tracking based on form input
    session_settings.set_tracking(request.form.get("track") == "on")
    flash(
        f"Tracking is now {'ON' if session_settings.is_track_enabled() else 'OFF'}.",
        "info",
    )
    return redirect(request.referrer or url_for("index"))


@app.route("/history")
def history():
    # Set infrastructure for history page, which has the ability to view the db records
    label = request.args.get("label") or None
    rows = database.get_recent_records(label=label, limit=100)
    labels = database.get_known_labels()
    return render_template(
        "history.html",
        rows=rows,
        labels=labels,
        active_label=label or "",
        total=len(rows),
    )

@app.route("/history/clear", methods=["POST"])
def history_clear():
    # Clear the history of the session
    deleted = database.clear_all_records()
    session_settings.clear_history()
    flash("Cleared all stored results for this session.", "info")
    return redirect(url_for("history"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
