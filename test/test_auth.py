from pathlib import Path

import pytest

from db.manager import DatabaseManager
from service.auth import authenticate

SCHEMA = """
CREATE TABLE IF NOT EXISTS USER (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL
);
"""


@pytest.fixture
def db(tmp_path: Path):
    db_path = tmp_path / "t.db"
    mgr = DatabaseManager(str(db_path))
    # load schema
    mgr.conn.executescript(SCHEMA)
    mgr.conn.commit()
    yield mgr
    mgr.close()


def test_new_email_creates_user(db):
    status, user = authenticate(
        db, "Alice", "alice@example.com", confirm_on_mismatch=lambda a, b: True)
    assert status == "created"
    assert user is not None
    # row exists
    rows = db.fetchall("SELECT * FROM USER WHERE email=?",
                       ("alice@example.com",))
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"


def test_existing_email_same_name_logs_in_no_duplicate(db):
    # seed
    db.execute("INSERT INTO USER (name, email) VALUES (?, ?)",
               ("Bob", "bob@example.com"))
    # act
    status, user = authenticate(
        db, "Bob", "bob@example.com", confirm_on_mismatch=lambda a, b: True)
    assert status == "logged_in"
    assert user["name"] == "Bob"
    # ensure no duplicate
    rows = db.fetchall(
        "SELECT COUNT(*) AS c FROM USER WHERE email=?", ("bob@example.com",))
    assert rows[0]["c"] == 1


def test_existing_email_name_mismatch_declined_aborts(db):
    db.execute("INSERT INTO USER (name, email) VALUES (?, ?)",
               ("Carol", "c@example.com"))
    status, user = authenticate(
        db, "Karo", "c@example.com", confirm_on_mismatch=lambda a, b: False)
    assert status == "mismatch_declined"
    assert user is None
    # still single row
    rows = db.fetchall(
        "SELECT COUNT(*) AS c FROM USER WHERE email=?", ("c@example.com",))
    assert rows[0]["c"] == 1


def test_existing_email_name_mismatch_confirmed_logs_in(db):
    db.execute("INSERT INTO USER (name, email) VALUES (?, ?)",
               ("Dave", "d@example.com"))
    status, user = authenticate(
        db, "David", "d@example.com", confirm_on_mismatch=lambda a, b: True)
    assert status == "logged_in"
    assert user["name"] == "Dave"
    # still single row
    rows = db.fetchall(
        "SELECT COUNT(*) AS c FROM USER WHERE email=?", ("d@example.com",))
    assert rows[0]["c"] == 1


def test_invalid_input_no_write(db):
    status, user = authenticate(
        db, "", "bademail", confirm_on_mismatch=lambda a, b: True)
    assert status == "invalid_input"
    assert user is None
    rows = db.fetchall("SELECT COUNT(*) AS c FROM USER", ())
    assert rows[0]["c"] == 0
