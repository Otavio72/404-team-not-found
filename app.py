import sys
from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES

from ui.task_manager import TaskManagerFrame
from ui.welcome import WelcomeScreen


def resource_path(rel: str) -> Path:
    """
    Resolve a resource path that works both in development and when bundled with PyInstaller.
    - In a PyInstaller onefile build, resources are extracted under sys._MEIPASS.
    - Otherwise, resolve relative to this file's directory.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent
    return base / rel


def main() -> None:
    # Main window acts as the "controller" for TaskManagerFrame (exposes .db, .logout, .title()).
    app = ttk.Window(themename="superhero")
    app.title("Task Manager")
    app.geometry("900x600")

    # Resolve resources for both dev and PyInstaller runtimes
    # created on first run if absent
    db_path = resource_path("task_manager.db")
    # bundled via --add-data in CI
    schema_path = resource_path("db/schema.sql")

    def logout() -> None:
        """Return to the Welcome screen (clear current user session if you add one later)."""
        app.title("Task Manager")
        show_welcome()

    def on_login(user_row) -> None:
        """
        Called by WelcomeScreen after a successful Login/Register.
        user_row is a sqlite3.Row with keys: id, name, email.
        """
        # Swap to TaskManagerFrame
        for w in app.winfo_children():
            w.destroy()
        # Ensure the controller exposes the API TaskManagerFrame expects
        app.logout = logout  # type: ignore[attr-defined]
        tm = TaskManagerFrame(app, app)  # (parent widget, controller = app)
        tm.set_user(user_row["id"])
        tm.pack(fill=BOTH, expand=YES)

    def show_welcome() -> None:
        """Show the Welcome screen and initialize the DatabaseManager."""
        for w in app.winfo_children():
            w.destroy()
        screen = WelcomeScreen(
            app,
            db_path=str(db_path),
            schema_path=str(schema_path),
            on_login=on_login,
        )
        # Expose DB handle on the controller (TaskManagerFrame expects controller.db)
        app.db = screen.db  # type: ignore[attr-defined]
        app.logout = logout  # type: ignore[attr-defined]
        screen.pack(fill=BOTH, expand=YES)

    # Initial screen
    show_welcome()
    app.mainloop()


if __name__ == "__main__":
    main()
