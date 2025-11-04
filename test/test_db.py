import sqlite3
from pathlib import Path

import pytest

# Import your DatabaseManager
from db.manager import DatabaseManager

SCHEMA_TEXT = """
CREATE TABLE IF NOT EXISTS USER (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  name  TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS COURSE (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id     INTEGER,
  name        TEXT NOT NULL,
  description TEXT,
  FOREIGN KEY (user_id) REFERENCES USER (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TASK (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id   INTEGER,
  name        TEXT NOT NULL,
  description TEXT,
  due_date    TEXT,
  FOREIGN KEY (course_id) REFERENCES COURSE (id) ON DELETE CASCADE
);
"""


@pytest.fixture
def temp_db(tmp_path: Path):
    """Yield a DatabaseManager wired to a temp file DB, with schema applied."""
    db_file = tmp_path / "test.db"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text(SCHEMA_TEXT, encoding="utf-8")

    db = DatabaseManager(str(db_file))
    db.run_schema_file(str(schema_file))
    try:
        yield db
    finally:
        db.close()


def test_row_factory_is_dict_like(temp_db: DatabaseManager):
    user_id = temp_db.execute(
        "INSERT INTO USER(name, email) VALUES(?, ?)",
        ("Alice", "alice@example.com"),
    )

    row = temp_db.fetchall("SELECT * FROM USER WHERE id=?", (user_id,))[0]
    # sqlite3.Row behaves like a mapping
    assert row["name"] == "Alice"
    assert row["email"] == "alice@example.com"
    # Access by key should work; access by attribute should not
    with pytest.raises(AttributeError):
        _ = row.name  # type: ignore[attr-defined]


def test_unique_email_constraint(temp_db: DatabaseManager):
    temp_db.execute(
        "INSERT INTO USER(name, email) VALUES(?, ?)",
        ("Bob", "bob@example.com"),
    )
    with pytest.raises(sqlite3.IntegrityError):
        temp_db.execute(
            "INSERT INTO USER(name, email) VALUES(?, ?)",
            ("Bobby", "bob@example.com"),
        )


def test_foreign_keys_cascade_delete_course_tasks(temp_db: DatabaseManager):
    # Insert user → course → tasks
    user_id = temp_db.execute(
        "INSERT INTO USER(name, email) VALUES(?, ?)",
        ("Carol", "carol@example.com"),
    )
    course_id = temp_db.execute(
        "INSERT INTO COURSE(user_id, name, description) VALUES(?, ?, ?)",
        (user_id, "Math 101", "Intro"),
    )
    t1 = temp_db.execute(
        "INSERT INTO TASK(course_id, name, description, due_date) VALUES(?, ?, ?, ?)",
        (course_id, "HW1", "Limits", "2025-11-01"),
    )
    t2 = temp_db.execute(
        "INSERT INTO TASK(course_id, name, description, due_date) VALUES(?, ?, ?, ?)",
        (course_id, "Quiz1", "Derivatives", "2025-11-07"),
    )
    assert t1 and t2

    # Sanity check they exist
    tasks = temp_db.fetchall(
        "SELECT id FROM TASK WHERE course_id=?", (course_id,))
    assert len(tasks) == 2

    # Delete course -> tasks should cascade
    temp_db.execute("DELETE FROM COURSE WHERE id=?", (course_id,))
    tasks_after = temp_db.fetchall(
        "SELECT id FROM TASK WHERE course_id=?", (course_id,))
    assert tasks_after == []


def test_foreign_keys_prevent_orphan_course(temp_db: DatabaseManager):
    # Inserting a COURSE with a non-existent user should fail
    with pytest.raises(sqlite3.IntegrityError):
        temp_db.execute(
            "INSERT INTO COURSE(user_id, name, description) VALUES(?, ?, ?)",
            (999999, "Ghost Course", "Should fail"),
        )
