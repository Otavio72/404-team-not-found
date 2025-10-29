import tkinter as tk
import ttkbootstrap as ttk

if __name__ == "__main__":
    app = ttk.Window(themename="superhero")
    app.title("Task Manager")
    app.geometry("900x600")
    ttk.Label(app, text="Hello from ttkbootstrap").pack(pady=40)
    app.mainloop()
