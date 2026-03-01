# ui/widgets/loading.py
import tkinter as tk
from tkinter import ttk


class LoadingWindow:
    def __init__(self, parent: tk.Tk, title: str = "Ładowanie"):
        self.parent = parent
        self.title = title
        self._win: tk.Toplevel | None = None

        self._lbl_main = None
        self._lbl_sub = None
        self._bar = None

    def show(self, message: str = "Ładowanie danych...", submessage: str = "Proszę czekać") -> None:
        """Create (if needed) and show the loading window."""
        if self._win is not None and self._win.winfo_exists():
            self._lbl_main.configure(text=message)
            self._lbl_sub.configure(text=submessage)
            self._win.deiconify()
            self._win.lift()
            self._win.focus_force()
            self._win.update_idletasks()
            return

        win = tk.Toplevel(self.parent)
        win.title(self.title)
        win.geometry("300x110")
        win.resizable(False, False)

        # NIE ustawiamy transient – bo parent może być ukrywany/disabled
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", lambda: None)

        frame = ttk.Frame(win, padding=20)
        frame.pack(fill="both", expand=True)

        self._lbl_main = ttk.Label(frame, text=message, font=("Segoe UI", 12))
        self._lbl_main.pack(pady=(0, 6))

        self._lbl_sub = ttk.Label(frame, text=submessage, font=("Segoe UI", 10))
        self._lbl_sub.pack()

        self._bar = ttk.Progressbar(frame, mode="indeterminate")
        self._bar.pack(fill="x", pady=(10, 0))
        self._bar.start(12)

        self._win = win
        self._win.lift()
        self._win.focus_force()
        self._win.update_idletasks()

    def hide(self) -> None:
        """Hide and destroy the loading window."""
        if self._win is None:
            return
        if self._win.winfo_exists():
            try:
                self._bar.stop()
            except Exception:
                pass
            self._win.destroy()
        self._win = None