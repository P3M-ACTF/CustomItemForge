"""Adaptive preview card with metadata."""

from __future__ import annotations

import math
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import InspectReport, ThumbnailState
from custom_item_forge.i18n import translate
from custom_item_forge.ops.inspect import inspect_item


class PreviewCard(ttk.LabelFrame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        title_key: str = "panel.preview",
        locale: str = "en",
        large: bool = False,
    ) -> None:
        super().__init__(master, text=translate(title_key, locale), style="Card.TLabelframe")
        self._locale = locale
        self._title_key = title_key
        self.large = large
        self._photo_refs: list[tk.PhotoImage] = []
        self.original_photo: tk.PhotoImage | None = None
        self.rendered_photo: tk.PhotoImage | None = None
        self.current_path: Path | None = None
        self.current_report: InspectReport | None = None

        self.image_area = ttk.Frame(self)
        self.image_area.pack(fill="both", expand=True, pady=(0, 8))
        self.image = ttk.Label(self.image_area, text="◇", anchor="center", font=("Segoe UI", 30))
        self.image.pack(fill="both", expand=True)
        self.image_area.bind("<Configure>", self._resize)

        self.name_label = ttk.Label(self, text=translate("preview.empty", locale), anchor="center", wraplength=270)
        self.name_label.pack(fill="x")
        self.meta_label = ttk.Label(self, text="", anchor="center", justify="center", foreground="#555")
        self.meta_label.pack(fill="x", pady=(4, 0))

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate(self._title_key, value))
        if self.current_report is None:
            self.name_label.configure(text=translate("preview.empty", value))
        elif self.current_path is not None:
            self.show(self.current_path)

    def clear(self) -> None:
        self.current_path = None
        self.current_report = None
        self.original_photo = None
        self.rendered_photo = None
        self.image.configure(image="", text="◇")
        self.name_label.configure(text=translate("preview.empty", self._locale))
        self.meta_label.configure(text="")

    def _resize(self, _event: object | None = None) -> None:
        if self.original_photo is None:
            return
        width = max(80, self.image_area.winfo_width() - 16)
        height = max(80, self.image_area.winfo_height() - 16)
        factor = max(
            1,
            math.ceil(self.original_photo.width() / width),
            math.ceil(self.original_photo.height() / height),
        )
        self.rendered_photo = (
            self.original_photo.subsample(factor, factor) if factor > 1 else self.original_photo
        )
        self.image.configure(image=self.rendered_photo, text="")

    def show(self, path: str | Path) -> InspectReport:
        resolved = Path(path).expanduser().resolve()
        report = inspect_item(resolved, language=self._locale)
        self.current_path = resolved
        self.current_report = report

        if report.thumbnail_state == ThumbnailState.OK and report.thumbnail_bytes:
            try:
                self.original_photo = tk.PhotoImage(data=report.thumbnail_bytes)
                self._photo_refs.append(self.original_photo)
                self.after_idle(self._resize)
            except tk.TclError:
                self.original_photo = None
                self.image.configure(image="", text="◇")
        else:
            self.original_photo = None
            self.rendered_photo = None
            placeholder = {
                ThumbnailState.MISSING: translate("thumbnail.missing", self._locale),
                ThumbnailState.UNREADABLE: translate("thumbnail.unreadable", self._locale),
            }.get(report.thumbnail_state, "◇")
            self.image.configure(image="", text=placeholder)

        vroid = report.field_map("vroid")
        file_data = report.field_map("file")
        category = vroid.get("category_label", "—")
        size_bytes = file_data.get("size_bytes", 0)
        entries = file_data.get("entry_count", 0)
        self.name_label.configure(text=resolved.name)
        self.meta_label.configure(
            text=f"{category}\n{size_bytes / 1024:.1f} KiB · {entries} entries"
        )
        return report
