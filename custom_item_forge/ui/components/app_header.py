"""Compact application header with title, version, and quick actions."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable
import webbrowser

from custom_item_forge import REPO_URL, __version__
from custom_item_forge.i18n import translate
from custom_item_forge.ui.utils.tooltip import ToolTip


class AppHeader(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        on_language: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, padding=(8, 6, 8, 2))
        self._locale = locale
        self._on_language = on_language

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        self.title_label = ttk.Label(self, text=translate("app.title", locale), style="Title.TLabel")
        self.title_label.grid(row=0, column=0, rowspan=2, sticky="w")

        meta = ttk.Frame(self)
        meta.grid(row=0, column=1, rowspan=2, sticky="w", padx=(10, 0))
        meta.columnconfigure(0, weight=1)
        meta.columnconfigure(1, weight=1)

        self.version_label = ttk.Label(meta, text=f"v{__version__}", style="Meta.TLabel")
        self.version_label.grid(row=0, column=0, columnspan=2, sticky="w")

        actions = ttk.Frame(meta)
        actions.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))
        self.update_btn = ttk.Button(
            actions,
            text="↻",
            width=3,
            style="Icon.TButton",
            command=self._check_updates,
        )
        self.update_btn.pack(side="left")
        self.repo_btn = ttk.Button(
            actions,
            text="⎇",
            width=3,
            style="Icon.TButton",
            command=self._open_repo,
        )
        self.repo_btn.pack(side="left", padx=(4, 0))

        ToolTip(self.update_btn, translate("header.update", locale))
        ToolTip(self.repo_btn, translate("header.repo", locale))

        self.lang_button = ttk.Button(
            self,
            text=translate("menu.language.toggle", locale),
            command=self._toggle_language,
        )
        self.lang_button.grid(row=0, column=2, rowspan=2, sticky="ne")

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.title_label.configure(text=translate("app.title", value))
        self.lang_button.configure(text=translate("menu.language.toggle", value))

    def _toggle_language(self) -> None:
        if self._on_language:
            self._on_language()

    def _check_updates(self) -> None:
        messagebox.showinfo(
            translate("header.update", self._locale),
            translate("header.update_soon", self._locale),
        )

    def _open_repo(self) -> None:
        webbrowser.open(REPO_URL)
