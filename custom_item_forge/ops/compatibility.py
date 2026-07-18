"""Compatibility summary for an item."""

from __future__ import annotations

from custom_item_forge.core.model import CompatibilityReport
from custom_item_forge.engines.router import FamilyRouter


def compatibility_report(category_id: str | None, *, language: str = "en") -> CompatibilityReport:
    return FamilyRouter().compatibility(category_id, language=language)
