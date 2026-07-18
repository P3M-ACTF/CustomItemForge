"""Combine tab shell — merge blocked until calibration."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from custom_item_forge.core.errors import ForgeError, NotCalibratedError
from custom_item_forge.core.model import InspectReport
from custom_item_forge.engines.router import FamilyRouter
from custom_item_forge.i18n import translate
from custom_item_forge.ui.components.path_picker import PathPicker
from custom_item_forge.ui.components.preview_card import PreviewCard


class CombineTab(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        log: Callable[[str, str], None] | None = None,
        set_status: Callable[[str], None] | None = None,
        run_background: Callable[[str, Callable[[], object], Callable[[object], None] | None], None] | None = None,
    ) -> None:
        super().__init__(master, padding=12)
        self._locale = locale
        self._log = log or (lambda _level, _msg: None)
        self._set_status = set_status or (lambda _msg: None)
        self._run_background = run_background
        self._base_report: InspectReport | None = None
        self._addon_report: InspectReport | None = None

        files = ttk.LabelFrame(self, text=translate("panel.files", locale), style="Card.TLabelframe", padding=8)
        files.pack(fill="x", pady=(0, 10))
        for row, (label_key, attr) in enumerate(
            (
                ("combine.base", "base_picker"),
                ("combine.addon", "addon_picker"),
                ("combine.output", "output_picker"),
            )
        ):
            ttk.Label(files, text=translate(label_key, locale), width=12).grid(row=row, column=0, sticky="w")
            picker = PathPicker(files, locale=locale, browse_mode="file", on_change=self.refresh_previews)
            picker.grid(row=row, column=1, sticky="ew", padx=6)
            setattr(self, attr, picker)
            if attr == "output_picker":
                ttk.Button(
                    files,
                    text=translate("menu.save_as", locale),
                    command=lambda: self.output_picker.pick_save_as("merged-item.vroidcustomitem"),
                ).grid(row=row, column=2)
        files.columnconfigure(1, weight=1)

        previews = ttk.Frame(self)
        previews.pack(fill="both", expand=True)
        self.base_preview = PreviewCard(previews, title_key="combine.base", locale=locale)
        self.addon_preview = PreviewCard(previews, title_key="combine.addon", locale=locale)
        self.result_preview = PreviewCard(previews, title_key="combine.result", locale=locale)
        for card in (self.base_preview, self.addon_preview, self.result_preview):
            card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.mismatch_label = ttk.Label(self, text="", style="Warning.TLabel", wraplength=900)
        self.mismatch_label.pack(fill="x", pady=(8, 4))

        self.confirm_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text=translate("combine.confirm", locale), variable=self.confirm_var).pack(anchor="w")
        self.merge_btn = ttk.Button(self, text=translate("combine.merge", locale), command=self.do_merge)
        self.merge_btn.pack(fill="x", pady=(8, 0))

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.merge_btn.configure(text=translate("combine.merge", value))
        self.refresh_previews()

    def refresh_previews(self) -> None:
        self._base_report = self._load_card(self.base_picker, self.base_preview)
        self._addon_report = self._load_card(self.addon_picker, self.addon_preview)
        self.result_preview.clear()
        self._update_mismatch_label()

    def _load_card(self, picker: PathPicker, card: PreviewCard) -> InspectReport | None:
        path = picker.get().strip()
        if not path:
            card.clear()
            return None
        try:
            return card.show(path)
        except ForgeError as exc:
            self._log("ERROR", str(exc))
            card.clear()
            return None

    def _update_mismatch_label(self) -> None:
        if self._base_report is None or self._addon_report is None:
            self.mismatch_label.configure(text="")
            return
        base = self._base_report.field_map("vroid")
        addon = self._addon_report.field_map("vroid")
        base_family = base.get("family")
        addon_family = addon.get("family")
        if base_family and addon_family and base_family != addon_family:
            self.mismatch_label.configure(text=translate("combine.family_mismatch", self._locale))
            return
        if base.get("category_id") != addon.get("category_id"):
            self.mismatch_label.configure(text=translate("combine.mismatch", self._locale))
            return
        self.mismatch_label.configure(text=translate("compat.awaiting_calibration", self._locale, family=base_family or "hair"))

    def do_merge(self) -> None:
        base = self.base_picker.get().strip()
        addon = self.addon_picker.get().strip()
        if not base or not addon:
            messagebox.showwarning(translate("tab.combine", self._locale), translate("dialog.missing_files", self._locale))
            return
        if not self.confirm_var.get():
            messagebox.showwarning(translate("tab.combine", self._locale), translate("combine.confirm", self._locale))
            return
        output = self._resolve_output(base)
        if output.exists() and not messagebox.askyesno(
            translate("tab.combine", self._locale),
            translate("dialog.overwrite", self._locale),
        ):
            return

        def action() -> object:
            return FamilyRouter().merge(base, addon, output, force=output.exists())

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

    def _resolve_output(self, base: str) -> Path:
        raw = self.output_picker.get().strip() or "merged-item.vroidcustomitem"
        candidate = Path(raw)
        if candidate.parent == Path("."):
            candidate = Path(base).expanduser().resolve().parent / candidate
        if candidate.suffix.lower() != ".vroidcustomitem":
            candidate = candidate.with_suffix(".vroidcustomitem")
        self.output_picker.set(str(candidate))
        return candidate
