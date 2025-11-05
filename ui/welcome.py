from pathlib import Path
import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

from db.manager import DatabaseManager


class WelcomeScreen(ttk.Frame):
    """
    Centered 'Welcome' card with name/email inputs and a Login/Register button.

    Args:
        master: parent window
        db_path (str): sqlite file path
        schema_path (str): path to schema.sql
        on_login (callable|None): callback receiving the logged-in sqlite3.Row
    """

    def __init__(self, master, db_path: str, schema_path: str, on_login=None):
        super().__init__(master)
        self.on_login = on_login

        # ---- DB init --------------------------------------------------------
        self.db = DatabaseManager(db_path)
        self.db.run_schema_file(schema_path)

        # ---- Centered card --------------------------------------------------
        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        card = ttk.Frame(wrapper, padding=30, bootstyle="secondary")
        card.grid(row=0, column=0, sticky=NSEW)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Welcome!", font=("-size", 14, "-weight", "bold")).grid(
            row=0, column=0, pady=(0, 16)
        )

        # Name
        self.name_var = ttk.StringVar()
        ttk.Label(card, text="Name:").grid(row=1, column=0, sticky=W)
        self.name_entry = ttk.Entry(card, textvariable=self.name_var, width=44)
        self.name_entry.grid(row=2, column=0, sticky=EW, pady=(4, 12))

        # Email
        self.email_var = ttk.StringVar()
        ttk.Label(card, text="Email:").grid(row=3, column=0, sticky=W)
        self.email_entry = ttk.Entry(
            card, textvariable=self.email_var, width=44)
        self.email_entry.grid(row=4, column=0, sticky=EW, pady=(4, 16))

        # Action
        self.submit_btn = ttk.Button(
            card, text="Login / Register", bootstyle=SUCCESS, command=self.on_submit
        )
        self.submit_btn.grid(row=5, column=0, sticky=EW)

        self.name_entry.focus_set()

    # ---- DB helpers ---------------------------------------------------------
    def _get_user_by_email(self, email: str):
        rows = self.db.fetchall(
            "SELECT id, name, email FROM USER WHERE email=? LIMIT 1", (email,)
        )
        return rows[0] if rows else None

    def _create_user(self, name: str, email: str):
        return self.db.execute(
            "INSERT INTO USER (name, email) VALUES (?, ?)", (name, email)
        )

    # ---- UI events ----------------------------------------------------------
    def on_submit(self):
        name = (self.name_var.get() or "").strip()
        email = (self.email_var.get() or "").strip()

        # Validation
        if not name or not email:
            messagebox.showerror("Input Error", "Name and Email are required.")
            return
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            messagebox.showerror(
                "Input Error", "Please enter a valid email address.")
            return

        # Login or register
        user = self._get_user_by_email(email)
        if user:
            messagebox.showinfo(
                "Welcome back", f"Logged in as {user['name']} ({user['email']}).")
            if self.on_login:
                self.on_login(user)
            return

        try:
            user_id = self._create_user(name, email)
            # fetch the new row for callback consistency
            user = self._get_user_by_email(email)
        except sqlite3.IntegrityError:
            # UNIQUE(email) collision fallback
            user = self._get_user_by_email(
                email) or {"id": None, "name": name, "email": email}
            messagebox.showinfo(
                "Welcome back", f"Logged in as {user['name']} ({user['email']}).")
        except Exception as exc:
            messagebox.showerror(
                "Database Error", f"Could not create user.\n{exc}")
            return
        else:
            messagebox.showinfo(
                "Welcome!", f"Account created (ID: {user_id}). You're now logged in.")

        if self.on_login:
            self.on_login(user)
