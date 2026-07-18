"""Thumbnail viewer with missing/unreadable/ok states."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.i18n import translate
from custom_item_forge.ui.photo_loader import photo_from_png
from custom_item_forge.ui.thumbnail_display import resolve_display_png


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
        family: str | None = None,
    ) -> None:
        png_bytes, _used_fallback = resolve_display_png(
            state=state,
            raw_bytes=data if state is ThumbnailState.OK else None,
            family=family,
        )
        if png_bytes:
            photo = photo_from_png(png_bytes, max_width=self.PREVIEW_SIZE, max_height=self.PREVIEW_SIZE)
            if photo is not None:
                self._photo = photo
                self._label.configure(image=self._photo, text="")
                return

        message_key = {
            ThumbnailState.MISSING: "thumbnail.missing",
            ThumbnailState.UNREADABLE: "thumbnail.unreadable",
            ThumbnailState.OK: "thumbnail.unreadable",
        }[state]
        self._photo = None
        self._label.configure(
            image="",
            text=translate(message_key, self._locale),
        )

    def clear(self) -> None:
        self.set_state(ThumbnailState.MISSING)
