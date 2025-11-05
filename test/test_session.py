from pathlib import Path
import pytest
from session.session import SessionManager
from db.manager import DatabaseManager


@pytest.fixture
def temp_paths(tmp_path: Path):
    return {
        "db_file": tmp_path / "test.db",
        "schema_file": tmp_path / "schema.sql",
        "session_file": tmp_path / "session.txt",
    }


SCHEMA_TEXT = """
CREATE TABLE IF NOT EXISTS USER (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL
);
"""


@pytest.fixture
def temp_db(temp_paths):
    temp_paths["schema_file"].write_text(SCHEMA_TEXT, encoding="utf-8")
    db = DatabaseManager(str(temp_paths["db_file"]))
    db.run_schema_file(str(temp_paths["schema_file"]))
    try:
        yield db
    finally:
        db.close()


def create_user(db: DatabaseManager, name="Alice", email="alice@example.com") -> int:
    return db.execute("INSERT INTO USER(name, email) VALUES(?, ?)", (name, email))


def test_login_persists_session_and_autologin(temp_db: DatabaseManager, temp_paths):
    session = SessionManager(temp_paths["session_file"])
    user_id = create_user(temp_db)

    # Simulate login
    session.save(user_id)
    assert temp_paths["session_file"].exists()

    # Simulate app restart (fresh SessionManager)
    session2 = SessionManager(temp_paths["session_file"])
    loaded = session2.load()
    assert loaded == user_id
    assert temp_db.user_exists(loaded) is True


def test_logout_removes_session_file(temp_db: DatabaseManager, temp_paths):
    session = SessionManager(temp_paths["session_file"])
    uid = create_user(temp_db, "Bob", "bob@example.com")
    session.save(uid)
    assert temp_paths["session_file"].exists()

    session.clear()
    assert not temp_paths["session_file"].exists()

    # Next start -> no auto-login
    loaded = SessionManager(temp_paths["session_file"]).load()
    assert loaded is None


def test_corrupt_or_empty_session_falls_back_to_login(temp_db: DatabaseManager, temp_paths):
    p = temp_paths["session_file"]

    # Empty file
    p.write_text("", encoding="utf-8")
    assert SessionManager(p).load() is None

    # Non-integer
    p.write_text("not-an-int", encoding="utf-8")
    assert SessionManager(p).load() is None

    # Negative / zero
    p.write_text("0", encoding="utf-8")
    assert SessionManager(p).load() is None
    p.write_text("-5", encoding="utf-8")
    assert SessionManager(p).load() is None


def test_missing_session_file_is_safe(temp_db: DatabaseManager, temp_paths):
    # No file created
    loaded = SessionManager(temp_paths["session_file"]).load()
    assert loaded is None


def test_autologin_blocks_nonexistent_user(temp_db: DatabaseManager, temp_paths):
    # Save a user_id that does not exist (e.g., stale file from old install)
    SessionManager(temp_paths["session_file"]).save(999999)
    loaded = SessionManager(temp_paths["session_file"]).load()
    assert loaded == 999999
    # Guard in bootstrap: check DB before trusting
    assert temp_db.user_exists(loaded) is False
