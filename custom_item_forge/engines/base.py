"""Family engine protocol."""

from __future__ import annotations

from typing import Protocol

from custom_item_forge.core.model import CompatibilityReport, MergeReport
from pathlib import Path


class FamilyEngine(Protocol):
    family: str
    calibrated: bool

    def compatibility(self, category_id: str | None, *, language: str = "en") -> CompatibilityReport:
        ...

    def recategorize(
        self,
        source: str | Path,
        output: str | Path,
        category: str,
        *,
        force: bool = False,
    ) -> Path:
        ...

    def merge(
        self,
        base: str | Path,
        addon: str | Path,
        output: str | Path,
        *,
        force: bool = False,
    ) -> MergeReport:
        ...
