"""Structural comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from custom_item_forge.core.archive import CustomItemArchive
from custom_item_forge.catalog.categories import category_family, category_label
from custom_item_forge.ops.inspect import inspect_item


def compare_items(
    left: str | Path,
    right: str | Path,
    *,
    language: str = "en",
) -> dict[str, Any]:
    left_path = Path(left).expanduser().resolve()
    right_path = Path(right).expanduser().resolve()
    left_report = inspect_item(left_path, language=language)
    right_report = inspect_item(right_path, language=language)

    with CustomItemArchive(left_path) as first, CustomItemArchive(right_path) as second:
        first_names = set(first.names)
        second_names = set(second.names)
        shared = sorted(first_names & second_names)
        changed = []
        for name in shared:
            a = first.infos[name]
            b = second.infos[name]
            if (a.file_size, a.CRC) != (b.file_size, b.CRC):
                changed.append(
                    {
                        "entry": name,
                        "left_size": a.file_size,
                        "right_size": b.file_size,
                        "left_crc32": f"{a.CRC:08x}",
                        "right_crc32": f"{b.CRC:08x}",
                    }
                )

        return {
            "left": str(first.path),
            "right": str(second.path),
            "left_inspect": left_report.to_dict(),
            "right_inspect": right_report.to_dict(),
            "left_category": first.category_id,
            "right_category": second.category_id,
            "left_category_label": category_label(first.category_id, language),
            "right_category_label": category_label(second.category_id, language),
            "left_family": category_family(first.category_id),
            "right_family": category_family(second.category_id),
            "only_left": sorted(first_names - second_names),
            "only_right": sorted(second_names - first_names),
            "changed": changed,
            "metadata_equal": first.metadata == second.metadata,
        }
