"""Compose or regenerate item thumbnails when embedded previews are missing."""

from __future__ import annotations

import io
from pathlib import Path

from custom_item_forge.core.archive import THUMBNAIL_PATH, CustomItemArchive
from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.core.thumbnail import load_thumbnail, load_thumbnail_from_path
from custom_item_forge.ui.thumbnail_display import decode_image_to_png


def _load_png(path: Path) -> bytes | None:
    result = load_thumbnail_from_path(str(path))
    if result.state == ThumbnailState.OK and result.data:
        return decode_image_to_png(result.data)
    return None


def compose_side_by_side_png(left: bytes, right: bytes, *, height: int = 512) -> bytes:
    """Place two PNG previews side by side for merged items."""
    from PIL import Image

    left_img = Image.open(io.BytesIO(left)).convert("RGBA")
    right_img = Image.open(io.BytesIO(right)).convert("RGBA")
    target_h = max(64, height)
    left_img.thumbnail((target_h, target_h), Image.Resampling.LANCZOS)
    right_img.thumbnail((target_h, target_h), Image.Resampling.LANCZOS)
    gap = 8
    canvas = Image.new(
        "RGBA",
        (left_img.width + gap + right_img.width, max(left_img.height, right_img.height)),
        (245, 245, 245, 255),
    )
    canvas.paste(left_img, (0, (canvas.height - left_img.height) // 2), left_img)
    offset_x = left_img.width + gap
    canvas.paste(right_img, (offset_x, (canvas.height - right_img.height) // 2), right_img)
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def compose_merge_thumbnail(
    base_path: str | Path,
    addon_path: str | Path,
    *,
    height: int = 512,
) -> bytes | None:
    """Build a merge preview thumbnail from base + add-on embedded PNGs."""
    base_png = _load_png(Path(base_path))
    addon_png = _load_png(Path(addon_path))
    if base_png and addon_png:
        return compose_side_by_side_png(base_png, addon_png, height=height)
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
