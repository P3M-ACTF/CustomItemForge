"""Hair family engine — recategorize and merge for VRoid 2.x hair items."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.catalog.categories import category_family, resolve_category
from custom_item_forge.core.errors import UnsupportedFormatError
from custom_item_forge.core.model import CompatibilityReport, MergeReport
from custom_item_forge.engines.hair.operations import merge_hair_items, recategorize_hair_item
from custom_item_forge.i18n import translate


class HairEngine:
    family = "hair"
    calibrated = True

    def compatibility(
        self,
        category_id: str | None,
        *,
        language: str = "en",
    ) -> CompatibilityReport:
        family = category_family(category_id)
        if family != self.family:
            return CompatibilityReport(
                family=family,
                can_recategorize=False,
                can_merge=False,
                recategorize_reason=translate("compat.cross_family", language),
                merge_reason=translate("compat.cross_family", language),
                calibrated=False,
            )
        return CompatibilityReport(
            family=self.family,
            can_recategorize=True,
            can_merge=True,
            recategorize_reason=translate("compat.hair_ready", language),
            merge_reason=translate("compat.hair_ready", language),
            calibrated=self.calibrated,
        )

    def recategorize(
        self,
        source: str | Path,
        output: str | Path,
        category: str,
        *,
        force: bool = False,
    ) -> Path:
        target = resolve_category(category)
        if target.family != self.family:
            raise UnsupportedFormatError(translate("error.cross_family_recategorize", "en"))
        return recategorize_hair_item(source, output, category, force=force)

    def merge(
        self,
        base: str | Path,
        addon: str | Path,
        output: str | Path,
        *,
        force: bool = False,
    ) -> MergeReport:
        return merge_hair_items(base, addon, output, force=force)
