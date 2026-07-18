from __future__ import annotations

import io
from pathlib import Path

import pytest

from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.ui.assets.fallback_icons import fallback_png
from custom_item_forge.ui.thumbnail_display import decode_image_to_png, resolve_display_png
from tests.fixtures.synthetic.builder import PNG_1X1, build_minimal_item


def test_decode_png_passthrough() -> None:
    assert decode_image_to_png(PNG_1X1) == PNG_1X1


def test_decode_jpeg_to_png() -> None:
    pytest.importorskip("PIL")
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (12, 12), (220, 40, 40)).save(buffer, format="JPEG")
    jpeg = buffer.getvalue()
    png = decode_image_to_png(jpeg)
    assert png is not None
    assert png.startswith(b"\x89PNG")


def test_resolve_embedded_jpeg_item(tmp_path: Path) -> None:
    pytest.importorskip("PIL")
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (40, 120, 200)).save(buffer, format="JPEG")
    path = build_minimal_item(
        tmp_path / "jpeg-thumb.vroidcustomitem",
        thumbnail_bytes=buffer.getvalue(),
    )
    from custom_item_forge.core.thumbnail import load_thumbnail_from_path

    loaded = load_thumbnail_from_path(str(path))
    png, used_fallback = resolve_display_png(
        state=loaded.state,
        raw_bytes=loaded.data,
        family="hair",
    )
    assert png is not None
    assert png.startswith(b"\x89PNG")
    assert used_fallback is False


def test_resolve_missing_uses_family_fallback() -> None:
    png, used_fallback = resolve_display_png(
        state=ThumbnailState.MISSING,
        raw_bytes=None,
        family="accessory",
    )
    assert png is not None
    assert png.startswith(b"\x89PNG")
    assert used_fallback is True


def test_resolve_unreadable_uses_fallback() -> None:
    png, used_fallback = resolve_display_png(
        state=ThumbnailState.UNREADABLE,
        raw_bytes=b"not-an-image",
        family="clothing",
    )
    assert png is not None
    assert used_fallback is True


def test_fallback_png_varies_by_family() -> None:
    pytest.importorskip("PIL")
    hair = fallback_png("hair")
    clothing = fallback_png("clothing")
    assert hair.startswith(b"\x89PNG")
    assert clothing.startswith(b"\x89PNG")
    assert hair != clothing
