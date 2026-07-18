"""Unified application shell."""

from __future__ import annotations

import queue
import threading
import traceback
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from custom_item_forge.core.errors import ForgeError, NotCalibratedError
from custom_item_forge.i18n import translate
from custom_item_forge.ui.components.log_view import LogView
from custom_item_forge.ui.tabs.change_tab import ChangeTab
from custom_item_forge.ui.tabs.combine_tab import CombineTab
from custom_item_forge.ui.tabs.inspect_tab import InspectTab
from custom_item_forge.ui.themes.simple.styles import apply_simple_theme


class CustomItemForgeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.locale = "en"
        apply_simple_theme(self.root)
        self.root.geometry("1180x790")
        self.root.minsize(940, 660)
        self.root.title(translate("app.window_title", self.locale))

        self.status_var = tk.StringVar(value=translate("status.ready", self.locale))
        self._events: queue.Queue[tuple[str, object, Callable[[object], None] | None]] = queue.Queue()

        self._build_ui()
        self.root.after(100, self._poll_events)

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=(14, 10, 14, 0))
        top.pack(fill="x")
        self.title_label = ttk.Label(top, text=translate("app.title", self.locale), style="Title.TLabel")
        self.title_label.pack(side="left")
        self.lang_button = ttk.Button(top, text=translate("menu.language.toggle", self.locale), command=self.toggle_language)
        self.lang_button.pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=10)

        shared = {
            "locale": self.locale,
            "log": self.log,
            "set_status": self.set_status,
            "run_background": self.run_background,
        }
        self.inspect_tab = InspectTab(self.notebook, **shared)
        self.change_tab = ChangeTab(self.notebook, **shared)
        self.combine_tab = CombineTab(self.notebook, **shared)

        self.notebook.add(self.inspect_tab, text=translate("tab.inspect", self.locale))
        self.notebook.add(self.change_tab, text=translate("tab.change", self.locale))
        self.notebook.add(self.combine_tab, text=translate("tab.combine", self.locale))

        bottom = ttk.Frame(self.root, padding=(14, 0, 14, 10))
        bottom.pack(fill="both")
        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.log_view = LogView(bottom, locale=self.locale, height=7)
        self.log_view.pack(fill="both", expand=True, pady=(0, 6))
        self.status_label = ttk.Label(bottom, textvariable=self.status_var, style="Status.TLabel", anchor="w")
        self.status_label.pack(fill="x")

    def log(self, level: str, message: str) -> None:
        self.log_view.append(level, message)

    def set_status(self, message: str) -> None:
        self.status_var.set(message.splitlines()[0])

    def run_background(
        self,
        label: str,
        action: Callable[[], object],
        done: Callable[[object], None] | None = None,
    ) -> None:
        self.progress.pack(fill="x", pady=(0, 6))
        self.progress.start(11)
        self.set_status(label)
        self.log("START", label)
        self.notebook.configure(cursor="watch")

        def worker() -> None:
            try:
                result = action()
                self._events.put(("ok", result, done))
            except Exception as exc:  # noqa: BLE001
                details = traceback.format_exc()
                self._events.put(("error", (exc, details), done))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_events(self) -> None:
        try:
            while True:
                kind, payload, done = self._events.get_nowait()
                self.progress.stop()
                self.progress.pack_forget()
                self.notebook.configure(cursor="")
                if kind == "ok":
                    if done:
                        done(payload)
                else:
                    exc, details = payload  # type: ignore[misc]
                    self.log("ERROR", str(exc))
                    if not isinstance(exc, ForgeError):
                        self.log("TRACE", details)
                    if not isinstance(exc, NotCalibratedError):
                        messagebox.showerror(translate("status.failed", self.locale), str(exc))
                self._events.task_done()
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def toggle_language(self) -> None:
        self.locale = "es" if self.locale == "en" else "en"
        self.root.title(translate("app.window_title", self.locale))
        self.lang_button.configure(text=translate("menu.language.toggle", self.locale))
        self.log_view.locale = self.locale
        self.inspect_tab.locale = self.locale
        self.change_tab.locale = self.locale
        self.combine_tab.locale = self.locale
        for index, key in enumerate(("tab.inspect", "tab.change", "tab.combine")):
            self.notebook.tab(index, text=translate(key, self.locale))
        self.set_status(translate("status.ready", self.locale))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CustomItemForgeApp().run()


if __name__ == "__main__":
    main()
