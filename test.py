import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from stats.circuits import (
    get_circuits,
    get_circuit_data,
    get_best_driver_on_circuit,
    get_best_team_on_circuit,
    get_most_gained_positions_on_circuit,
)

from stats.drivers import (
    get_drivers,
    get_driver_data,
    get_best_circuit_of_driver,
    get_most_gained_positions_by_driver,
)


class F1App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("F1 Analyzer")
        self.geometry("900x600")
        self.minsize(700, 450)

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_circuits = ttk.Frame(self.notebook, padding=10)
        self.tab_drivers = ttk.Frame(self.notebook, padding=10)
        self.tab_teams = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_circuits, text="Tory")
        self.notebook.add(self.tab_drivers, text="Kierowcy")
        self.notebook.add(self.tab_teams, text="Zespoły")

        self._build_circuits_tab()
        self._build_drivers_tab()

        ttk.Label(self.tab_teams, text="Widok: Zespoły (wkrótce)").pack(anchor="w")

    # =========================
    # TORY
    # =========================
    def _build_circuits_tab(self):
        container = ttk.Frame(self.tab_circuits)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Tory").grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.circuits_listbox = tk.Listbox(left, height=20, activestyle="dotbox", width=35)
        self.circuits_listbox.grid(row=1, column=0, sticky="nsw")

        lb_scroll = ttk.Scrollbar(left, orient="vertical", command=self.circuits_listbox.yview)
        lb_scroll.grid(row=1, column=1, sticky="ns")
        self.circuits_listbox.configure(yscrollcommand=lb_scroll.set)

        self.circuits_listbox.bind("<<ListboxSelect>>", self.on_circuit_selected)

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        self.lbl_circuit_name = ttk.Label(right, text="Wybierz tor", font=("Segoe UI", 16, "bold"))
        self.lbl_circuit_name.grid(row=0, column=0, sticky="w")

        self.lbl_circuit_location = ttk.Label(right, text="Kliknij tor po lewej, żeby zobaczyć szczegóły.")
        self.lbl_circuit_location.grid(row=1, column=0, sticky="w", pady=(4, 12))

        ttk.Separator(right, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=(0, 12))

        stats = ttk.Frame(right)
        stats.grid(row=3, column=0, sticky="nsew")
        stats.columnconfigure(1, weight=1)

        ttk.Label(stats, text="Statystyki", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        ttk.Label(stats, text="Najlepszy kierowca (avg pozycja):").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.lbl_best_driver = ttk.Label(stats, text="—")
        self.lbl_best_driver.grid(row=1, column=1, sticky="w")

        ttk.Label(stats, text="Najlepszy zespół (avg pozycja):").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(6, 0))
        self.lbl_best_team = ttk.Label(stats, text="—")
        self.lbl_best_team.grid(row=2, column=1, sticky="w", pady=(6, 0))

        ttk.Label(stats, text="Największy zysk pozycji:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=(6, 0))
        self.lbl_best_gain = ttk.Label(stats, text="—")
        self.lbl_best_gain.grid(row=3, column=1, sticky="w", pady=(6, 0))

        self._load_circuits_list()

    def _load_circuits_list(self):
        try:
            df = get_circuits(ascending=True)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać listy torów:\n{e}")
            return

        self.circuits_listbox.delete(0, tk.END)
        self.circuit_ids = df["_id"].tolist()

        for name in df["name"].tolist():
            self.circuits_listbox.insert(tk.END, name)

    def on_circuit_selected(self, event):
        selection = self.circuits_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
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
            self.lbl_circuit_name.configure(text="Nie znaleziono toru")
            self.lbl_circuit_location.configure(text="")
            self.lbl_best_driver.configure(text="—")
            self.lbl_best_team.configure(text="—")
            self.lbl_best_gain.configure(text="—")
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

    # =========================
    # KIEROWCY
    # =========================
    def _build_drivers_tab(self):
        container = ttk.Frame(self.tab_drivers)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Kierowcy").grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.drivers_listbox = tk.Listbox(left, height=20, activestyle="dotbox", width=35)
        self.drivers_listbox.grid(row=1, column=0, sticky="nsw")

        lb_scroll = ttk.Scrollbar(left, orient="vertical", command=self.drivers_listbox.yview)
        lb_scroll.grid(row=1, column=1, sticky="ns")
        self.drivers_listbox.configure(yscrollcommand=lb_scroll.set)

        self.drivers_listbox.bind("<<ListboxSelect>>", self.on_driver_selected)

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        self.lbl_driver_name = ttk.Label(right, text="Wybierz kierowcę", font=("Segoe UI", 16, "bold"))
        self.lbl_driver_name.grid(row=0, column=0, sticky="w")

        self.lbl_driver_info = ttk.Label(right, text="Kliknij kierowcę po lewej, żeby zobaczyć szczegóły.")
        self.lbl_driver_info.grid(row=1, column=0, sticky="w", pady=(4, 12))

        ttk.Separator(right, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=(0, 12))

        stats = ttk.Frame(right)
        stats.grid(row=3, column=0, sticky="nsew")
        stats.columnconfigure(1, weight=1)

        ttk.Label(stats, text="Statystyki", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        ttk.Label(stats, text="Najlepszy tor (avg pozycja):").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.lbl_driver_best_circuit = ttk.Label(stats, text="—")
        self.lbl_driver_best_circuit.grid(row=1, column=1, sticky="w")

        ttk.Label(stats, text="Największy zysk pozycji:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(6, 0))
        self.lbl_driver_best_gain = ttk.Label(stats, text="—")
        self.lbl_driver_best_gain.grid(row=2, column=1, sticky="w", pady=(6, 0))

        self._load_drivers_list()

    def _load_drivers_list(self):
        try:
            df = get_drivers(ascending=True)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać listy kierowców:\n{e}")
            return

        self.drivers_listbox.delete(0, tk.END)
        self.driver_ids = df["_id"].tolist()

        # w listboxie: "Nazwisko Imię"
        for family, name in zip(df["family_name"].tolist(), df["name"].tolist()):
            self.drivers_listbox.insert(tk.END, f"{family} {name}")

    def on_driver_selected(self, event):
        selection = self.drivers_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        driver_id = self.driver_ids[idx]

        try:
            df_d = get_driver_data(driver_id)
            df_best_circuit = get_best_circuit_of_driver(driver_id)
            df_gain = get_most_gained_positions_by_driver(driver_id)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych kierowcy:\n{e}")
            return

        if df_d.empty:
            self.lbl_driver_name.configure(text="Nie znaleziono kierowcy")
            self.lbl_driver_info.configure(text="")
            self.lbl_driver_best_circuit.configure(text="—")
            self.lbl_driver_best_gain.configure(text="—")
            return

        d = df_d.iloc[0]
        self.lbl_driver_name.configure(text=f"{d['name']} {d['family_name']}")

        info_parts = []
        if pd.notna(d.get("nationality")):
            info_parts.append(str(d["nationality"]))
        if pd.notna(d.get("date_of_birth")):
            info_parts.append(str(d["date_of_birth"]))
        self.lbl_driver_info.configure(text=" | ".join(info_parts) if info_parts else "")

        if df_best_circuit.empty:
            self.lbl_driver_best_circuit.configure(text="brak danych")
        else:
            bc = df_best_circuit.iloc[0]
            self.lbl_driver_best_circuit.configure(text=f"{bc['name']} (avg: {bc['mean_pos']:.2f})")

        if df_gain.empty:
            self.lbl_driver_best_gain.configure(text="brak danych")
        else:
            g = df_gain.iloc[0]
            diff = int(g["diff"])
            diff_txt = f"+{diff}" if diff > 0 else str(diff)
            self.lbl_driver_best_gain.configure(text=diff_txt)


if __name__ == "__main__":
    app = F1App()
    app.mainloop()