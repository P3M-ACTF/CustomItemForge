"""Validate wrapper."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.core.archive import validate_archive
from custom_item_forge.core.model import ValidationReport


def validate_item(path: str | Path, *, verify_crc: bool = True) -> ValidationReport:
    return validate_archive(path, verify_crc=verify_crc)
