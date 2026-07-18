"""Probe root group candidates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from custom_item_forge.core.archive import CustomItemArchive
from custom_item_forge.core.probe import probe_root_groups


def probe_item(path: str | Path) -> list[dict[str, Any]]:
    with CustomItemArchive(path) as archive:
        return [candidate.to_dict() for candidate in probe_root_groups(archive)]
