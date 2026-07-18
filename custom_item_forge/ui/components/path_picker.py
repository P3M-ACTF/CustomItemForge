"""Reusable path entry with browse button."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable

from custom_item_forge.i18n import translate


class PathPicker(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        browse_mode: str = "file",
        on_change: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master)
        self._locale = locale
        self._browse_mode = browse_mode
        self._on_change = on_change
        self.variable = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.variable)
        self.entry.pack(side="left", fill="x", expand=True)
        self.browse_btn = ttk.Button(
            self,
            text=translate("menu.browse", locale),
            command=self._browse,
        )
        self.browse_btn.pack(side="left", padx=(8, 0))

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.browse_btn.configure(text=translate("menu.browse", value))

    def get(self) -> str:
        return self.variable.get()

    def set(self, value: str) -> None:
        self.variable.set(value)

    def _browse(self) -> None:
        selected = None
        if self._browse_mode == "folder_or_file":
            selected = filedialog.askdirectory(title=translate("dialog.open_folder", self._locale))
            if not selected:
                selected = filedialog.askopenfilename(
                    title=translate("dialog.open_title", self._locale),
                    filetypes=[
                        (translate("dialog.filter_all", self._locale), "*.vroidcustomitem *.vroid"),
                        ("All files", "*.*"),
                    ],
                )
        elif self._browse_mode == "file":
            selected = filedialog.askopenfilename(
                title=translate("dialog.open_title", self._locale),
                filetypes=[
                    (translate("dialog.filter", self._locale), "*.vroidcustomitem"),
                    ("All files", "*.*"),
                ],
            )
        if selected:
            self.variable.set(selected)
            if self._on_change:
                self._on_change()

    def pick_save_as(self, suggested: str = "changed-item.vroidcustomitem") -> None:
        current = self.variable.get().strip()
        initialfile = suggested
        initialdir = None
        if current:
            path = __import__("pathlib").Path(current)
            if path.name:
                initialfile = path.name
            if path.parent != __import__("pathlib").Path("."):
                initialdir = str(path.parent)
        selected = filedialog.asksaveasfilename(
            title=translate("dialog.save_title", self._locale),
            defaultextension=".vroidcustomitem",
            initialfile=initialfile,
            initialdir=initialdir,
            filetypes=[
                (translate("dialog.filter", self._locale), "*.vroidcustomitem"),
                ("All files", "*.*"),
            ],
        )
        if selected:
            self.variable.set(selected)
