"""Simple theme styles for CustomItemForge."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_simple_theme(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("Meta.TLabel", font=("Segoe UI", 9), foreground="#666")
    style.configure("Card.TLabelframe", padding=6)
    style.configure("Section.TButton", padding=(2, 0))
    style.configure("Icon.TButton", padding=(0, 0))
    style.configure("Warning.TLabel", foreground="#9a5700", font=("Segoe UI", 9, "bold"))
    style.configure("Status.TLabel", padding=(4, 4))
    return style
