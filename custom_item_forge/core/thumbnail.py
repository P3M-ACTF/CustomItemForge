"""Embedded thumbnail loading with explicit states."""

from __future__ import annotations

from dataclasses import dataclass

from custom_item_forge.core.archive import THUMBNAIL_PATH, CustomItemArchive
from custom_item_forge.core.model import ThumbnailState

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_THUMBNAIL_BYTES = 32 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class ThumbnailResult:
    state: ThumbnailState
    data: bytes | None = None
    reason: str | None = None


def _looks_like_png(data: bytes) -> bool:
    if not data.startswith(PNG_SIGNATURE) or len(data) < 24:
        return False
    # IHDR chunk must follow the signature.
    return data[12:16] == b"IHDR"


def load_thumbnail(archive: CustomItemArchive) -> ThumbnailResult:
    if THUMBNAIL_PATH not in archive.infos:
        return ThumbnailResult(ThumbnailState.MISSING, reason="no_thumbnail_entry")

    try:
        data = archive.read_bytes(THUMBNAIL_PATH, limit=MAX_THUMBNAIL_BYTES)
    except Exception as exc:  # noqa: BLE001 — surface as unreadable, never crash callers
        return ThumbnailResult(
            ThumbnailState.UNREADABLE,
            reason=f"read_failed:{exc}",
        )

    if not data:
        return ThumbnailResult(ThumbnailState.UNREADABLE, reason="empty_thumbnail")

    if _looks_like_png(data):
        return ThumbnailResult(ThumbnailState.OK, data=data)

    # Accept other common image headers conservatively.
    if data.startswith(b"\xff\xd8\xff"):
        return ThumbnailResult(ThumbnailState.OK, data=data)
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ThumbnailResult(ThumbnailState.OK, data=data)
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ThumbnailResult(ThumbnailState.OK, data=data)

    return ThumbnailResult(ThumbnailState.UNREADABLE, reason="unsupported_image_format")


def load_thumbnail_from_path(path: str) -> ThumbnailResult:
    with CustomItemArchive(path) as archive:
        return load_thumbnail(archive)
