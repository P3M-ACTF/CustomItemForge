"""Change tab shell — recategorize blocked until calibration."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from custom_item_forge.catalog.categories import BY_ID, CATEGORIES
from custom_item_forge.core.errors import ForgeError, NotCalibratedError
from custom_item_forge.engines.router import FamilyRouter
from custom_item_forge.i18n import translate
from custom_item_forge.ui.components.path_picker import PathPicker
from custom_item_forge.ui.components.preview_card import PreviewCard


class ChangeTab(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        log: Callable[[str, str], None] | None = None,
        set_status: Callable[[str], None] | None = None,
        run_background: Callable[[str, Callable[[], object], Callable[[object], None] | None], None] | None = None,
    ) -> None:
        super().__init__(master, padding=8)
        self._locale = locale
        self._log = log or (lambda _level, _msg: None)
        self._set_status = set_status or (lambda _msg: None)
        self._run_background = run_background
        self._category_display_map: dict[str, str] = {}

        source = ttk.LabelFrame(self, text=translate("panel.item", locale), style="Card.TLabelframe", padding=8)
        source.pack(fill="x", pady=(0, 8))
        source.columnconfigure(1, weight=1)
        ttk.Label(source, text=translate("change.source", locale), width=16).grid(row=0, column=0, sticky="w")
        self.source_picker = PathPicker(source, locale=locale, browse_mode="file", on_change=self.load_item)
        self.source_picker.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)
        self.preview = PreviewCard(body, title_key="panel.preview", locale=locale, large=True)
        controls = ttk.LabelFrame(body, text=translate("panel.details", locale), style="Card.TLabelframe", padding=8)
        body.add(self.preview, weight=3)
        body.add(controls, weight=2)

        controls.columnconfigure(0, weight=1)
        ttk.Label(controls, text=translate("change.category", locale)).grid(row=0, column=0, sticky="w")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(controls, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=1, column=0, sticky="ew", pady=(4, 10))
        ttk.Label(controls, text=translate("change.output", locale)).grid(row=2, column=0, sticky="w")
        output_row = ttk.Frame(controls)
        output_row.grid(row=3, column=0, sticky="ew", pady=(4, 10))
        output_row.columnconfigure(0, weight=1)
        self.output_picker = PathPicker(output_row, locale=locale, browse_mode="file")
        self.output_picker.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            output_row,
            text=translate("menu.save_as", locale),
            command=lambda: self.output_picker.pick_save_as("changed-item.vroidcustomitem"),
        ).grid(row=0, column=1, padx=(6, 0))
        self.warning = ttk.Label(controls, text="", style="Warning.TLabel", wraplength=420, justify="left")
        self.warning.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        self.create_btn = ttk.Button(controls, text=translate("change.create", locale), command=self.do_change)
        self.create_btn.grid(row=5, column=0, sticky="ew")

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.create_btn.configure(text=translate("change.create", value))
        if self.preview.current_path:
            self.load_item()

    def load_item(self) -> None:
        source = self.source_picker.get().strip()
        if not source:
            return
        try:
            report = self.preview.show(source)
        except ForgeError as exc:
            self._log("ERROR", str(exc))
            return
        family = report.field_map("vroid").get("family")
        choices = [item for item in CATEGORIES if not family or item.family == family]
        self._category_display_map = {item.display(self._locale): item.key for item in choices}
        self.category_combo.configure(values=list(self._category_display_map))
        category_id = report.field_map("vroid").get("category_id")
        current = BY_ID.get(category_id or "")
        self.category_var.set(current.display(self._locale) if current else (next(iter(self._category_display_map), "")))
        if family in {"clothing", "accessory"}:
            self.warning.configure(text=translate("change.family_limited", self._locale))
        else:
            self.warning.configure(text=translate("compat.awaiting_calibration", self._locale, family=family or "hair"))

    def do_change(self) -> None:
        source = self.source_picker.get().strip()
        if not source or not self.category_var.get():
            messagebox.showwarning(translate("tab.change", self._locale), translate("dialog.missing_files", self._locale))
            return
        output = self._resolve_output(source)
        if output.exists() and not messagebox.askyesno(
            translate("tab.change", self._locale),
            translate("dialog.overwrite", self._locale),
        ):
            return
        category_key = self._category_display_map.get(self.category_var.get(), self.category_var.get())

        def action() -> Path:
            return FamilyRouter().recategorize(source, output, category_key, force=output.exists())

        def finished(payload: object) -> None:
            if isinstance(payload, NotCalibratedError):
                self._log("NOTICE", str(payload))
                self._set_status(str(payload))
                return
            if isinstance(payload, ForgeError):
                self._log("ERROR", str(payload))
                self._set_status(translate("status.failed", self._locale))
                return
            self._log("INFO", translate("status.done", self._locale))
            self._set_status(translate("status.done", self._locale))

        if self._run_background:
            self._run_background(translate("status.working", self._locale), action, finished)
        else:
            try:
                finished(action())
            except ForgeError as exc:
                finished(exc)

    def _resolve_output(self, source: str) -> Path:
        raw = self.output_picker.get().strip() or "changed-item.vroidcustomitem"
        candidate = Path(raw)
        if candidate.parent == Path("."):
            candidate = Path(source).expanduser().resolve().parent / candidate
        if candidate.suffix.lower() != ".vroidcustomitem":
            candidate = candidate.with_suffix(".vroidcustomitem")
        self.output_picker.set(str(candidate))
        return candidate
