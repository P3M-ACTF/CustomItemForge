"""Large icon tab buttons."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from custom_item_forge.i18n import translate


class TabBar(ttk.Frame):
    _TABS = (
        ("inspect", "tab.inspect.icon"),
        ("change", "tab.change.icon"),
        ("combine", "tab.combine.icon"),
    )

    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        on_select: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(master)
        self._locale = locale
        self._on_select = on_select
        self._active = "inspect"
        self._buttons: dict[str, ttk.Button] = {}

        for tab_id, label_key in self._TABS:
            btn = ttk.Button(
                self,
                text=translate(label_key, locale),
                style="Tab.TButton",
                command=lambda tid=tab_id: self.select(tid),
            )
            btn.pack(side="left", padx=(0, 4))
            self._buttons[tab_id] = btn
        self._refresh_styles()

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def active(self) -> str:
        return self._active

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        for tab_id, label_key in self._TABS:
            self._buttons[tab_id].configure(text=translate(label_key, value))
        self._refresh_styles()

    def select(self, tab_id: str) -> None:
        if tab_id not in self._buttons:
            return
        self._active = tab_id
        self._refresh_styles()
        if self._on_select:
            self._on_select(tab_id)

    def _refresh_styles(self) -> None:
        for tab_id, button in self._buttons.items():
            button.configure(style="TabActive.TButton" if tab_id == self._active else "Tab.TButton")
