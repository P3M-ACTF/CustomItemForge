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


def _rgba_png(size: int, color: tuple[int, int, int, int], box: tuple[int, int, int, int]) -> bytes:
    from PIL import Image

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for x in range(box[0], box[2]):
        for y in range(box[1], box[3]):
            image.putpixel((x, y), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_compose_overlay_square_is_square_and_keeps_both_layers() -> None:
    pytest.importorskip("PIL")
    from PIL import Image

    from custom_item_forge.core.thumbnail_compose import compose_overlay_square_png

    # Opaque red patch top-left, opaque blue patch bottom-right.
    base = _rgba_png(128, (220, 40, 40, 255), (0, 0, 40, 40))
    addon = _rgba_png(128, (40, 80, 220, 255), (88, 88, 128, 128))
    merged = compose_overlay_square_png(base, addon, size=256)
    image = Image.open(io.BytesIO(merged))
    assert image.size == (256, 256)
    assert image.mode == "RGBA"
    # Sample near the painted regions after fit/centering on 256 canvas (1:1 scale of 128→centered).
    # 128 fitted into 256 is centered with offset 64; patches map accordingly.
    red = image.getpixel((64 + 10, 64 + 10))
    blue = image.getpixel((64 + 100, 64 + 100))
    assert red[0] > 180 and red[2] < 80
    assert blue[2] > 180 and blue[0] < 80


def test_compose_overlay_knockouts_opaque_studio_background() -> None:
    """Studio thumbs are opaque #F5F5F5; without knockout the add-on hides the base."""
    pytest.importorskip("PIL")
    from PIL import Image

    from custom_item_forge.core.thumbnail_compose import compose_overlay_square_png

    def opaque_subject(size: int, color: tuple[int, int, int], box: tuple[int, int, int, int]) -> bytes:
        image = Image.new("RGBA", (size, size), (245, 245, 245, 255))
        for x in range(box[0], box[2]):
            for y in range(box[1], box[3]):
                image.putpixel((x, y), (*color, 255))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    base = opaque_subject(128, (20, 20, 20), (0, 40, 30, 80))
    addon = opaque_subject(128, (180, 100, 40), (98, 40, 128, 80))
    merged = compose_overlay_square_png(base, addon, size=128)
    image = Image.open(io.BytesIO(merged))
    has_dark = any(
        image.getpixel((x, y))[0] < 50 and image.getpixel((x, y))[1] < 50
        for y in range(image.height)
        for x in range(image.width)
    )
    has_brown = any(
        image.getpixel((x, y))[0] > 150 and image.getpixel((x, y))[2] < 80
        for y in range(image.height)
        for x in range(image.width)
    )
    assert has_dark
    assert has_brown


def test_compose_overlay_reframes_wide_subjects(tmp_path: Path) -> None:
    """Edge-to-edge strips should be reframed with padding, not left full-width."""
    pytest.importorskip("PIL")
    from PIL import Image

    from custom_item_forge.core.thumbnail_compose import compose_overlay_square_png

    def strip_thumb(y0: int, y1: int, color: tuple[int, int, int]) -> bytes:
        image = Image.new("RGBA", (512, 512), (245, 245, 245, 255))
        for x in range(0, 512, 64):
            for y in range(y0, y1):
                image.putpixel((x, y), (*color, 255))
                image.putpixel((511 - x, y), (*color, 255))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    merged = compose_overlay_square_png(
        strip_thumb(200, 240, (20, 20, 20)),
        strip_thumb(260, 320, (160, 90, 40)),
        size=512,
    )
    image = Image.open(io.BytesIO(merged))
    assert image.size == (512, 512)
    # Subject should not span the full width after reframe (was ~512px wide before).
    xs = [x for y in range(512) for x in range(512) if image.getpixel((x, y))[3] > 20 and image.getpixel((x, y))[:3] != (245, 245, 245)]
    assert xs
    assert max(xs) - min(xs) < 450


def test_compose_merge_thumbnail_writes_square_png(tmp_path: Path) -> None:
    pytest.importorskip("PIL")
    from PIL import Image

    from custom_item_forge.core.thumbnail_compose import compose_merge_thumbnail

    base_thumb = _rgba_png(512, (10, 10, 10, 255), (20, 20, 80, 80))
    addon_thumb = _rgba_png(512, (200, 200, 50, 255), (400, 400, 480, 480))
    base = build_minimal_item(tmp_path / "base.vroidcustomitem", thumbnail_bytes=base_thumb)
    addon = build_minimal_item(tmp_path / "addon.vroidcustomitem", thumbnail_bytes=addon_thumb)
    composed = compose_merge_thumbnail(base, addon)
    assert composed is not None
    image = Image.open(io.BytesIO(composed))
    assert image.size == (512, 512)
