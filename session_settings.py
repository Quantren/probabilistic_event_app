from collections import Counter
from flask import session

def initialize_session():
    # Initialize session with default values
    # This should allow for providing a previous history and tracking setting if they exist
    # TODO: How do we implement reading in of history from a file?
    if "history" not in session:
        session["history"] = []
    if "track" not in session:
        session["track"] = True

def is_track_enabled():
    # Method for checking if tracking is enabled
    return session.get("track", True)

def set_tracking(track):
    # Method for setting tracking value
    session["track"] = track
    session.modified = True

def filter_history_by_type(history, type):
    # Method to filter history by an event type. List comprehension may not be the most efficient way to do this
    # as it is iterating through the history, rather than performing some sort of lookup
    # Could implement a lookup by using more efficient data structures
    return [entry for entry in history if entry["type"] == type]

def filter_history_by_date_range(history, start_date, end_date):
    # Method to filter history by a date range
    return [
        entry for entry in history if start_date <= entry["timestamp"] <= end_date
    ]

def record(entry: dict):
    # Set default over get allows us to avoid having to assign back to session by providing a reference to the list
    # instead of a copy of the list that we later have to assign
    # history = session.get("history", [])
    history = session.setdefault("history", [])
    history.append(entry)
    # session["history"] = history
    session.modified = True

def all_history():
    # As we are reading the history, we just use get
    return session.get("history", [])

def clear_history():
    # Clearing history is as simple as assigning an empty list to the history key in session
    session["history"] = []
    session.modified = True
