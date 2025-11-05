from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger("TaskManager.Session")


class SessionManager:
    """
    Persist/retrieve a single logged-in user_id in a plaintext file.
    - File format: just the user_id as an integer string, e.g. "42\n"
    - Corrupt/missing/empty file -> returns None (caller should show Login screen)
    - `clear()` removes the file (logout)
    """

    def __init__(self, session_file: str | Path = "session.txt"):
        self.session_path = Path(session_file)

    def save(self, user_id: int) -> None:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive int")
        self.session_path.write_text(f"{user_id}\n", encoding="utf-8")
        log.info("Session saved for user_id=%s at %s",
                 user_id, self.session_path.resolve())

    def load(self) -> Optional[int]:
        """
        Returns the user_id from disk if present and looks like a positive int.
        Otherwise returns None.
        """
        try:
            if not self.session_path.exists():
                return None
            raw = self.session_path.read_text(encoding="utf-8").strip()
            if not raw:
                return None
            user_id = int(raw)
            if user_id <= 0:
                return None
            return user_id
        except Exception:
            # Any parsing/IO error -> treat as no session (safe fallback)
            log.warning(
                "Invalid session file; ignoring and falling back to login.", exc_info=True)
            return None

    def clear(self) -> None:
        try:
            if self.session_path.exists():
                self.session_path.unlink()
                log.info("Session cleared (%s removed).",
                         self.session_path.resolve())
        except Exception:
            # Don't raise on logout cleanup failure
            log.warning("Failed to remove session file %s",
                        self.session_path, exc_info=True)
