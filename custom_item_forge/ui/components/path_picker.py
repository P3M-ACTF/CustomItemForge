"""Reusable path entry with browse button."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable

from custom_item_forge.i18n import translate
from custom_item_forge.ui.utils.tooltip import ToolTip


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
        self.variable.trace_add("write", self._maybe_notify)
        self._tooltip = ToolTip(self, "")

        entry_frame = ttk.Frame(self)
        entry_frame.pack(side="left", fill="x", expand=True)
        xscroll = ttk.Scrollbar(entry_frame, orient="horizontal")
        self.entry = ttk.Entry(entry_frame, textvariable=self.variable, xscrollcommand=xscroll.set)
        self.entry.pack(side="top", fill="x", expand=True)
        xscroll.pack(side="bottom", fill="x")
        xscroll.configure(command=self.entry.xview)
        self.browse_btn = ttk.Button(
            self,
            text=translate("menu.browse", locale),
            command=self._browse,
        )
        self.browse_btn.pack(side="left", padx=(6, 0))
        self.entry.bind("<Return>", self._submit)
        self._update_tooltip()

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
        self._update_tooltip()

    def _update_tooltip(self) -> None:
        self._tooltip.set_text(self.variable.get())

    def _maybe_notify(self, *_args: object) -> None:
        self._update_tooltip()

    def _submit(self, _event: object | None = None) -> None:
        if self._on_change:
            self._on_change()

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
            if self._on_change:
                self._on_change()
