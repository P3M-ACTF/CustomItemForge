"""Unified application shell."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from custom_item_forge.core.errors import ForgeError
from custom_item_forge.i18n import translate
from custom_item_forge.ops.inspect import inspect_item
from custom_item_forge.ops.validate import validate_item
from custom_item_forge.ui.components.inspect_panel import InspectPanel
from custom_item_forge.ui.components.thumbnail_viewer import ThumbnailViewer


class CustomItemForgeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.locale = "en"
        self.current_path: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.root.title(f"{translate('app.title', self.locale)} — {translate('app.tagline', self.locale)}")
        self.root.minsize(820, 560)

        toolbar = ttk.Frame(self.root, padding=(8, 8, 8, 4))
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text=translate("menu.open", self.locale), command=self.open_file).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(toolbar, text=translate("menu.validate", self.locale), command=self.validate_file).pack(
            side="left", padx=(0, 6)
        )

        lang_frame = ttk.Frame(toolbar)
        lang_frame.pack(side="right")
        ttk.Label(lang_frame, text=translate("menu.language", self.locale)).pack(side="left", padx=(0, 4))
        self.lang_var = tk.StringVar(value=self.locale)
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["en", "es"],
            state="readonly",
            width=6,
        )
        lang_combo.pack(side="left")
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(body, padding=4)
        right = ttk.Frame(body, padding=4)
        body.add(left, weight=0)
        body.add(right, weight=1)

        self.thumbnail = ThumbnailViewer(left, locale=self.locale)
        self.thumbnail.pack(fill="both", expand=True)

        self.inspect_panel = InspectPanel(right, locale=self.locale)
        self.inspect_panel.pack(fill="both", expand=True)

        self.status = ttk.Label(self.root, text=translate("status.ready", self.locale), anchor="w", padding=(8, 4))
        self.status.pack(fill="x")

    def _on_language_change(self, _event: object | None = None) -> None:
        self.locale = self.lang_var.get()
        self.root.title(f"{translate('app.title', self.locale)} — {translate('app.tagline', self.locale)}")
        self.thumbnail.locale = self.locale
        self.inspect_panel.locale = self.locale
        if self.current_path:
            self._load_path(self.current_path)

    def open_file(self) -> None:
        selected = filedialog.askopenfilename(
            title=translate("dialog.open_title", self.locale),
            filetypes=[("Custom Item", "*.vroidcustomitem"), ("All files", "*.*")],
        )
        if selected:
            self._load_path(Path(selected))

    def _load_path(self, path: Path) -> None:
        try:
            report = inspect_item(path, language=self.locale)
        except ForgeError as exc:
            messagebox.showerror(translate("app.title", self.locale), str(exc))
            self.status.configure(text=translate("status.error", self.locale, message=str(exc)))
            return
        except OSError as exc:
            messagebox.showerror(translate("app.title", self.locale), str(exc))
            self.status.configure(text=translate("status.error", self.locale, message=str(exc)))
            return

        self.current_path = path
        self.thumbnail.set_state(report.thumbnail_state, data=report.thumbnail_bytes)
        self.inspect_panel.show_report(report)
        self.status.configure(text=translate("status.opened", self.locale, path=path.name))

    def validate_file(self) -> None:
        if self.current_path is None:
            self.open_file()
            if self.current_path is None:
                return
        try:
            report = validate_item(self.current_path)
        except ForgeError as exc:
            messagebox.showerror(translate("app.title", self.locale), str(exc))
            self.status.configure(text=translate("status.error", self.locale, message=str(exc)))
            return

        if report.valid:
            self.status.configure(text=translate("status.valid", self.locale))
            messagebox.showinfo(translate("app.title", self.locale), translate("status.valid", self.locale))
        else:
            self.status.configure(text=translate("status.invalid", self.locale))
            details = "\n".join(issue.message for issue in report.issues if issue.severity != "info")
            messagebox.showwarning(translate("app.title", self.locale), details or translate("status.invalid", self.locale))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CustomItemForgeApp().run()


if __name__ == "__main__":
    main()
