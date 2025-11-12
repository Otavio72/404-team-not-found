# ui/task_manager.py
import tkinter as tk
from tkinter import messagebox as Messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, X
from ttkbootstrap.dialogs.dialogs import Querybox

from ui.welcome import WelcomeScreen


class TaskManagerFrame(ttk.Frame):
    """Task Manager main UI (user-scoped)."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db              # expects DatabaseManager with fetchall/execute
        self.current_user_id = None
        style = ttk.Style(theme=WelcomeScreen.current_theme)

        # ---- Top Bar --------------------------------------------------------
        top = ttk.Frame(self, padding=(12, 12, 12, 0))
        top.pack(fill=X)
        self.user_label = ttk.Label(top, text="Welcome!", font=("-size", 12))
        self.user_label.pack(side=tk.LEFT)
        ttk.Button(top, text="Logout", bootstyle="danger", command=self.controller.logout) \
            .pack(side=tk.RIGHT)

        frameThemeButton = ttk.Frame(top)
        frameThemeButton.pack(side=tk.RIGHT, padx=10)


        def toggle_theme():
            current = style.theme_use()
            new_theme = "darkly" if current == "flatly" else "flatly"
            WelcomeScreen.current_theme = new_theme
            style.theme_use(new_theme)


        toggle_btn = ttk.Button(frameThemeButton, text="Toggle Light/Dark", command=toggle_theme)
        toggle_btn.grid(row=0, column=0, pady=20)

        # ---- Main Panes -----------------------------------------------------
        main = ttk.Frame(self, padding=12)
        main.pack(fill=BOTH, expand=True)



        panes = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
        panes.pack(fill=BOTH, expand=True)




        # Courses pane
        courses_pane = ttk.Labelframe(panes, text="Courses", padding=10)
        panes.add(courses_pane, weight=1)

        self.courses_list = tk.Listbox(
            courses_pane, exportselection=False, height=16)
        self.courses_list.pack(fill=BOTH, expand=True)
        self.courses_list.bind("<<ListboxSelect>>", self.on_course_select)

        cbar = ttk.Frame(courses_pane)
        cbar.pack(fill=X, pady=(8, 0))
        ttk.Button(cbar, text="Add", bootstyle="primary-outline", command=self.add_course) \
            .pack(side=tk.LEFT, expand=True, fill=X, padx=(0, 4))
        ttk.Button(cbar, text="Delete", bootstyle="danger-outline", command=self.delete_course) \
            .pack(side=tk.LEFT, expand=True, fill=X, padx=(4, 0))

        # Tasks pane
        tasks_pane = ttk.Labelframe(panes, text="Tasks", padding=10)
        panes.add(tasks_pane, weight=1)

        self.tasks_list = tk.Listbox(
            tasks_pane, exportselection=False, height=16)
        self.tasks_list.pack(fill=BOTH, expand=True)
        self.tasks_list.bind("<<ListboxSelect>>", self.on_task_select)

        tbar = ttk.Frame(tasks_pane)
        tbar.pack(fill=X, pady=(8, 0))
        self.btn_task_add = ttk.Button(
            tbar, text="Add", bootstyle="primary-outline",
            command=self.add_task, state="disabled"
        )
        self.btn_task_add.pack(side=tk.LEFT, expand=True, fill=X, padx=(0, 4))
        self.btn_task_del = ttk.Button(
            tbar, text="Delete", bootstyle="danger-outline",
            command=self.delete_task, state="disabled"
        )
        self.btn_task_del.pack(side=tk.LEFT, expand=True, fill=X, padx=(4, 0))

        # Details pane
        details_pane = ttk.Labelframe(panes, text="Details", padding=10)
        panes.add(details_pane, weight=2)

        ttk.Label(details_pane, text="Name:").pack(anchor="w")
        self.ent_name = ttk.Entry(details_pane)
        self.ent_name.pack(fill=X, pady=(4, 8))

        ttk.Label(details_pane, text="Description:").pack(anchor="w")
        self.txt_desc = tk.Text(details_pane, height=8)
        self.txt_desc.pack(fill=BOTH, expand=True, pady=(4, 8))

        ttk.Label(details_pane, text="Due Date (YYYY-MM-DD):").pack(anchor="w")
        self.ent_due = ttk.Entry(details_pane)
        self.ent_due.pack(fill=X, pady=(4, 8))

        self.btn_save = ttk.Button(
            details_pane, text="Save Changes",
            bootstyle="success", command=self.save_changes, state="disabled"
        )
        self.btn_save.pack(fill=X, pady=(4, 0))

        # in-memory index maps
        self._course_index_to_id = {}
        self._task_index_to_id = {}

    # ---- Public API ---------------------------------------------------------
    def set_user(self, user_id: int):
        """Called by App after login."""
        self.current_user_id = user_id
        rows = self.db.fetchall("SELECT name FROM USER WHERE id=?", (user_id,))
        name = rows[0]["name"] if rows else "User"
        self.user_label.configure(text=f"Welcome, {name}!")
        self.controller.title(f"Task Manager - {name}")
        self.refresh_all()

    # ---- UI refresh helpers -------------------------------------------------
    def refresh_all(self):
        self.load_courses()
        self.load_tasks(None)
        self.clear_details()
        self._update_button_states(course_selected=False, task_selected=False)

    def load_courses(self):
        self.courses_list.delete(0, tk.END)
        self._course_index_to_id.clear()
        if not self.current_user_id:
            return
        rows = self.db.fetchall(
            "SELECT id, name FROM COURSE WHERE user_id=? ORDER BY id DESC",
            (self.current_user_id,),
        )
        for i, row in enumerate(rows):
            self.courses_list.insert(tk.END, row["name"])
            self._course_index_to_id[i] = row["id"]

    def load_tasks(self, course_id):
        self.tasks_list.delete(0, tk.END)
        self._task_index_to_id.clear()
        if not course_id:
            return
        rows = self.db.fetchall(
            "SELECT id, name FROM TASK WHERE course_id=? ORDER BY id DESC",
            (course_id,),
        )
        for i, row in enumerate(rows):
            self.tasks_list.insert(tk.END, row["name"])
            self._task_index_to_id[i] = row["id"]

    def clear_details(self):
        self.ent_name.delete(0, tk.END)
        self.txt_desc.delete("1.0", tk.END)
        self.ent_due.delete(0, tk.END)

    def _selected_course_id(self):
        sel = self.courses_list.curselection()
        return self._course_index_to_id.get(sel[0]) if sel else None

    def _selected_task_id(self):
        sel = self.tasks_list.curselection()
        return self._task_index_to_id.get(sel[0]) if sel else None

    def _update_button_states(self, course_selected: bool, task_selected: bool):
        self.btn_task_add.configure(
            state=("normal" if course_selected else "disabled"))
        self.btn_task_del.configure(
            state=("normal" if task_selected else "disabled"))
        self.btn_save.configure(
            state=("normal" if (course_selected or task_selected) else "disabled"))
        # when only course is selected, due_date is disabled (course has no due date)
        self.ent_due.configure(
            state=("normal" if task_selected else "disabled"))

    # ---- Events -------------------------------------------------------------
    def on_course_select(self, _evt):
        cid = self._selected_course_id()
        self.clear_details()
        self.load_tasks(cid)
        self._update_button_states(
            course_selected=bool(cid), task_selected=False)

        if cid:
            rows = self.db.fetchall(
                "SELECT name, description FROM COURSE WHERE id=?", (cid,))
            if rows:
                self.ent_name.insert(0, rows[0]["name"])
                self.txt_desc.insert("1.0", rows[0]["description"] or "")

    def on_task_select(self, _evt):
        tid = self._selected_task_id()
        self._update_button_states(course_selected=bool(
            self._selected_course_id()), task_selected=bool(tid))
        self.clear_details()
        if tid:
            rows = self.db.fetchall(
                "SELECT name, description, due_date FROM TASK WHERE id=?", (
                    tid,)
            )
            if rows:
                self.ent_name.insert(0, rows[0]["name"])
                self.txt_desc.insert("1.0", rows[0]["description"] or "")
                self.ent_due.insert(0, rows[0]["due_date"] or "")

    # ---- Actions ------------------------------------------------------------
    def add_course(self):
        name = Querybox.get_string(
            prompt="Enter course name:", title="Add Course")
        if not name:
            return
        desc = Querybox.get_string(
            prompt="Enter course description (optional):", title="Add Course")
        self.db.execute(
            "INSERT INTO COURSE (user_id, name, description) VALUES (?, ?, ?)",
            (self.current_user_id, name.strip(), (desc or "").strip()),
        )
        self.load_courses()

    def delete_course(self):
        cid = self._selected_course_id()
        if not cid:
            return
        if Messagebox.askyesno(
            "Are you sure you want to delete this course and all its tasks?",
            "Confirm Delete",
            parent=self,
        ):
            self.db.execute("DELETE FROM COURSE WHERE id=?", (cid,))
            self.refresh_all()

    def add_task(self):
        cid = self._selected_course_id()
        if not cid:
            return
        name = Querybox.get_string(prompt="Enter task name:", title="Add Task")
        if not name:
            return
        desc = Querybox.get_string(
            prompt="Enter task description (optional):", title="Add Task Description")
        due = Querybox.get_string(
            prompt="Enter due date (YYYY-MM-DD):", title="Add Task Due Date")
        self.db.execute(
            "INSERT INTO TASK (course_id, name, description, due_date) VALUES (?, ?, ?, ?)",
            (cid, name.strip(), (desc or "").strip(), (due or "").strip()),
        )
        self.load_tasks(cid)

    def delete_task(self):
        tid = self._selected_task_id()
        if not tid:
            return
        if Messagebox.askyesno("Are you sure you want to delete this task?", "Confirm Delete", parent=self):
            self.db.execute("DELETE FROM TASK WHERE id=?", (tid,))
            # stay on the current course
            self.load_tasks(self._selected_course_id())
            self.clear_details()
            self._update_button_states(
                course_selected=True, task_selected=False)

    def save_changes(self):
        name = self.ent_name.get().strip()
        desc = self.txt_desc.get("1.0", tk.END).strip()
        due = self.ent_due.get().strip()
        if not name:
            Messagebox.show_error("Name cannot be empty.", "Error")
            return

        cid = self._selected_course_id()
        tid = self._selected_task_id()

        if tid:
            self.db.execute(
                "UPDATE TASK SET name=?, description=?, due_date=? WHERE id=?",
                (name, desc, due, tid),
            )
            self.load_tasks(cid)
        elif cid:
            self.db.execute(
                "UPDATE COURSE SET name=?, description=? WHERE id=?",
                (name, desc, cid),
            )
            self.load_courses()
            # reselect the course if still present (best-effort)
            for i in range(self.courses_list.size()):
                if self.courses_list.get(i) == name:
                    self.courses_list.selection_set(i)
                    break
            self.on_course_select(None)
