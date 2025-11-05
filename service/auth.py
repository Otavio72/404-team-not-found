from typing import Callable, Optional
import sqlite3

# Status strings the caller can use to decide what to show in UI.
# - "created": new user inserted
# - "logged_in": existing user, name matched OR mismatch but user confirmed
# - "mismatch_declined": name mismatch and user declined to proceed
# - "invalid_input": name/email invalid (no DB writes)
# - "db_error": database error (no DB writes)


def authenticate(
    db,                      # DatabaseManager instance
    name: str,
    email: str,
    # (entered_name, saved_name) -> bool
    confirm_on_mismatch: Callable[[str, str], bool],
) -> tuple[str, Optional[sqlite3.Row]]:
    name = (name or "").strip()
    email = (email or "").strip()

    if not name or not email or "@" not in email or email.startswith("@") or email.endswith("@"):
        return "invalid_input", None

    rows = db.fetchall(
        "SELECT id, name, email FROM USER WHERE email=? LIMIT 1", (email,))
    user = rows[0] if rows else None

    # Existing email
    if user:
        saved_name = (user["name"] or "").strip()
        if name != saved_name:
            # Ask the caller (UI or test) whether to proceed as saved_name
            if not confirm_on_mismatch(name, saved_name):
                return "mismatch_declined", None
            # proceed as the saved user
            return "logged_in", user
        # names match
        return "logged_in", user

    # New email -> create user
    try:
        db.execute("INSERT INTO USER (name, email) VALUES (?, ?)", (name, email))
        rows = db.fetchall(
            "SELECT id, name, email FROM USER WHERE email=? LIMIT 1", (email,))
        return "created", rows[0] if rows else None
    except sqlite3.IntegrityError:
        # Race: someone inserted concurrently. Treat as existing and log in.
        rows = db.fetchall(
            "SELECT id, name, email FROM USER WHERE email=? LIMIT 1", (email,))
        return "logged_in", rows[0] if rows else None
    except Exception:
        return "db_error", None
