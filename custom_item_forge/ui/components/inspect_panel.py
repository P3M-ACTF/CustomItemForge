"""Three-section inspect panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import InspectReport
from custom_item_forge.i18n import section_title, translate


class InspectPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, *, locale: str = "en") -> None:
        super().__init__(master)
        self._locale = locale
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)
        self._trees: dict[str, ttk.Treeview] = {}
        for section_id in ("vroid", "vroidcustomitem", "file"):
            frame = ttk.Frame(self._notebook, padding=8)
            self._notebook.add(frame, text=section_title(section_id, locale))
            tree = ttk.Treeview(
                frame,
                columns=("value",),
                show="headings",
                height=12,
            )
            tree.heading("value", text="Value")
            tree.column("value", width=480, stretch=True)
            tree.pack(fill="both", expand=True, side="left")
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
            self._trees[section_id] = tree

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        for index, section_id in enumerate(("vroid", "vroidcustomitem", "file")):
            self._notebook.tab(index, text=section_title(section_id, value))

    def show_report(self, report: InspectReport | None) -> None:
        for section_id, tree in self._trees.items():
            tree.delete(*tree.get_children())
            if report is None:
                continue
            section = report.section(section_id)
            if section is None:
                continue
            for field in section.fields:
                label = translate(field.label_key or field.key, self._locale)
                tree.insert("", "end", values=(f"{label}: {field.value}",))
