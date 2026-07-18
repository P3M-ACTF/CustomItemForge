"""Right column for Change: recategorize controls."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from custom_item_forge.catalog.categories import BY_ID, CATEGORIES
from custom_item_forge.core.errors import ForgeError, NotCalibratedError
from custom_item_forge.core.model import InspectReport
from custom_item_forge.engines.router import FamilyRouter
from custom_item_forge.i18n import translate
from custom_item_forge.ui.components.path_picker import PathPicker


class ChangeSidePanel(ttk.LabelFrame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        on_source_change: Callable[[str], None] | None = None,
        log: Callable[[str, str], None] | None = None,
        set_status: Callable[[str], None] | None = None,
        run_background: Callable[[str, Callable[[], object], Callable[[object], None] | None], None] | None = None,
    ) -> None:
        super().__init__(master, text=translate("tab.change", locale), style="Card.TLabelframe")
        self._locale = locale
        self._on_source_change = on_source_change
        self._log = log or (lambda _level, _msg: None)
        self._set_status = set_status or (lambda _msg: None)
        self._run_background = run_background
        self._category_display_map: dict[str, str] = {}

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text=translate("change.source", locale), style="FieldLabel.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 2),
        )
        self.source_picker = PathPicker(self, locale=locale, browse_mode="file", on_change=self._source_changed)
        self.source_picker.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(self, text=translate("change.category", locale), style="FieldLabel.TLabel").grid(
            row=2, column=0, sticky="w",
        )
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=3, column=0, sticky="ew", pady=(2, 8))

        ttk.Label(self, text=translate("change.output", locale), style="FieldLabel.TLabel").grid(
            row=4, column=0, sticky="w",
        )
        output_row = ttk.Frame(self)
        output_row.grid(row=5, column=0, sticky="ew", pady=(2, 8))
        output_row.columnconfigure(0, weight=1)
        self.output_picker = PathPicker(output_row, locale=locale, browse_mode="file")
        self.output_picker.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            output_row,
            text=translate("menu.save_as", locale),
            command=lambda: self.output_picker.pick_save_as("changed-item.vroidcustomitem"),
        ).grid(row=0, column=1, padx=(4, 0))

        self.warning = ttk.Label(self, text="", style="Warning.TLabel", wraplength=220, justify="left")
        self.warning.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        self.bind("<Configure>", lambda _e: self._sync_warning_wrap())

        self.create_btn = ttk.Button(self, text=translate("change.create", locale), command=self.do_change)
        self.create_btn.grid(row=7, column=0, sticky="ew")

    def _sync_warning_wrap(self) -> None:
        width = max(160, self.winfo_width() - 12)
        self.warning.configure(wraplength=width)

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate("tab.change", value))
        self.create_btn.configure(text=translate("change.create", value))

    def set_source(self, path: str, *, load: bool = True) -> None:
        self.source_picker.set(path)
        if load and path.strip():
            self._source_changed()

    def _source_changed(self) -> None:
        source = self.source_picker.get().strip()
        if source and self._on_source_change:
            self._on_source_change(source)

    def _populate_categories(self, report: InspectReport) -> None:
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
            compat = FamilyRouter().compatibility(category_id, language=self._locale)
            self.warning.configure(
                text="" if compat.can_recategorize else compat.recategorize_reason
            )
        self.after_idle(self._sync_warning_wrap)

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
