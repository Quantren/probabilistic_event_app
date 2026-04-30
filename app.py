import os
import sys
import json

import session_settings
from events import event_factory
from collections import Counter
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "secret-key-required-for-session-management"

@app.before_request
def _ensure_session():
    session_settings.initialize_session()

@app.route('/')
def index():
    return render_template('index.html',
                           tracking=session_settings.is_track_enabled(),
                           history=session_settings.all_history())

@app.route('/perform', methods=['POST'])
def perform():
    event_type = request.form.get("kind", "coin")
    times = int(request.form.get("times", 1))


    params = {
        "p_heads": float(request.form.get("p_heads", 0.5)),
        "faces": int(request.form.get("faces", 6))
    }

    try:
        event = event_factory(event_type, params)
    except ValueError as e:
        return str(e), 400
    
    outcomes = [event.perform() for _ in range(times)]
    records = [event.to_record(outcome) for outcome in outcomes]

    if session_settings.is_track_enabled():
        for record in records:
            session_settings.record(record)
        stored = True

    else:
        stored = False

    summary = dict(Counter(str(outcome) for outcome in outcomes))

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
    session_settings.set_tracking(request.form.get("track") == "on")
    flash(
        f"Tracking is now {'ON' if session_settings.is_track_enabled() else 'OFF'}.",
        "info",
    )
    return redirect(request.referrer or url_for("index"))


@app.route("/history")
def history():
    label = request.args.get("label", "__all__")
    rows = list(reversed(session_settings.filter_history_by_type(session_settings.all_history(), label)))
    return render_template(
        "history.html",
        rows=rows,
        labels=session_settings.known_labels(),
        active_label=label,
        total=len(rows),
    )

@app.route("/history/clear", methods=["POST"])
def history_clear():
    session_settings.clear_history()
    flash("Cleared all stored results for this session.", "info")
    return redirect(url_for("history"))


@app.route("/distribution")
def distribution():
    labels = session_settings.known_labels()
    label = request.args.get("label") or (labels[0] if labels else None)
    dist = session_settings.create_dist_dict(label) if label else {}
    total = sum(dist.values())

    def sort_key(k):
        try:
            return (0, float(k))
        except ValueError:
            return (1, k)

    sorted_items = sorted(dist.items(), key=lambda kv: sort_key(kv[0]))
    max_count = max(dist.values()) if dist else 0

    return render_template(
        "distribution.html",
        labels=labels,
        active_label=label,
        items=sorted_items,
        total=total,
        max_count=max_count,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
