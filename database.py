"""
Module for handling all database interactions using SQLite

Need methods to init connection, close connection, get connection, write to db, etc.

Will define schema as well
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager
from flask import current_app, g

def get_db() -> sqlite3.Connection:
    # Returns current db connection, creates if doesn't exist
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None) -> None:
    # Close db connection if exists
    # Removes db from g
    db = g.pop('db', None)
    if db is not None:
        db.close()

SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    label TEXT NOT NULL,
    outcome TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
"""

def init_db(app) -> None:
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()

def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    init_db(app)

def save_record(record: dict) -> int | None:
    db = get_db()
    cursor = db.execute("INSERT INTO history (type, label, outcome, timestamp) VALUES (?, ?, ?, ?)",
                        (record["type"], record["label"], str(record["outcome"]), record["timestamp"]))
    db.commit()
    return cursor.lastrowid

def save_records(records: list[dict]) -> int:
    db = get_db()
    rows = [(record["type"], record["label"], str(record["outcome"]), record["timestamp"]) for record in records]
    cursor = db.executemany("INSERT INTO history (type, label, outcome, timestamp) VALUES (?, ?, ?, ?)", rows)
    db.commit()
    return len(rows)

def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "type": row["type"],
        "label": row["label"],
        "outcome": row["outcome"],
        "timestamp": row["timestamp"]
    }

def get_record(id: int) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM history WHERE id = ?", (id,)).fetchone()
    return row_to_dict(row) if row else None

def get_records_by_label(label: str, limit: int | None =None) -> list[dict]:
    db = get_db()
    params = []
    params.append(label,)

    sql_stub = "SELECT * FROM history WHERE label = ? ORDER BY id DESC"

    if limit is not None:
        sql_stub += " LIMIT ?"
        params.append((int(limit),))

    rows = db.execute(sql_stub, params).fetchall()
    return [row_to_dict(row) for row in rows]

def get_all_records(limit: int | None = None) -> list[dict]:
    db = get_db()
    params = []
    
    sql_stub = "SELECT * FROM history ORDER BY id DESC"

    if limit is not None:
        sql_stub += " LIMIT ?"
        params.append((int(limit),))

    rows = db.execute(sql_stub, params).fetchall()
    return [row_to_dict(row) for row in rows]

def get_recent_records(label: str | None = None, limit: int = 100) -> list[dict]:
    db = get_db()
    params = []
    
    sql_stub = "SELECT * FROM history"
    
    if label is not None:
        sql_stub += " WHERE label = ?"
        params.append(label)

    sql_stub += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    rows = db.execute(sql_stub, params).fetchall()
    return [row_to_dict(row) for row in rows]

def clear_records_by_label(label: str) -> int:
    db = get_db()
    cursor = db.execute("DELETE FROM history WHERE label = ?", (label,))
    db.commit()
    return cursor.rowcount

def clear_all_records() -> int:
    db = get_db()
    cursor = db.execute("DELETE FROM history")
    db.commit()
    return cursor.rowcount

def get_known_labels() -> list[str]:
    # Need this to populate dropdowns for filtering on history
    db = get_db()
    rows = db.execute("SELECT DISTINCT label FROM history ORDER BY label").fetchall()
    return [row["label"] for row in rows]
