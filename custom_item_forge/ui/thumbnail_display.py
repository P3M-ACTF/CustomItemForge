"""Prepare embedded thumbnails for Tk display."""

from __future__ import annotations

import io

from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.core.thumbnail import _looks_like_png
from custom_item_forge.ui.assets.fallback_icons import fallback_png


def decode_image_to_png(data: bytes) -> bytes | None:
    if _looks_like_png(data) or data[:6] in (b"GIF87a", b"GIF89a"):
        return data
    try:
        from PIL import Image

        image = Image.open(io.BytesIO(data))
        image = image.convert("RGBA")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except ImportError:
        return None
    except Exception:
        return None


def resolve_display_png(
    *,
    state: ThumbnailState,
    raw_bytes: bytes | None,
    family: str | None,
    use_fallback: bool = True,
) -> tuple[bytes | None, bool]:
    """Return PNG bytes and whether a family fallback was used."""
    if state is ThumbnailState.OK and raw_bytes:
        decoded = decode_image_to_png(raw_bytes)
        if decoded is not None:
            return decoded, False
    if use_fallback:
        return fallback_png(family), True
    return None, False
