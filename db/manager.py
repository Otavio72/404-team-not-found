import sqlite3
import logging
from pathlib import Path

log = logging.getLogger("TaskManager.DB")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")


class DatabaseManager:
    """
    SQLite helper with:
    - PRAGMA foreign_keys=ON
    - conn.row_factory=sqlite3.Row (dict-like rows)
    - safe execute/fetch helpers with logging
    """

    def __init__(self, db_path: str = "task_manager.db"):
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cur = self.conn.cursor()
            self.cur.execute("PRAGMA foreign_keys = ON;")
            log.info("Connected %s (foreign_keys=ON)",
                     Path(self.db_path).resolve())
        except Exception:
            log.exception("Failed to connect to database")
            raise

    # ---- schema/load ---------------------------------------------------------
    def run_schema_file(self, schema_file: str) -> None:
        """Execute full schema.sql file (idempotent CREATE TABLE IF NOT EXISTS)."""
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                sql = f.read()
            self.conn.executescript(sql)
            self.conn.commit()
            log.info("Schema applied from %s", schema_file)
        except Exception:
            log.exception("Failed to apply schema")
            raise

    # ---- generic helpers -----------------------------------------------------
    def execute(self, sql: str, params=()):
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
            return self.cur.lastrowid
        except Exception:
            log.exception("DB write failed: %s | params=%s", sql, params)
            raise

    def fetchall(self, sql: str, params=()):
        try:
            self.cur.execute(sql, params)
            return self.cur.fetchall()
        except Exception:
            log.exception("DB read failed: %s | params=%s", sql, params)
            raise

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def __del__(self):
        self.close()
