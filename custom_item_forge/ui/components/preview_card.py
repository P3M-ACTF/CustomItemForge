"""Adaptive preview card with metadata."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import InspectReport, ThumbnailState
from custom_item_forge.core.thumbnail_compose import ensure_item_thumbnail
from custom_item_forge.i18n import translate
from custom_item_forge.ops.inspect import inspect_item
from custom_item_forge.ui.photo_loader import photo_from_png
from custom_item_forge.ui.thumbnail_display import resolve_display_png
from custom_item_forge.ui.utils.tooltip import ToolTip


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
        self._png_bytes: bytes | None = None
        self.rendered_photo: tk.PhotoImage | None = None
        self.current_path: Path | None = None
        self.current_report: InspectReport | None = None
        self._used_fallback = False
        self._resize_job: str | None = None
        self._last_render_size = (0, 0)

        self.image_area = ttk.Frame(self)
        self.image_area.pack(fill="both", expand=True, pady=(0, 4 if large else 6))
        self.image = ttk.Label(self.image_area, text="◇", anchor="center", font=("Segoe UI", 30))
        self.image.place(relx=0.5, rely=0.5, anchor="center")
        self.image_area.bind("<Configure>", self._resize)
        self.bind("<Configure>", self._resize)

        self.name_label = ttk.Label(
            self,
            text=translate("preview.empty", locale),
            anchor="center",
            wraplength=420 if large else 220,
            font=("Segoe UI", 9 if large else 8),
        )
        self.name_label.pack(fill="x")
        self.meta_label = ttk.Label(
            self,
            text="",
            anchor="center",
            justify="center",
            foreground="#555",
            font=("Segoe UI", 8),
        )
        self.meta_label.pack(fill="x", pady=(2, 0))
        self._name_tooltip = ToolTip(self.name_label, "")

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
        self._png_bytes = None
        self.rendered_photo = None
        self._used_fallback = False
        self.image.configure(image="", text="◇")
        self.name_label.configure(text=translate("preview.empty", self._locale))
        self.meta_label.configure(text="")

    def _resize(self, _event: object | None = None) -> None:
        if self._png_bytes is None:
            return
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(40, self._apply_resize)

    def _apply_resize(self) -> None:
        self._resize_job = None
        if self._png_bytes is None:
            return
        width = max(
            80,
            self.image_area.winfo_width() - 8,
            self.winfo_width() - 16,
        )
        height = max(
            80,
            self.image_area.winfo_height() - 8,
            self.winfo_height() - (72 if self.large else 56),
        )
        size = (width, height)
        if size == self._last_render_size and self.rendered_photo is not None:
            return
        self._last_render_size = size
        photo = photo_from_png(self._png_bytes, max_width=width, max_height=height)
        if photo is None:
            return
        self.rendered_photo = photo
        self._photo_refs.append(photo)
        self.image.configure(image=self.rendered_photo, text="")
        wrap = max(120, self.winfo_width() - 16)
        self.name_label.configure(wraplength=wrap)

    def show(self, path: str | Path) -> InspectReport:
        resolved = Path(path).expanduser().resolve()
        report = inspect_item(resolved, language=self._locale)
        self.current_path = resolved
        self.current_report = report

        family = report.field_map("vroid").get("family")
        family_str = family if isinstance(family, str) else None
        if report.thumbnail_state is ThumbnailState.OK and report.thumbnail_bytes:
            png_bytes, used_fallback = resolve_display_png(
                state=report.thumbnail_state,
                raw_bytes=report.thumbnail_bytes,
                family=family_str,
            )
        else:
            generated = ensure_item_thumbnail(resolved, family=family_str)
            png_bytes = generated
            used_fallback = True
        self._png_bytes = png_bytes
        self._used_fallback = used_fallback
        self._last_render_size = (0, 0)

        if png_bytes:
            self.after_idle(self._resize)
        else:
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
        meta = f"{category} · {size_bytes / 1024:.1f} KiB · {entries} entries"
        if self._used_fallback:
            meta += f"\n{translate('thumbnail.fallback', self._locale)}"
        self.name_label.configure(text=resolved.name)
        self._name_tooltip.set_text(str(resolved))
        self.meta_label.configure(text=meta)
        return report
