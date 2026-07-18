"""Two-column details panel grouped by section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import InspectReport
from custom_item_forge.i18n import section_title, translate


class DetailsPanel(ttk.LabelFrame):
    def __init__(self, master: tk.Misc, *, locale: str = "en") -> None:
        super().__init__(master, text=translate("panel.details", locale), style="Card.TLabelframe")
        self._locale = locale
        self.text = tk.Text(self, wrap="word", state="disabled", relief="flat", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.text.tag_configure("section", font=("Segoe UI", 10, "bold"))
        self.text.tag_configure("field", foreground="#333")

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate("panel.details", value))

    def show_report(self, report: InspectReport | None) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        if report is None:
            self.text.configure(state="disabled")
            return

        for section in report.sections:
            self.text.insert("end", f"{section_title(section.id, self._locale).upper()}\n", "section")
            for field in section.fields:
                label = translate(field.label_key or field.key, self._locale)
                self.text.insert("end", f"{label}\n", "field")
                self.text.insert("end", f"{field.value}\n\n")
        self.text.configure(state="disabled")
