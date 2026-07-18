"""Flat details panel — all sections visible with wrapped text."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from custom_item_forge.core.model import InspectReport
from custom_item_forge.i18n import section_title, translate
from custom_item_forge.ui.utils.text import format_field_value


class DetailsPanel(ttk.LabelFrame):
    _LABEL_COLUMN_MIN = 96
    _LABEL_COLUMN_MAX = 140
    _LABEL_COLUMN_RATIO = 0.38

    def __init__(self, master: tk.Misc, *, locale: str = "en") -> None:
        super().__init__(master, text=translate("panel.details", locale), style="Card.TLabelframe")
        self._locale = locale
        self._wrap_labels: list[ttk.Label] = []
        self._blocks: list[ttk.Frame] = []

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

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, value: str) -> None:
        self._locale = value
        self.configure(text=translate("panel.details", value))

    def show_report(self, report: InspectReport | None) -> None:
        for child in self._inner.winfo_children():
            child.destroy()
        self._wrap_labels.clear()
        self._blocks.clear()
        if report is None:
            return

        for index, section in enumerate(report.sections):
            if index:
                ttk.Separator(self._inner, orient="horizontal").pack(fill="x", pady=(8, 6))
            ttk.Label(
                self._inner,
                text=section_title(section.id, self._locale).upper(),
                style="SectionHeader.TLabel",
            ).pack(anchor="w", pady=(0, 4))

            block = ttk.Frame(self._inner)
            block.pack(fill="x")
            block.columnconfigure(1, weight=1)
            self._blocks.append(block)

            for row, field in enumerate(section.fields):
                label = translate(field.label_key or field.key, self._locale)
                ttk.Label(block, text=f"{label}:", anchor="nw", style="FieldLabel.TLabel").grid(
                    row=row,
                    column=0,
                    sticky="nw",
                    padx=(0, 8),
                    pady=2,
                )
                value = ttk.Label(
                    block,
                    text=format_field_value(field.value),
                    anchor="nw",
                    justify="left",
                    wraplength=1,
                    style="FieldValue.TLabel",
                )
                value.grid(row=row, column=1, sticky="ew", pady=2)
                self._wrap_labels.append(value)

        self.after_idle(self._apply_wrap)

    def _label_column_width(self, canvas_width: int) -> int:
        return max(
            self._LABEL_COLUMN_MIN,
            min(self._LABEL_COLUMN_MAX, int(canvas_width * self._LABEL_COLUMN_RATIO)),
        )

    def _value_wrap_width(self, canvas_width: int) -> int:
        return max(80, canvas_width - self._label_column_width(canvas_width) - 20)

    def _apply_wrap(self) -> None:
        width = self._canvas.winfo_width()
        if width <= 1:
            return
        label_width = self._label_column_width(width)
        value_wrap = self._value_wrap_width(width)
        for block in self._blocks:
            block.columnconfigure(0, minsize=label_width)
        for label in self._wrap_labels:
            label.configure(wraplength=value_wrap)

    def _on_inner_configure(self, _event: object | None = None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._window_id, width=event.width)
        label_width = self._label_column_width(event.width)
        value_wrap = self._value_wrap_width(event.width)
        for block in self._blocks:
            block.columnconfigure(0, minsize=label_width)
        for label in self._wrap_labels:
            label.configure(wraplength=value_wrap)

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
