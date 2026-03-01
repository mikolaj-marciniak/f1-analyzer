import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from ui.widgets.list_panel import ListPanel

from stats.teams import (
    get_teams,
    get_teams_by_season,
    get_team_data,
    get_best_circuit_of_team,
    get_most_gained_positions_by_team,
)

class TeamsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        self.team_ids: list[int] = []

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

        self.left = ListPanel(container, "Zespoły", list_width=35, list_height=20)
        self.left.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        self.left.bind_select(self._on_selected)
        self.left.bind_season_change(lambda e: self._load_list())
        self.left.set_on_sort_changed(lambda asc: self._load_list())

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        self.lbl_team_name = ttk.Label(right, text="Wybierz zespół", font=("Segoe UI", 16, "bold"))
        self.lbl_team_name.grid(row=0, column=0, sticky="w")

        self.lbl_team_info = ttk.Label(right, text="Kliknij zespół po lewej, żeby zobaczyć szczegóły.")
        self.lbl_team_info.grid(row=1, column=0, sticky="w", pady=(4, 12))

        ttk.Separator(right, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=(0, 12))

        stats = ttk.Frame(right)
        stats.grid(row=3, column=0, sticky="nsew")
        stats.columnconfigure(1, weight=1)

        ttk.Label(stats, text="Statystyki", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        ttk.Label(stats, text="Najlepszy tor (avg pozycja):").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.lbl_team_best_circuit = ttk.Label(stats, text="—")
        self.lbl_team_best_circuit.grid(row=1, column=1, sticky="w")

        ttk.Label(stats, text="Największy zysk pozycji:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=(6, 0)
        )
        self.lbl_team_best_gain = ttk.Label(stats, text="—")
        self.lbl_team_best_gain.grid(row=2, column=1, sticky="w", pady=(6, 0))

        self._load_list()

    def _load_list(self) -> None:
        season = self.left.get_selected_season()
        asc = self.left.sort_ascending

        try:
            if season is None:
                df = get_teams(ascending=asc)
            else:
                df = get_teams_by_season(season, ascending=asc)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać listy zespołów:\n{e}")
            return

        self.team_ids = df["_id"].tolist() if not df.empty else []
        names = df["name"].tolist() if not df.empty else []
        self.left.set_items(names)

    def _on_selected(self, event: tk.Event) -> None:
        idx = self.left.get_selected_index()
        if idx is None:
            return
        if idx >= len(self.team_ids):
            return

        team_id = self.team_ids[idx]

        try:
            df_t = get_team_data(team_id)
            df_best_circuit = get_best_circuit_of_team(team_id)
            df_gain = get_most_gained_positions_by_team(team_id)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych zespołu:\n{e}")
            return

        if df_t.empty:
            self._reset_details()
            self.lbl_team_name.configure(text="Nie znaleziono zespołu")
            self.lbl_team_info.configure(text="")
            return

        t = df_t.iloc[0]
        self.lbl_team_name.configure(text=str(t["name"]))

        info_parts = []
        if pd.notna(t.get("nationality")):
            info_parts.append(str(t["nationality"]))
        self.lbl_team_info.configure(text=" | ".join(info_parts) if info_parts else "")

        if df_best_circuit.empty:
            self.lbl_team_best_circuit.configure(text="brak danych")
        else:
            bc = df_best_circuit.iloc[0]
            self.lbl_team_best_circuit.configure(text=f"{bc['name']} (avg: {bc['mean_pos']:.2f})")

        if df_gain.empty:
            self.lbl_team_best_gain.configure(text="brak danych")
        else:
            g = df_gain.iloc[0]
            diff = int(g["diff"])
            diff_txt = f"+{diff}" if diff > 0 else str(diff)
            self.lbl_team_best_gain.configure(text=diff_txt)

    def _reset_details(self) -> None:
        self.lbl_team_name.configure(text="Wybierz zespół")
        self.lbl_team_info.configure(text="Kliknij zespół po lewej, żeby zobaczyć szczegóły.")
        self.lbl_team_best_circuit.configure(text="—")
        self.lbl_team_best_gain.configure(text="—")