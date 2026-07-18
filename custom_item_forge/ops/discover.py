"""Discover .vroidcustomitem files in paths."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.core.errors import InvalidArchiveError, UnsupportedFormatError


def discover_items(path: str | Path) -> list[Path]:
    resolved = Path(path).expanduser().resolve()
    if resolved.is_dir():
        return sorted(resolved.rglob("*.vroidcustomitem"), key=lambda item: str(item).lower())
    if resolved.is_file() and resolved.suffix.lower() == ".vroidcustomitem":
        return [resolved]
    if resolved.is_file() and resolved.suffix.lower() == ".vroid":
        raise UnsupportedFormatError(
            "This .vroid model does not expose standalone .vroidcustomitem files. "
            "Export the desired item from VRoid Studio first."
        )
    raise InvalidArchiveError(f"Path not found or unsupported: {resolved}")
