"""Accordion details panel grouped by section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import InspectReport
from custom_item_forge.i18n import section_title, translate
from custom_item_forge.ui.components.collapsible_section import CollapsibleSection
from custom_item_forge.ui.utils.text import format_field_value, is_wide_value
from custom_item_forge.ui.utils.tooltip import ToolTip


class DetailsPanel(ttk.LabelFrame):
    _LABEL_WIDTH = 22

    def __init__(self, master: tk.Misc, *, locale: str = "en") -> None:
        super().__init__(master, text=translate("panel.details", locale), style="Card.TLabelframe")
        self._locale = locale
        self._sections: dict[str, CollapsibleSection] = {}
        self._tooltips: list[ToolTip] = []

        self._canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._inner = ttk.Frame(self._canvas)
        self._inner.bind("<Configure>", self._on_inner_configure)
        self._window_id = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel(self._canvas)

        for index, section_id in enumerate(("vroid", "vroidcustomitem", "file")):
            section = CollapsibleSection(
                self._inner,
                section_title(section_id, locale),
                expanded=index == 0,
            )
            section.pack(fill="x", pady=(0, 4))
            self._sections[section_id] = section

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate("panel.details", value))
        for section_id, widget in self._sections.items():
            widget.set_title(section_title(section_id, value))

    def show_report(self, report: InspectReport | None) -> None:
        self._tooltips.clear()
        for section_id, widget in self._sections.items():
            widget.clear_body()
            if report is None:
                continue
            section = next((item for item in report.sections if item.id == section_id), None)
            if section is None:
                continue
            self._fill_section(widget.body, section.fields)

    def _fill_section(self, parent: ttk.Frame, fields: tuple) -> None:
        parent.columnconfigure(1, weight=1)
        for row, field in enumerate(fields):
            label = translate(field.label_key or field.key, self._locale)
            ttk.Label(parent, text=label, width=self._LABEL_WIDTH, anchor="w").grid(
                row=row,
                column=0,
                sticky="nw",
                padx=(0, 8),
                pady=2,
            )
            value_text = format_field_value(field.value)
            if is_wide_value(field.value):
                value = ttk.Entry(parent)
                value.insert(0, value_text)
                value.configure(state="readonly")
                value.grid(row=row, column=1, sticky="ew", pady=2)
            else:
                value = ttk.Label(parent, text=value_text, anchor="w", wraplength=360, justify="left")
                value.grid(row=row, column=1, sticky="ew", pady=2)
            if len(value_text) > 48:
                self._tooltips.append(ToolTip(value, value_text))

    def _on_inner_configure(self, _event: object | None = None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._window_id, width=event.width)

    def _bind_mousewheel(self, widget: tk.Misc) -> None:
        def _scroll(event: tk.Event) -> None:
            if event.delta:
                self._canvas.yview_scroll(int(-event.delta / 120), "units")
            elif event.num == 4:
                self._canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._canvas.yview_scroll(1, "units")

        widget.bind("<Enter>", lambda _e: widget.bind_all("<MouseWheel>", _scroll), add="+")
        widget.bind("<Leave>", lambda _e: widget.unbind_all("<MouseWheel>"), add="+")
        widget.bind("<Enter>", lambda _e: widget.bind_all("<Button-4>", _scroll), add="+")
        widget.bind("<Enter>", lambda _e: widget.bind_all("<Button-5>", _scroll), add="+")
