"""Thumbnail viewer with missing/unreadable/ok states."""

from __future__ import annotations

import io
import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.i18n import translate


class ThumbnailViewer(ttk.Frame):
    PREVIEW_SIZE = 192

    def __init__(self, master: tk.Misc, *, locale: str = "en") -> None:
        super().__init__(master)
        self._locale = locale
        self._photo: tk.PhotoImage | None = None
        self._label = ttk.Label(self, anchor="center", justify="center")
        self._label.pack(fill="both", expand=True, padx=8, pady=8)
        self.set_state(ThumbnailState.MISSING)

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value

    def set_state(
        self,
        state: ThumbnailState,
        *,
        data: bytes | None = None,
    ) -> None:
        self._photo = None
        if state == ThumbnailState.OK and data:
            try:
                self._photo = tk.PhotoImage(data=data)
                width = self._photo.width()
                height = self._photo.height()
                if width > self.PREVIEW_SIZE or height > self.PREVIEW_SIZE:
                    scale = max(width, height) // self.PREVIEW_SIZE + 1
                    self._photo = self._photo.subsample(scale, scale)
                self._label.configure(image=self._photo, text="")
                return
            except tk.TclError:
                state = ThumbnailState.UNREADABLE

        message_key = {
            ThumbnailState.MISSING: "thumbnail.missing",
            ThumbnailState.UNREADABLE: "thumbnail.unreadable",
            ThumbnailState.OK: "thumbnail.unreadable",
        }[state]
        self._label.configure(
            image="",
            text=translate(message_key, self._locale),
        )

    def clear(self) -> None:
        self.set_state(ThumbnailState.MISSING)
