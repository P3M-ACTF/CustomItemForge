"""Folder/file browser with item list."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from custom_item_forge.i18n import translate
from custom_item_forge.ui.components.path_picker import PathPicker


class FileListPanel(ttk.LabelFrame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        on_select: Callable[[Path], None] | None = None,
        on_open: Callable[[], None] | None = None,
        on_validate: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, text=translate("panel.files", locale), style="Card.TLabelframe")
        self._locale = locale
        self._on_select = on_select
        self._on_open = on_open
        self._on_validate = on_validate
        self._paths: list[Path] = []

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 6))
        self.path_picker = PathPicker(bar, locale=locale, browse_mode="folder_or_file", on_change=self._trigger_open)
        self.path_picker.pack(side="left", fill="x", expand=True)
        self.validate_btn = ttk.Button(
            bar,
            text=translate("menu.validate", locale),
            command=self._trigger_validate,
        )
        self.validate_btn.pack(side="left", padx=(6, 0))

        self.listbox = tk.Listbox(self, width=28, exportselection=False)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_list_select)

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate("panel.files", value))
        self.path_picker.locale = value
        self.validate_btn.configure(text=translate("menu.validate", value))

    def source_path(self) -> str:
        return self.path_picker.get()

    def set_items(self, paths: list[Path], *, select_first: bool = True) -> None:
        self._paths = paths
        self.listbox.delete(0, "end")
        for item in paths:
            self.listbox.insert("end", item.name)
        if select_first and paths:
            self.listbox.selection_set(0)
            self._emit_selection(0)

    def selected_path(self) -> Path | None:
        selection = self.listbox.curselection()
        if not selection:
            return None
        return self._paths[selection[0]]

    def _trigger_open(self) -> None:
        if self._on_open:
            self._on_open()

    def _trigger_validate(self) -> None:
        if self._on_validate:
            self._on_validate()

    def _on_list_select(self, _event: object | None = None) -> None:
        selection = self.listbox.curselection()
        if selection:
            self._emit_selection(selection[0])

    def _emit_selection(self, index: int) -> None:
        if self._on_select and 0 <= index < len(self._paths):
            self._on_select(self._paths[index])
