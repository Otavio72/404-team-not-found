from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES

from ui.task_manager import TaskManagerFrame
from ui.welcome import WelcomeScreen


def main():
    app = ttk.Window(themename="superhero")
    app.title("Task Manager")
    app.geometry("900x600")

    base = Path(__file__).resolve().parent
    db_path = base / "task_manager.db"
    schema_path = base / "db" / "schema.sql"

    def logout():
        app.title("Task Manager")
        show_welcome()

    def on_login(user_row):
        # app.db is set by show_welcome(); just switch screens
        for w in app.winfo_children():
            w.destroy()
        # Treat the main window as the controller (has .db, .logout, .title)
        app.logout = logout
        tm = TaskManagerFrame(app, app)
        tm.set_user(user_row["id"])
        tm.pack(fill=BOTH, expand=YES)

    def show_welcome():
        for w in app.winfo_children():
            w.destroy()
        screen = WelcomeScreen(
            app,
            db_path=str(db_path),
            schema_path=str(schema_path),
            on_login=on_login,
        )
        # expose DB handle to the controller
        app.db = screen.db  # type: ignore[attr-defined]
        app.logout = logout  # type: ignore[attr-defined]
        screen.pack(fill=BOTH, expand=YES)

    show_welcome()
    app.mainloop()


if __name__ == "__main__":
    main()
