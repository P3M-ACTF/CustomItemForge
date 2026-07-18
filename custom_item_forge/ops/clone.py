"""Clone / repackage."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.core.archive import CustomItemArchive, write_transformed_archive


def clone_item(
    source: str | Path,
    output: str | Path,
    *,
    force: bool = False,
) -> Path:
    with CustomItemArchive(source) as archive:
        return write_transformed_archive(archive, output, force=force)
