import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, List, Optional

class ListPanel(ttk.Frame):
    def __init__(
        self,
        parent,
        title: str,
        *,
        enable_season: bool = True,
        enable_sort: bool = True,
        list_width: int = 35,
        list_height: int = 20,
    ):
        super().__init__(parent)

        self.enable_season = enable_season
        self.enable_sort = enable_sort

        self.sort_ascending = True

        ttk.Label(self, text=title).grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.filter_frame = ttk.Frame(self)
        self.filter_frame.grid(row=1, column=0, sticky="we", pady=(0, 0))
        self.filter_frame.columnconfigure(1, weight=1)

        self.season_var = tk.StringVar(value="")

        if self.enable_season:
            ttk.Label(self.filter_frame, text="Sezon:").grid(row=0, column=0, sticky="w")
            self.season_cb = ttk.Combobox(
                self.filter_frame,
                textvariable=self.season_var,
                state="readonly",
                width=10,
            )
            self.season_cb.grid(row=0, column=1, sticky="w", padx=2)
        else:
            self.season_cb = None

        if self.enable_sort:
            self.sort_btn = ttk.Button(self.filter_frame, text="↑", width=2, command=self._toggle_sort)
            self.sort_btn.grid(row=0, column=2, padx=0)
        else:
            self.sort_btn = None

        self.listbox = tk.Listbox(self, height=list_height, activestyle="dotbox", width=list_width)
        self.listbox.grid(row=2, column=0, sticky="nsw")

        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.scroll.grid(row=2, column=1, sticky="ns")

        self.listbox.configure(yscrollcommand=self.scroll.set)

        self._on_sort_changed: Optional[Callable[[bool], None]] = None

    def set_seasons(self, seasons: Iterable[int]) -> None:
        if not self.enable_season or self.season_cb is None:
            return
        values = [""] + [str(s) for s in seasons]
        self.season_cb["values"] = values

    def get_selected_season(self) -> Optional[int]:
        txt = self.season_var.get().strip()
        if not txt:
            return None
        try:
            return int(txt)
        except ValueError:
            return None

    def reset_filters(self) -> None:
        self.season_var.set("")
        self.set_sort(True)

    def set_sort(self, ascending: bool) -> None:
        self.sort_ascending = bool(ascending)
        if self.sort_btn is not None:
            self.sort_btn.configure(text="↑" if self.sort_ascending else "↓")

    def set_items(self, items: List[str]) -> None:
        self.listbox.delete(0, tk.END)
        for it in items:
            self.listbox.insert(tk.END, it)

    def clear_items(self) -> None:
        self.listbox.delete(0, tk.END)

    def get_selected_index(self) -> Optional[int]:
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def bind_select(self, handler: Callable[[tk.Event], None]) -> None:
        self.listbox.bind("<<ListboxSelect>>", handler)

    def bind_season_change(self, handler: Callable[[tk.Event], None]) -> None:
        if self.season_cb is None:
            return
        self.season_cb.bind("<<ComboboxSelected>>", handler)

    def set_on_sort_changed(self, callback: Callable[[bool], None]) -> None:
        """Set callback invoked after sort order changes. Arg is ascending bool."""
        self._on_sort_changed = callback

    def _toggle_sort(self) -> None:
        self.sort_ascending = not self.sort_ascending
        if self.sort_btn is not None:
            self.sort_btn.configure(text="↑" if self.sort_ascending else "↓")
        if self._on_sort_changed is not None:
            self._on_sort_changed(self.sort_ascending)