"""Simple theme styles for CustomItemForge."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_simple_theme(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
    style.configure("Card.TLabelframe", padding=10)
    style.configure("Warning.TLabel", foreground="#9a5700", font=("Segoe UI", 9, "bold"))
    style.configure("Status.TLabel", padding=(9, 5))
    return style
