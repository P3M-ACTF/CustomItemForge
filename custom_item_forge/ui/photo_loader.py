"""Render PNG bytes into Tk PhotoImage with optional Pillow scaling."""

from __future__ import annotations

import io
import math
import tkinter as tk


def photo_from_png(png_bytes: bytes, *, max_width: int, max_height: int) -> tk.PhotoImage | None:
    if max_width < 1 or max_height < 1:
        return None
    try:
        from PIL import Image, ImageTk

        image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        width, height = image.size
        if width <= 0 or height <= 0:
            return None
        scale = min(max_width / width, max_height / height)
        target = (max(1, int(width * scale)), max(1, int(height * scale)))
        if target != (width, height):
            image = image.resize(target, Image.Resampling.LANCZOS)
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
