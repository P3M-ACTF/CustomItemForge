from __future__ import annotations

from pathlib import Path

import pytest

from custom_item_forge.core.errors import NotCalibratedError
from custom_item_forge.engines.accessory.engine import AccessoryEngine
from custom_item_forge.engines.clothing.engine import ClothingEngine
from custom_item_forge.engines.hair.engine import HairEngine
from custom_item_forge.engines.router import FamilyRouter
from tests.fixtures.synthetic.builder import build_minimal_item


def test_hair_engine_calibrated() -> None:
    engine = HairEngine()
    assert engine.calibrated is True
    report = engine.compatibility("TransferableGroupType.N00.Level1.HairBack", language="en")
    assert report.can_recategorize is True
    assert report.can_merge is True


def test_merge_report_includes_family(tmp_path: Path) -> None:
    from custom_item_forge.core.model import MergeReport

    report = MergeReport(
        base=tmp_path / "a.vroidcustomitem",
        addon=tmp_path / "b.vroidcustomitem",
        output=tmp_path / "out.vroidcustomitem",
        family="hair",
        base_root_entry="group",
        addon_root_entry="group2",
    )
    assert report.family == "hair"


def test_hair_engine_still_blocks_cross_family(tmp_path: Path) -> None:
    path = build_minimal_item(tmp_path / "hair.vroidcustomitem")
    engine = HairEngine()
    with pytest.raises(Exception):
        engine.recategorize(path, tmp_path / "out.vroidcustomitem", "tops", force=True)


def test_router_compatibility_unknown() -> None:
    report = FamilyRouter().compatibility(None, language="en")
    assert report.can_recategorize is False
    assert report.can_merge is False


def test_cross_family_blocked() -> None:
    hair = HairEngine()
    report = hair.compatibility("TransferableGroupType.N00.Level1.Tops", language="en")
    assert report.can_recategorize is False
    assert "Cross-family" in report.recategorize_reason or "bloqueadas" not in report.recategorize_reason


def test_accessory_engine_stub() -> None:
    engine = AccessoryEngine()
    report = engine.compatibility("TransferableGroupType.N00.Level1.Glasses", language="en")
    assert report.family == "accessory"
    assert report.calibrated is False
    with pytest.raises(NotCalibratedError):
        engine.merge(
            __import__("pathlib").Path("x"),
            __import__("pathlib").Path("y"),
            __import__("pathlib").Path("z"),
            force=True,
        )


def test_clothing_engine_stub() -> None:
    engine = ClothingEngine()
    report = engine.compatibility("TransferableGroupType.N00.Level1.Tops", language="en")
    assert report.family == "clothing"
