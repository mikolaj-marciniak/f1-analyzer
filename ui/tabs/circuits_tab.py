import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from ui.widgets.list_panel import ListPanel

from stats.circuits import (
    get_circuits,
    get_circuits_by_season,
    get_circuit_data,
    get_best_driver_on_circuit,
    get_best_team_on_circuit,
    get_most_gained_positions_on_circuit,
)

class CircuitsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        self.circuit_ids: list[int] = []

        self._build_ui()

    def set_seasons(self, seasons: list[int]) -> None:
        self.left.set_seasons(seasons)

    def refresh(self) -> None:
        """Reset filters + clear details + reload list."""
        self.left.reset_filters()
        self._reset_details()
        self._load_list()

    def _build_ui(self) -> None:
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self.left = ListPanel(container, "Tory", list_width=35, list_height=20)
        self.left.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        self.left.bind_select(self._on_selected)
        self.left.bind_season_change(lambda e: self._load_list())
        self.left.set_on_sort_changed(lambda asc: self._load_list())

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        self.lbl_circuit_name = ttk.Label(right, text="Wybierz tor", font=("Segoe UI", 16, "bold"))
        self.lbl_circuit_name.grid(row=0, column=0, sticky="w")

        self.lbl_circuit_location = ttk.Label(
            right, text="Kliknij tor po lewej, żeby zobaczyć szczegóły."
        )
        self.lbl_circuit_location.grid(row=1, column=0, sticky="w", pady=(4, 12))

        ttk.Separator(right, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=(0, 12))

        stats = ttk.Frame(right)
        stats.grid(row=3, column=0, sticky="nsew")
        stats.columnconfigure(1, weight=1)

        ttk.Label(stats, text="Statystyki", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        ttk.Label(stats, text="Najlepszy kierowca (avg pozycja):").grid(
            row=1, column=0, sticky="w", padx=(0, 10)
        )
        self.lbl_best_driver = ttk.Label(stats, text="—")
        self.lbl_best_driver.grid(row=1, column=1, sticky="w")

        ttk.Label(stats, text="Najlepszy zespół (avg pozycja):").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=(6, 0)
        )
        self.lbl_best_team = ttk.Label(stats, text="—")
        self.lbl_best_team.grid(row=2, column=1, sticky="w", pady=(6, 0))

        ttk.Label(stats, text="Największy zysk pozycji:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=(6, 0)
        )
        self.lbl_best_gain = ttk.Label(stats, text="—")
        self.lbl_best_gain.grid(row=3, column=1, sticky="w", pady=(6, 0))

        self._load_list()

    def _load_list(self) -> None:
        season = self.left.get_selected_season()
        asc = self.left.sort_ascending

        try:
            if season is None:
                df = get_circuits(ascending=asc)
            else:
                df = get_circuits_by_season(season, ascending=asc)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać listy torów:\n{e}")
            return

        self.circuit_ids = df["_id"].tolist() if not df.empty else []
        names = df["name"].tolist() if not df.empty else []
        self.left.set_items(names)

    def _on_selected(self, event: tk.Event) -> None:
        idx = self.left.get_selected_index()
        if idx is None:
            return
        if idx >= len(self.circuit_ids):
            return

        circuit_id = self.circuit_ids[idx]

        try:
            df_c = get_circuit_data(circuit_id)
            df_best_driver = get_best_driver_on_circuit(circuit_id)
            df_best_team = get_best_team_on_circuit(circuit_id)
            df_gain = get_most_gained_positions_on_circuit(circuit_id)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych toru:\n{e}")
            return

        if df_c.empty:
            self._reset_details()
            self.lbl_circuit_name.configure(text="Nie znaleziono toru")
            return

        c = df_c.iloc[0]
        self.lbl_circuit_name.configure(text=str(c["name"]))
        self.lbl_circuit_location.configure(text=f"{c['location']}, {c['country']}")

        if df_best_driver.empty:
            self.lbl_best_driver.configure(text="brak danych")
        else:
            bd = df_best_driver.iloc[0]
            self.lbl_best_driver.configure(text=f"{bd['name']} {bd['family_name']} (avg: {bd['mean_pos']:.2f})")

        if df_best_team.empty:
            self.lbl_best_team.configure(text="brak danych")
        else:
            bt = df_best_team.iloc[0]
            self.lbl_best_team.configure(text=f"{bt['name']} (avg: {bt['mean_pos']:.2f})")

        if df_gain.empty:
            self.lbl_best_gain.configure(text="brak danych")
        else:
            g = df_gain.iloc[0]
            diff = int(g["diff"])
            diff_txt = f"+{diff}" if diff > 0 else str(diff)
            self.lbl_best_gain.configure(text=f"{g['name']} {g['family_name']} ({diff_txt})")

    def _reset_details(self) -> None:
        self.lbl_circuit_name.configure(text="Wybierz tor")
        self.lbl_circuit_location.configure(text="Kliknij tor po lewej, żeby zobaczyć szczegóły.")
        self.lbl_best_driver.configure(text="—")
        self.lbl_best_team.configure(text="—")
        self.lbl_best_gain.configure(text="—")