import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("SNAPBITE_DB_PATH", "data/snapbite.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS meal_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    message_id TEXT,
    analysis_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(_CREATE_TABLE_SQL)


def save_analysis_log(user_id: str, message_id: str, analysis: Any) -> None:
    """
    Save analysis data for a message into SQLite.
    """
    _init_db()
    if analysis is None:
        analysis_json = ""
    elif hasattr(analysis, "model_dump_json"):
        analysis_json = analysis.model_dump_json()
    else:
        analysis_json = json.dumps(analysis, ensure_ascii=False)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO meal_analysis (user_id, message_id, analysis_json) VALUES (?, ?, ?)",
            (user_id, message_id, analysis_json),
        )
        conn.commit()
