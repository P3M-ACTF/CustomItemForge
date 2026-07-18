"""Inspect tab with three-column layout."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Callable

from custom_item_forge.core.errors import ForgeError
from custom_item_forge.i18n import translate
from custom_item_forge.ops.discover import discover_items
from custom_item_forge.ops.validate import validate_item
from custom_item_forge.ui.components.details_panel import DetailsPanel
from custom_item_forge.ui.components.file_list_panel import FileListPanel
from custom_item_forge.ui.components.preview_card import PreviewCard


class InspectTab(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        log: Callable[[str, str], None] | None = None,
        set_status: Callable[[str], None] | None = None,
        run_background: Callable[[str, Callable[[], object], Callable[[object], None] | None], None] | None = None,
    ) -> None:
        super().__init__(master, padding=6)
        self._locale = locale
        self._log = log or (lambda _level, _msg: None)
        self._set_status = set_status or (lambda _msg: None)
        self._run_background = run_background
        self._current_path: Path | None = None

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)

        self.file_list = FileListPanel(
            body,
            locale=locale,
            on_select=self._inspect_path,
            on_open=self.scan_source,
            on_validate=self.validate_current,
        )
        self.preview = PreviewCard(body, title_key="tab.inspect", locale=locale, large=True)
        self.details = DetailsPanel(body, locale=locale)

        body.add(self.file_list, weight=1)
        body.add(self.preview, weight=5)
        body.add(self.details, weight=2)

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.file_list.locale = value
        self.preview.locale = value
        self.details.locale = value
        if self._current_path:
            self._inspect_path(self._current_path)

    def scan_source(self) -> None:
        source = self.file_list.source_path().strip()
        if not source:
            return

        def action() -> list[Path]:
            return discover_items(source)

        def finished(payload: object) -> None:
            if isinstance(payload, ForgeError):
                self._log("ERROR", str(payload))
                self._set_status(translate("status.failed", self._locale))
                return
            paths = list(payload)  # type: ignore[arg-type]
            if not paths:
                self._log("INFO", translate("dialog.no_items", self._locale))
                self._set_status(translate("dialog.no_items", self._locale))
                return
            self.file_list.set_items(paths)
            self._log("INFO", f"Found {len(paths)} item(s)")

        if self._run_background:
            self._run_background(translate("status.scanning", self._locale), action, finished)
        else:
            try:
                finished(action())
            except ForgeError as exc:
                finished(exc)

    def _inspect_path(self, path: Path) -> None:
        try:
            report = self.preview.show(path)
        except ForgeError as exc:
            self._log("ERROR", str(exc))
            self._set_status(translate("status.failed", self._locale))
            return
        self._current_path = path
        self.details.show_report(report)
        category = report.field_map("vroid").get("category_label", "—")
        entries = report.field_map("file").get("entry_count", 0)
        message = translate(
            "status.inspected",
            self._locale,
            name=path.name,
            category=category,
            entries=entries,
        )
        self._log("INFO", message)
        self._set_status(message)

    def validate_current(self) -> None:
        path = self._current_path or self.file_list.selected_path()
        if path is None:
            self._log("INFO", translate("preview.empty", self._locale))
            return
        try:
            report = validate_item(path)
        except ForgeError as exc:
            self._log("ERROR", str(exc))
            self._set_status(translate("status.failed", self._locale))
            return
        if report.valid:
            self._log("INFO", translate("status.valid", self._locale))
            self._set_status(translate("status.valid", self._locale))
        else:
            for issue in report.issues:
                if issue.severity != "info":
                    self._log(issue.severity.upper(), issue.message)
            self._set_status(translate("status.invalid", self._locale))
