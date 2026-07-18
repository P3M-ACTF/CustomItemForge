"""Synthetic .vroidcustomitem builders for tests."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from custom_item_forge.core.archive import META_PATH, THUMBNAIL_PATH
from custom_item_forge.core.protobuf_wire import encode_field, encode_text

PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _trans_ref(template: str, identifier: str) -> bytes:
    nested = encode_text(1, template) + encode_text(2, identifier)
    return encode_field(4, 2, nested)


def _minimal_root_group(category_id: str, transferable_id: str) -> bytes:
    chunks = [
        encode_text(2, category_id),
        encode_text(3, "GroupEditType.N00.Hair"),
        _trans_ref("TransferTemplate.N00.Hair", transferable_id),
    ]
    return b"".join(chunks)


def build_minimal_item(
    path: Path,
    *,
    category_suffix: str = "HairHanege",
    include_thumbnail: bool = True,
    thumbnail_bytes: bytes | None = None,
    corrupt_thumbnail: bool = False,
) -> Path:
    category_id = f"TransferableGroupType.N00.Level1.{category_suffix}"
    transferable_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    meta = {
        "rootTransferableGroupTypeId": category_id,
        "customItemVersion": 1,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(META_PATH, json.dumps(meta, separators=(",", ":")))
        archive.writestr(
            f"v1customitem/transferables/{transferable_id}",
            encode_text(2, f"TransferableType.N00.{category_suffix}"),
        )
        archive.writestr(
            "v1customitem/groups/root.group",
            _minimal_root_group(category_id, transferable_id),
        )
        archive.writestr(
            "v1customitem/basetransferable.basetransferable",
            b"\x00",
        )
        if include_thumbnail:
            payload = b"not-a-png" if corrupt_thumbnail else (thumbnail_bytes or PNG_1X1)
            archive.writestr(THUMBNAIL_PATH, payload)
    return path
