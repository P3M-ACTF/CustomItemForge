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


def test_remap_material_slot_indices_increments_small_varints() -> None:
    from custom_item_forge.core.protobuf_wire import encode_field, parse_fields
    from custom_item_forge.engines.hair.merge import (
        HairReferenceMaps,
        remap_addon_references,
    )

    maps = HairReferenceMaps(
        base_bt_count=1,
        addon_bt_count=1,
        bt_slot={1: 2},
        storage_f1={2: 3},
        storage_f8={1: 38},
        storage_f9={1: 1},
    )
    geometry = encode_field(8, 0, 1) + encode_field(6, 0, 1)
    remapped = remap_addon_references(geometry, maps, root="geometry")
    values = {
        field.number: field.value
        for field in parse_fields(remapped)
        if field.wire_type == 0 and isinstance(field.value, int)
    }
    assert values[8] == 38
    assert values[6] == 1

    strand = encode_field(6, 0, 1) + encode_field(6, 0, 3)
    remapped_strand = remap_addon_references(strand, maps, root="strand")
    strand_values = [
        field.value
        for field in parse_fields(remapped_strand)
        if field.number == 6 and isinstance(field.value, int)
    ]
    assert strand_values == [2, 4]

    material_geom = encode_field(
        5,
        2,
        encode_field(3, 2, encode_field(6, 0, 1)),
    )
    remapped_mat = remap_addon_references(material_geom, maps, root="geometry")
    nested = parse_fields(parse_fields(remapped_mat)[0].value)  # type: ignore[arg-type]
    inner = parse_fields(nested[0].value)  # type: ignore[arg-type]
    assert inner[0].value == 2
