# 404-team-not-found

This application is a task manager for York University students to be able to register dates.

## PLANNER

**Project Docs**

- **Wiki**

  - [Wiki home](../../wiki)
  - [Design (wiki)](../../wiki/Design)
  - [Proposal (wiki)](../../wiki/proposal)

- **In-repo Drafts (reviewed via PRs)**
  - [Design: User Stories & Acceptance](docs/design/user-stories.md)
  - [Design: Architecture & Components](docs/design/Architecture.md)
  - [Design: Data & Content](docs/design/Data-content.md)
  - [Design: Risks & Constraints](docs/design/Risk-Constraints.md)

# Task Manager (Tkinter + ttkbootstrap)

A simple desktop **Task Manager** built with **Python 3.12.11**, **Tkinter**, **ttkbootstrap**, and **SQLite**.  
This guide helps you initialize the repository and get a runnable window quickly.

---

## Prerequisites

- **Python**: 3.12.11 (same as WorkSpace we use for lab)
- **Git**
- OS support: Windows, macOS, Linux (X11/Wayland)

> **Note**: `sqlite3` and `tkinter` are part of the CPython standard library. On some Linux distros you may need to install Tk bindings separately (see Troubleshooting).

---

## Quick Start

```bash
# 1) clone or create your repo
git clone <your-repo-url> task-manager
cd task-manager

# 2) add dependencies
echo ttkbootstrap==1.10.1 > requirements.txt
echo pyinstaller==6.8.0 > requirements.txt
pip install -r requirements.txt

# 3) run
python app.py
```

---

## Suggested Project Structure

```
.
├─ app.py               # entrypoint (will later contain the full app UI)
├─ requirements.txt     # pinned dependencies
└─ README.md            # this file
```

---

## Minimal `app.py`

Create `app.py` with the snippet below to verify your environment and ttkbootstrap theme rendering:

```python
import tkinter as tk
import ttkbootstrap as ttk

if __name__ == "__main__":
    app = ttk.Window(themename="superhero")
    app.title("Task Manager (smoke test)")
    app.geometry("900x600")
    ttk.Label(app, text="Hello from ttkbootstrap").pack(pady=40)
    app.mainloop()
```

Run:

```bash
python app.py
```

A window should appear with the text **Hello from ttkbootstrap**.

---

## Dependencies

Create `requirements.txt` (already covered above):

```
ttkbootstrap==1.10.1
pyinstaller==6.8.0
```

> `sqlite3` and `tkinter` come with Python. On Linux you may need: `sudo apt-get install python3-tk` (Debian/Ubuntu) or the equivalent for your distro.

---

## 🔧 Troubleshooting

- **tkinter not found (Linux):**  
  Install Tk bindings:

  - Debian/Ubuntu: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`

- **macOS app doesn’t show window / permission prompts:**  
  Ensure you’re using the **framework build** that ships with the official Python.org installer, or use Homebrew with Tk support:  
  `brew install python-tk` (or `brew reinstall python-tk` if needed).

- **Windows PowerShell execution policy blocks venv activation:**  
  Use `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in an elevated PowerShell (or run the `activate.bat` from `cmd.exe`).

- **Fonts or theme look odd on Wayland:**  
  Try running under XWayland or adjust compositor settings. ttkbootstrap uses standard Tk rendering.

---

## Environment Info

- **Python**: 3.12.11
- **OS**: Windows / macOS / Linux
- **UI Toolkit**: Tkinter + ttkbootstrap
- **pyinstaller**: Bundles a Python application and all its dependencies into a single package
- **DB**: SQLite (file-based, no server required)
