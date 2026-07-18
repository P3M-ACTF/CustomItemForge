"""Collapsible accordion section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class CollapsibleSection(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        title: str,
        *,
        expanded: bool = True,
        padding: tuple[int, int] = (0, 6),
    ) -> None:
        super().__init__(master)
        self._title = title
        self._expanded = expanded
        self._padding = padding

        self.header = ttk.Frame(self)
        self.header.pack(fill="x")
        self.toggle_btn = ttk.Button(
            self.header,
            text=self._button_text(),
            style="Section.TButton",
            command=self.toggle,
        )
        self.toggle_btn.pack(anchor="w")

        self.body = ttk.Frame(self, padding=(10, 4, 0, 0))
        if expanded:
            self.body.pack(fill="x")

    @property
    def expanded(self) -> bool:
        return self._expanded

    def _button_text(self) -> str:
        arrow = "▾" if self._expanded else "▸"
        return f"{arrow}  {self._title}"

    def set_title(self, title: str) -> None:
        self._title = title
        self.toggle_btn.configure(text=self._button_text())

    def expand(self) -> None:
        if self._expanded:
            return
        self._expanded = True
        self.toggle_btn.configure(text=self._button_text())
        self.body.pack(fill="x")

    def collapse(self) -> None:
        if not self._expanded:
            return
        self._expanded = False
        self.toggle_btn.configure(text=self._button_text())
        self.body.pack_forget()

    def toggle(self) -> None:
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()
