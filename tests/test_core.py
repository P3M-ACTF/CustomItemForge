from __future__ import annotations

from pathlib import Path

import pytest

from custom_item_forge.core.archive import CustomItemArchive, validate_archive
from custom_item_forge.core.model import ThumbnailState
from custom_item_forge.core.thumbnail import load_thumbnail
from custom_item_forge.ops.clone import clone_item
from custom_item_forge.ops.inspect import inspect_item
from tests.fixtures.synthetic.builder import build_minimal_item


@pytest.fixture()
def sample_item(tmp_path: Path) -> Path:
    return build_minimal_item(tmp_path / "sample.vroidcustomitem")


def test_validate_synthetic_item(sample_item: Path) -> None:
    report = validate_archive(sample_item)
    assert report.valid


def test_inspect_sections(sample_item: Path) -> None:
    report = inspect_item(sample_item, language="en")
    assert {section.id for section in report.sections} == {
        "vroid",
        "vroidcustomitem",
        "file",
    }
    vroid = report.field_map("vroid")
    assert vroid["family"] == "hair"
    assert vroid["category_id"] == "TransferableGroupType.N00.Level1.HairHanege"


def test_thumbnail_ok(sample_item: Path) -> None:
    with CustomItemArchive(sample_item) as archive:
        result = load_thumbnail(archive)
    assert result.state is ThumbnailState.OK
    assert result.data is not None


def test_thumbnail_missing(tmp_path: Path) -> None:
    path = build_minimal_item(tmp_path / "no-thumb.vroidcustomitem", include_thumbnail=False)
    with CustomItemArchive(path) as archive:
        result = load_thumbnail(archive)
    assert result.state is ThumbnailState.MISSING


def test_thumbnail_unreadable(tmp_path: Path) -> None:
    path = build_minimal_item(
        tmp_path / "bad-thumb.vroidcustomitem",
        corrupt_thumbnail=True,
    )
    with CustomItemArchive(path) as archive:
        result = load_thumbnail(archive)
    assert result.state is ThumbnailState.UNREADABLE


def test_clone_roundtrip(sample_item: Path, tmp_path: Path) -> None:
    output = tmp_path / "clone.vroidcustomitem"
    clone_item(sample_item, output)
    report = validate_archive(output)
    assert report.valid
