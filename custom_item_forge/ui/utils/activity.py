"""Shared log/status helpers for loaded items."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from custom_item_forge.core.model import InspectReport
from custom_item_forge.i18n import translate


def report_inspected(
    log: Callable[[str, str], None],
    set_status: Callable[[str], None],
    locale: str,
    path: str | Path,
    report: InspectReport,
    *,
    slot: str | None = None,
) -> str:
    category = report.field_map("vroid").get("category_label", "—")
    entries = report.field_map("file").get("entry_count", 0)
    name = Path(path).name
    if slot:
        message = translate(
            "status.inspected_slot",
            locale,
            slot=slot,
            name=name,
            category=category,
            entries=entries,
        )
    else:
        message = translate(
            "status.inspected",
            locale,
            name=name,
            category=category,
            entries=entries,
        )
    log("INFO", message)
    set_status(message)
    return message
