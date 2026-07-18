"""Read-only activity log."""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import ttk

from custom_item_forge.i18n import translate


class LogView(ttk.LabelFrame):
    def __init__(self, master: tk.Misc, *, locale: str = "en", height: int = 8) -> None:
        super().__init__(master, text=translate("panel.log", locale), style="Card.TLabelframe")
        self._locale = locale
        self.text = tk.Text(self, height=height, wrap="word", state="disabled", relief="flat")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate("panel.log", value))

    def append(self, level: str, message: str) -> None:
        line = f"{datetime.now():%H:%M:%S}  {level:<7}  {message.rstrip()}\n"
        self.text.configure(state="normal")
        self.text.insert("end", line)
        self.text.see("end")
        self.text.configure(state="disabled")

    def first_line(self, message: str) -> str:
        return message.splitlines()[0] if message else ""
