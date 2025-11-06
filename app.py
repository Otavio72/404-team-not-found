from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES

from ui.welcome import WelcomeScreen
from ui.task_manager import TaskManagerFrame  # <-- import the frame


def main():
    app = ttk.Window(themename="superhero")
    app.title("Task Manager")
    app.geometry("900x600")

    base = Path(__file__).resolve().parent
    db_path = base / "task_manager.db"
    schema_path = base / "db" / "schema.sql"

    def show_welcome():
        # Recreate the welcome screen and re-use the same DB file
        for w in app.winfo_children():
            w.destroy()
        screen = WelcomeScreen(
            app,
            db_path=str(db_path),
            schema_path=str(schema_path),
            on_login=on_login,  # re-use the same callback
        )
        # expose DB handle to controller after WelcomeScreen sets it up
        app.db = screen.db
        screen.pack(fill=BOTH, expand=YES)

    def logout():
        # Clear session state if you add one later, then go back to Welcome
        app.title("Task Manager")
        show_welcome()

    def on_login(user_row):
        # Make app act as the controller for TaskManagerFrame
        # Ensure app has .db and .logout the frame expects
        if not hasattr(app, "db"):
            # welcome screen created it; grab it if missing
            # (this line is usually unnecessary because we set app.db in show_welcome)
            app.db = screen.db  # type: ignore[name-defined]

        app.logout = logout  # attach controller API

        # Swap to TaskManagerFrame
        for w in app.winfo_children():
            w.destroy()
        tm = TaskManagerFrame(app, app)   # <-- pass (parent, controller)
        tm.set_user(user_row['id'])
        tm.pack(fill=BOTH, expand=YES)

    # initial screen
    show_welcome()
    app.mainloop()


if __name__ == "__main__":
    main()
