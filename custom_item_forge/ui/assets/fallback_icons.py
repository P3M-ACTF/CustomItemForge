"""Family placeholder icons when embedded thumbnails are missing."""

from __future__ import annotations

_PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

_CACHE: dict[str, bytes] | None = None


def _build_cache() -> dict[str, bytes]:
    palette = {
        "hair": (176, 196, 222),
        "clothing": (143, 188, 143),
        "accessory": (186, 170, 211),
        "unknown": (192, 192, 192),
    }
    try:
        import io

        from PIL import Image, ImageDraw

        icons: dict[str, bytes] = {}
        for family, color in palette.items():
            image = Image.new("RGBA", (96, 96), color + (255,))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((12, 12, 83, 83), radius=14, fill=(255, 255, 255, 210))
            letter = {"hair": "H", "clothing": "C", "accessory": "A", "unknown": "?"}[family]
            draw.text((38, 30), letter, fill=(60, 60, 60, 255))
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            icons[family] = buffer.getvalue()
        return icons
    except ImportError:
        return {family: _PNG_1X1 for family in palette}


def fallback_png(family: str | None) -> bytes:
    global _CACHE  # noqa: PLW0603
    if _CACHE is None:
        _CACHE = _build_cache()
    key = family if family in _CACHE else "unknown"
    return _CACHE[key]
