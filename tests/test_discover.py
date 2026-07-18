from __future__ import annotations

from pathlib import Path

import pytest

from custom_item_forge.core.errors import UnsupportedFormatError
from custom_item_forge.ops.discover import discover_items
from tests.fixtures.synthetic.builder import build_minimal_item


def test_discover_single_file(tmp_path: Path) -> None:
    item = build_minimal_item(tmp_path / "one.vroidcustomitem")
    found = discover_items(item)
    assert found == [item]


def test_discover_directory(tmp_path: Path) -> None:
    a = build_minimal_item(tmp_path / "a.vroidcustomitem")
    b = build_minimal_item(tmp_path / "nested" / "b.vroidcustomitem")
    found = discover_items(tmp_path)
    assert a in found
    assert b in found


def test_discover_vroid_rejected(tmp_path: Path) -> None:
    model = tmp_path / "model.vroid"
    model.write_bytes(b"PK")
    with pytest.raises(UnsupportedFormatError):
        discover_items(model)
