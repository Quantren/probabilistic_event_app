from collections import Counter
from flask import session

def initialize_session():
    if "history" not in session:
        session["history"] = []
    if "track" not in session:
        session["track"] = True

def is_track_enabled():
    return session.get("track", True)

def set_tracking(track):
    session["track"] = track
    session.modified = True

def filter_history_by_type(history, type):
    return [entry for entry in history if entry["type"] == type]

def filter_history_by_date_range(history, start_date, end_date):
    return [
        entry for entry in history if start_date <= entry["timestamp"] <= end_date
    ]

def record(entry: dict):
    # history = session.get("history", [])
    history = session.setdefault("history", [])
    history.append(entry)
    # session["history"] = history
    session.modified = True

def all_history():
    return session.get("history", [])

def clear_history():
    session["history"] = []
    session.modified = True

def create_dist_dict(label: str) -> dict[str | int, int]:
    history = session.get("history", [])
    history = filter_history_by_type(history, label)
    dist_dict = Counter(
        entry["outcome"] for entry in history if entry["label"] == label
    )
    return dict(dist_dict)

def known_labels() -> list[str]:
    return list(set(entry["label"] for entry in session.get("history", [])))
