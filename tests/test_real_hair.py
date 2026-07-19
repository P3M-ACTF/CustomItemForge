"""Golden tests against real Studio 2.14.0 hair fixtures (gitignored)."""

from __future__ import annotations

from pathlib import Path

import pytest

from custom_item_forge.core.archive import CustomItemArchive
from custom_item_forge.engines.hair.engine import HairEngine
from custom_item_forge.ops.inspect import inspect_item
from custom_item_forge.ops.probe import probe_item

HAIR_DIR = Path(__file__).resolve().parent / "fixtures" / "real" / "hair"


def _hair_files() -> list[Path]:
    if not HAIR_DIR.is_dir():
        return []
    return sorted(HAIR_DIR.glob("*.vroidcustomitem"))


pytestmark = pytest.mark.skipif(
    not _hair_files(),
    reason="Real hair fixtures not present under tests/fixtures/real/hair/",
)


def test_all_hair_fixtures_single_category() -> None:
    """Each export is one category — Back is not coupled to Base inside the ZIP (H1)."""
    for path in _hair_files():
        with CustomItemArchive(path) as archive:
            assert archive.category_id is not None
            suffix = archive.category_id.rsplit(".", 1)[-1]
            xfers = [
                name
                for name in archive.names
                if name.startswith("v1customitem/transferables/") and not name.endswith("/")
            ]
            groups = [
                name
                for name in archive.names
                if name.startswith("v1customitem/transferablegroups/") and not name.endswith("/")
            ]
            assert len(xfers) == 1, f"{path.name}: expected 1 transferable, got {len(xfers)}"
            assert len(groups) == 1, f"{path.name}: expected 1 group, got {len(groups)}"
            if path.name.startswith("Back"):
                assert suffix == "HairBack"
            if path.name.startswith("Base"):
                assert suffix == "BaseHair"


def test_back_vs_base_are_distinct_categories() -> None:
    back_b = HAIR_DIR / "BackB.vroidcustomitem"
    base_b = HAIR_DIR / "BaseB.vroidcustomitem"
    assert back_b.is_file() and base_b.is_file()
    with CustomItemArchive(back_b) as back, CustomItemArchive(base_b) as base:
        assert back.category_id.endswith("HairBack")
        assert base.category_id.endswith("BaseHair")
        assert back.category_id != base.category_id
    back_probe = probe_item(back_b)[0]
    base_probe = probe_item(base_b)[0]
    assert back_probe["group_edit_type"] == "TransferableGroupEditType.Hair"
    assert base_probe["group_edit_type"] == "TransferableGroupEditType.BaseHair"
    assert "BaseHair" not in (back_probe.get("category_text") or "")


def test_inspect_front_reports_hair_family() -> None:
    path = HAIR_DIR / "FrontA.vroidcustomitem"
    report = inspect_item(path)
    payload = report.to_dict()
    fields = {
        field["key"]: field["value"]
        for section in payload["sections"]
        for field in section["fields"]
    }
    assert fields["family"] == "hair"
    assert "Front" in str(fields.get("category_label", ""))


def test_merge_extra_a_and_b(tmp_path: Path) -> None:
    engine = HairEngine()
    output = tmp_path / "merged-extra.vroidcustomitem"
    report = engine.merge(
        HAIR_DIR / "ExtraA.vroidcustomitem",
        HAIR_DIR / "ExtraB.vroidcustomitem",
        output,
        force=True,
    )
    assert report.family == "hair"
    assert output.is_file()
    with CustomItemArchive(output) as archive:
        assert archive.category_id.endswith("HairHanege")


def test_recategorize_front_to_back(tmp_path: Path) -> None:
    engine = HairEngine()
    output = tmp_path / "front-as-back.vroidcustomitem"
    result = engine.recategorize(
        HAIR_DIR / "FrontA.vroidcustomitem",
        output,
        "hair-back",
        force=True,
    )
    with CustomItemArchive(result) as archive:
        assert archive.category_id.endswith("HairBack")


def test_extra_resaved_same_category() -> None:
    original = HAIR_DIR / "ExtraA.vroidcustomitem"
    resaved = HAIR_DIR / "ExtraA_resaved.vroidcustomitem"
    assert original.is_file() and resaved.is_file()
    with CustomItemArchive(original) as left, CustomItemArchive(resaved) as right:
        assert left.category_id == right.category_id
        assert left.category_id.endswith("HairHanege")
