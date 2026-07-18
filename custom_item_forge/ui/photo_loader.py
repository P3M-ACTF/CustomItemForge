"""Render PNG bytes into Tk PhotoImage with optional Pillow scaling."""

from __future__ import annotations

import io
import math
import tkinter as tk


def photo_from_png(png_bytes: bytes, *, max_width: int, max_height: int) -> tk.PhotoImage | None:
    try:
        from PIL import Image, ImageTk

        image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except ImportError:
        pass
    except Exception:
        return None

    try:
        photo = tk.PhotoImage(data=png_bytes)
    except tk.TclError:
        return None
    factor = max(
        1,
        math.ceil(photo.width() / max_width),
        math.ceil(photo.height() / max_height),
    )
    return photo.subsample(factor, factor) if factor > 1 else photo
