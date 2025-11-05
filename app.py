# app.py
from pathlib import Path
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES
from ui.welcome import WelcomeScreen


def main():
    app = ttk.Window(themename="superhero")
    app.title("Task Manager")
    app.geometry("900x600")

    base = Path(__file__).resolve().parent
    db_path = base / "task_manager.db"
    schema_path = base / "db" / "schema.sql"   # <-- FIXED

    screen = WelcomeScreen(
        app,
        db_path=str(db_path),
        schema_path=str(schema_path),
        on_login=lambda user: print(
            f"[OK] logged in as id={user['id']} email={user['email']}"),
    )
    screen.pack(fill=BOTH, expand=YES)
    app.mainloop()


if __name__ == "__main__":
    main()
