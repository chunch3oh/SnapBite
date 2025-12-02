import importlib
import sqlite3

import linebot_app.storage as storage_module


def test_save_analysis_log_writes_row(tmp_path, monkeypatch):
    db_path = tmp_path / "snapbite_test.db"
    monkeypatch.setenv("SNAPBITE_DB_PATH", str(db_path))

    # Reload module so it picks up the temp DB path
    storage = importlib.reload(storage_module)

    storage.save_analysis_log(
        user_id="user123",
        message_id="msg123",
        analysis={"food_items": [{"name": "test"}]},
    )

    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT user_id, message_id, analysis_json FROM meal_analysis"
        ).fetchall()

    assert len(rows) == 1
    user_id, message_id, analysis_json = rows[0]
    assert user_id == "user123"
    assert message_id == "msg123"
    assert "food_items" in analysis_json
