"""Clothing family engine (merge awaits real Studio samples)."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.catalog.categories import category_family, resolve_category
from custom_item_forge.core.errors import NotCalibratedError, UnsupportedFormatError
from custom_item_forge.core.model import CompatibilityReport, MergeReport
from custom_item_forge.engines.common import recategorize_item
from custom_item_forge.i18n import translate


class ClothingEngine:
    family = "clothing"
    # Recategorize uses the shared category rewrite; merge needs real Tops/etc. samples.
    calibrated = False
    recategorize_ready = True

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
            can_recategorize=self.recategorize_ready,
            can_merge=False,
            recategorize_reason=translate("compat.clothing_recategorize", language),
            merge_reason=translate("compat.awaiting_calibration", language, family=self.family),
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
        return recategorize_item(
            source,
            output,
            category,
            expected_family=self.family,
            force=force,
        )

    def merge(
        self,
        base: str | Path,
        addon: str | Path,
        output: str | Path,
        *,
        force: bool = False,
    ) -> MergeReport:
        raise NotCalibratedError(
            translate("error.not_calibrated", "en", family=self.family, operation="merge")
        )
