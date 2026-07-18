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
from custom_item_forge.ui.components.app_header import AppHeader
from custom_item_forge.ui.components.log_view import LogView
from custom_item_forge.ui.tabs.combine_tab import CombineTab
from custom_item_forge.ui.tabs.inspect_change_workspace import InspectChangeWorkspace
from custom_item_forge.ui.themes.simple.styles import apply_simple_theme


class CustomItemForgeApp:
    _LOG_HEIGHT = 5

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.locale = "en"
        self._log_visible = False
        self._active_tab = "inspect"
        apply_simple_theme(self.root)
        self.root.geometry("1180x760")
        self.root.minsize(940, 620)
        self.root.title(translate("app.window_title", self.locale))

        self.status_var = tk.StringVar(value=translate("status.ready", self.locale))
        self._events: queue.Queue[tuple[str, object, Callable[[object], None] | None]] = queue.Queue()

        self._build_ui()
        self.root.after(100, self._poll_events)

    def _build_ui(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.header = AppHeader(
            self.root,
            locale=self.locale,
            on_language=self.toggle_language,
            on_tab=self._select_tab,
        )
        self.header.grid(row=0, column=0, sticky="ew")

        self.content = ttk.Frame(self.root, padding=(4, 0, 4, 0))
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        shared = {
            "locale": self.locale,
            "log": self.log,
            "set_status": self.set_status,
            "run_background": self.run_background,
        }
        self.workspace = InspectChangeWorkspace(self.content, **shared)
        self.combine_tab = CombineTab(self.content, **shared)
        self.workspace.grid(row=0, column=0, sticky="nsew")
        self.combine_tab.grid(row=0, column=0, sticky="nsew")
        self.combine_tab.grid_remove()

        self.log_frame = ttk.Frame(self.root, padding=(8, 0, 8, 0))
        self.log_view = LogView(self.log_frame, locale=self.locale, height=self._LOG_HEIGHT)
        self.log_view.pack(fill="x")

        self.bottom = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        self.bottom.grid(row=3, column=0, sticky="ew")
        self.progress = ttk.Progressbar(self.bottom, mode="indeterminate")

        status_row = ttk.Frame(self.bottom)
        status_row.pack(fill="x")
        self.log_toggle_btn = ttk.Button(
            status_row,
            text=translate("menu.log.show", self.locale),
            width=8,
            command=self.toggle_log,
        )
        self.log_toggle_btn.pack(side="right")
        self.status_label = ttk.Label(
            status_row,
            textvariable=self.status_var,
            style="Status.TLabel",
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

    def _select_tab(self, tab_id: str) -> None:
        self._active_tab = tab_id
        if tab_id == "combine":
            self.workspace.grid_remove()
            self.combine_tab.grid()
        else:
            self.combine_tab.grid_remove()
            self.workspace.grid()
            self.workspace.set_mode(tab_id)

    def toggle_log(self) -> None:
        self._log_visible = not self._log_visible
        if self._log_visible:
            self.log_frame.grid(row=2, column=0, sticky="ew")
            self.log_toggle_btn.configure(text=translate("menu.log.hide", self.locale))
        else:
            self.log_frame.grid_remove()
            self.log_toggle_btn.configure(text=translate("menu.log.show", self.locale))

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
        self.progress.pack(fill="x", pady=(0, 4), before=self.log_toggle_btn.master)
        self.progress.start(8)
        self.set_status(label)
        self.log("START", label)
        self.content.configure(cursor="watch")

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
                self.content.configure(cursor="")
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
        self.header.locale = self.locale
        self.log_view.locale = self.locale
        self.workspace.locale = self.locale
        self.combine_tab.locale = self.locale
        self.log_toggle_btn.configure(
            text=translate("menu.log.hide" if self._log_visible else "menu.log.show", self.locale)
        )
        self.set_status(translate("status.ready", self.locale))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CustomItemForgeApp().run()


if __name__ == "__main__":
    main()
