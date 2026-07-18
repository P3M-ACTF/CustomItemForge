"""Route operations to family engines."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.catalog.categories import category_family
from custom_item_forge.core.errors import NotCalibratedError, UnsupportedFormatError
from custom_item_forge.core.model import CompatibilityReport, MergeReport
from custom_item_forge.engines.accessory.engine import AccessoryEngine
from custom_item_forge.engines.clothing.engine import ClothingEngine
from custom_item_forge.engines.hair.engine import HairEngine
from custom_item_forge.i18n import translate


class FamilyRouter:
    def __init__(self) -> None:
        self._engines = {
            "hair": HairEngine(),
            "clothing": ClothingEngine(),
            "accessory": AccessoryEngine(),
        }

    def engine_for(self, category_id: str | None):
        family = category_family(category_id)
        if family is None:
            raise UnsupportedFormatError(
                translate("error.unknown_family", "en", category=category_id or "none")
            )
        engine = self._engines.get(family)
        if engine is None:
            raise UnsupportedFormatError(
                translate("error.unsupported_family", "en", family=family)
            )
        return engine

    def compatibility(
        self,
        category_id: str | None,
        *,
        language: str = "en",
    ) -> CompatibilityReport:
        family = category_family(category_id)
        if family is None:
            return CompatibilityReport(
                family=None,
                can_recategorize=False,
                can_merge=False,
                recategorize_reason=translate("compat.unknown_category", language),
                merge_reason=translate("compat.unknown_category", language),
                calibrated=False,
            )
        return self._engines[family].compatibility(category_id, language=language)

    def recategorize(
        self,
        source: str | Path,
        output: str | Path,
        category: str,
        *,
        category_id: str | None = None,
        force: bool = False,
    ) -> Path:
        if category_id is None:
            from custom_item_forge.core.archive import CustomItemArchive

            with CustomItemArchive(source) as archive:
                category_id = archive.category_id
        engine = self.engine_for(category_id)
        return engine.recategorize(source, output, category, force=force)

    def merge(
        self,
        base: str | Path,
        addon: str | Path,
        output: str | Path,
        *,
        base_category_id: str | None = None,
        force: bool = False,
    ) -> MergeReport:
        if base_category_id is None:
            from custom_item_forge.core.archive import CustomItemArchive

            with CustomItemArchive(base) as archive:
                base_category_id = archive.category_id
        engine = self.engine_for(base_category_id)
        return engine.merge(base, addon, output, force=force)
