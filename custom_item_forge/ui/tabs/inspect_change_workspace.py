"""Shared Inspect/Change workspace — preview 3/4, side panel 1/4."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Callable

from custom_item_forge.core.errors import ForgeError
from custom_item_forge.i18n import translate
from custom_item_forge.ui.components.change_side_panel import ChangeSidePanel
from custom_item_forge.ui.components.inspect_side_panel import InspectSidePanel
from custom_item_forge.ui.components.preview_card import PreviewCard
from custom_item_forge.ui.utils.activity import report_inspected


class InspectChangeWorkspace(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        locale: str = "en",
        log: Callable[[str, str], None] | None = None,
        set_status: Callable[[str], None] | None = None,
        run_background: Callable[[str, Callable[[], object], Callable[[object], None] | None], None] | None = None,
    ) -> None:
        super().__init__(master, padding=4)
        self._locale = locale
        self._log = log or (lambda _level, _msg: None)
        self._set_status = set_status or (lambda _msg: None)
        self._run_background = run_background
        self._mode = "inspect"

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)

        self.preview = PreviewCard(body, title_key="panel.preview", locale=locale, large=True)
        self.side_host = ttk.Frame(body)
        body.add(self.preview, weight=3)
        body.add(self.side_host, weight=1)

        self.inspect_side = InspectSidePanel(
            self.side_host,
            locale=locale,
            on_item_loaded=self._load_from_inspect,
            log=log,
            set_status=set_status,
            run_background=run_background,
        )
        self.change_side = ChangeSidePanel(
            self.side_host,
            locale=locale,
            on_source_change=self._load_from_change,
            log=log,
            set_status=set_status,
            run_background=run_background,
        )
        self.inspect_side.pack(fill="both", expand=True)
        self.change_side.pack_forget()

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.preview.locale = value
        self.inspect_side.locale = value
        self.change_side.locale = value

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        if mode == "inspect":
            self.change_side.pack_forget()
            self.inspect_side.pack(fill="both", expand=True)
        else:
            self.inspect_side.pack_forget()
            self.change_side.pack(fill="both", expand=True)
            if self.preview.current_path:
                self.change_side.set_source(str(self.preview.current_path), load=False)
                if self.preview.current_report:
                    self.change_side._populate_categories(self.preview.current_report)

    def _load_from_inspect(self, path: Path) -> None:
        self._load_item(path, origin="inspect")

    def _load_from_change(self, source: str) -> None:
        self._load_item(Path(source), origin="change")

    def _load_item(self, path: Path, *, origin: str) -> None:
        try:
            report = self.preview.show(path)
        except ForgeError as exc:
            self._log("ERROR", str(exc))
            self._set_status(translate("status.failed", self._locale))
            return

        self.inspect_side._current_path = path
        self.inspect_side.details.show_report(report)
        self.change_side._populate_categories(report)

        if origin == "inspect":
            report_inspected(self._log, self._set_status, self._locale, path, report)
        else:
            report_inspected(
                self._log,
                self._set_status,
                self._locale,
                path,
                report,
                slot=translate("tab.change", self._locale),
            )
