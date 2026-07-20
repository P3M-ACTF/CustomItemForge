"""Compose or regenerate item thumbnails when embedded previews are missing."""

from __future__ import annotations

import io
from pathlib import Path

from custom_item_forge.core.archive import CustomItemArchive
from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.core.thumbnail import load_thumbnail, load_thumbnail_from_path
from custom_item_forge.ui.thumbnail_display import decode_image_to_png

# Studio custom-item grid expects roughly square previews (~512×512).
DEFAULT_MERGE_THUMB_SIZE = 512
_CANVAS_BG = (245, 245, 245, 255)


def _load_png(path: Path) -> bytes | None:
    result = load_thumbnail_from_path(str(path))
    if result.state == ThumbnailState.OK and result.data:
        return decode_image_to_png(result.data)
    return None


def _fit_centered(image, size: int):
    from PIL import Image

    fitted = image.copy()
    fitted.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - fitted.width) // 2, (size - fitted.height) // 2)
    canvas.paste(fitted, offset, fitted)
    return canvas


def compose_overlay_square_png(
    base: bytes,
    addon: bytes,
    *,
    size: int = DEFAULT_MERGE_THUMB_SIZE,
) -> bytes:
    """Overlay two PNG previews on a square canvas (Studio-friendly aspect)."""
    from PIL import Image

    side = max(64, size)
    base_img = Image.open(io.BytesIO(base)).convert("RGBA")
    addon_img = Image.open(io.BytesIO(addon)).convert("RGBA")
    canvas = Image.new("RGBA", (side, side), _CANVAS_BG)
    canvas.alpha_composite(_fit_centered(base_img, side))
    canvas.alpha_composite(_fit_centered(addon_img, side))
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def compose_merge_thumbnail(
    base_path: str | Path,
    addon_path: str | Path,
    *,
    size: int = DEFAULT_MERGE_THUMB_SIZE,
    height: int | None = None,
) -> bytes | None:
    """Build a square merge preview thumbnail from base + add-on embedded PNGs.

    ``height`` is accepted as a deprecated alias for ``size`` (older call sites).
    """
    side = size if height is None else height
    base_png = _load_png(Path(base_path))
    addon_png = _load_png(Path(addon_path))
    if base_png and addon_png:
        return compose_overlay_square_png(base_png, addon_png, size=side)
    return base_png or addon_png


def ensure_item_thumbnail(
    path: str | Path,
    *,
    family: str | None = None,
) -> bytes | None:
    """Return embedded PNG bytes, or a generated fallback when missing."""
    resolved = Path(path).expanduser().resolve()
    with CustomItemArchive(resolved) as archive:
        result = load_thumbnail(archive)
    if result.state == ThumbnailState.OK and result.data:
        decoded = decode_image_to_png(result.data)
        if decoded is not None:
            return decoded
    from custom_item_forge.ui.thumbnail_display import resolve_display_png

    png, _used = resolve_display_png(
        state=ThumbnailState.MISSING,
        raw_bytes=None,
        family=family,
        use_fallback=True,
    )
    return png
