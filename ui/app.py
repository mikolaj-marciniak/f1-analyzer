# ui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from etl.pipeline import full_data_reload, partial_reload

from stats.general import get_seasons

from ui.widgets.loading import LoadingWindow
from ui.tabs.circuits_tab import CircuitsTab
from ui.tabs.drivers_tab import DriversTab
from ui.tabs.teams_tab import TeamsTab

import traceback


def run_app() -> None:
    app = F1App()
    app.mainloop()


class F1App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("F1 Analyzer")
        self.geometry("900x600")
        self.minsize(700, 450)

        self.loading = LoadingWindow(self)

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(side="left", fill="both", expand=True)

        self.controls_frame = ttk.Frame(root, padding=(10, 0))
        self.controls_frame.pack(side="right", fill="y")

        ttk.Button(
            self.controls_frame,
            text="Załaduj dane od nowa",
            command=self._on_full_reload,
        ).pack(pady=(0, 5), fill="x")

        ttk.Button(
            self.controls_frame,
            text="Odśwież dane",
            command=self._on_partial_reload,
        ).pack(pady=(0, 5), fill="x")

        self.tab_circuits = CircuitsTab(self.notebook)
        self.tab_drivers = DriversTab(self.notebook)
        self.tab_teams = TeamsTab(self.notebook)

        self.notebook.add(self.tab_circuits, text="Tory")
        self.notebook.add(self.tab_drivers, text="Kierowcy")
        self.notebook.add(self.tab_teams, text="Zespoły")

        self._load_seasons_into_tabs()

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _load_seasons_into_tabs(self) -> None:
        try:
            df = get_seasons()
            seasons = df["season"].tolist()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać listy sezonów:\n{e}")
            seasons = []

        self.tab_circuits.set_seasons(seasons)
        self.tab_drivers.set_seasons(seasons)
        self.tab_teams.set_seasons(seasons)

        self.tab_circuits.refresh()
        self.tab_drivers.refresh()
        self.tab_teams.refresh()

    def _on_tab_changed(self, event) -> None:
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self.tab_circuits.refresh()
        elif idx == 1:
            self.tab_drivers.refresh()
        elif idx == 2:
            self.tab_teams.refresh()

    def _on_full_reload(self) -> None:
        if not messagebox.askyesno(
            "Potwierdź",
            "Czy na pewno chcesz załadować dane od nowa? To potrwa kilka minut.",
        ):
            return

        self.loading.show()
        self.withdraw()

        def run_reload():
            try:
                full_data_reload()
                self.after(0, self._reload_complete_full)
            except Exception:
                tb = traceback.format_exc()
                self.after(0, lambda: self._reload_failed("pełnego przeładowania", tb))

        threading.Thread(target=run_reload, daemon=True).start()

    def _on_partial_reload(self) -> None:
        if not messagebox.askyesno(
            "Potwierdź",
            "Czy chcesz odświeżyć dane (dodać nowe sezony)?",
        ):
            return

        self.loading.show()
        self.withdraw()

        def run_reload():
            try:
                partial_reload()
                self.after(0, self._reload_complete_partial)
            except Exception as e:
                self.after(0, lambda: self._reload_failed("odświeżenia", str(e)))

        threading.Thread(target=run_reload, daemon=True).start()

    def _reload_complete_full(self) -> None:
        self.loading.hide()
        self.deiconify()
        self._refresh_all_data()
        messagebox.showinfo("Gotowe", "Baza danych została odświeżona.")

    def _reload_complete_partial(self) -> None:
        self.loading.hide()
        self.deiconify()
        self._refresh_all_data()
        messagebox.showinfo("Gotowe", "Dane zostały zaktualizowane.")

    def _reload_failed(self, what: str, error: str) -> None:
        self.loading.hide()
        self.deiconify()
        messagebox.showerror("Błąd", f"Nie udało się wykonać {what}:\n{error}")

    def _refresh_all_data(self) -> None:
        self._load_seasons_into_tabs()