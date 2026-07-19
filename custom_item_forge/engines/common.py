"""Shared category rewrite for .vroidcustomitem archives."""

from __future__ import annotations

import json
from pathlib import Path

from custom_item_forge.catalog.categories import category_family, resolve_category
from custom_item_forge.core.archive import META_PATH, CustomItemArchive, write_transformed_archive
from custom_item_forge.core.errors import InvalidArchiveError, UnsupportedFormatError
from custom_item_forge.core.probe import select_root_group
from custom_item_forge.core.protobuf_wire import encode_text, parse_fields


def _replace_text_field(data: bytes, number: int, value: str) -> bytes:
    fields = parse_fields(data)
    matches = [field for field in fields if field.number == number and field.wire_type == 2]
    if len(matches) != 1 or matches[0].text() is None:
        raise UnsupportedFormatError(f"Expected one text field {number}, found {len(matches)}")
    replaced = False
    chunks: list[bytes] = []
    for field in fields:
        if field.number == number and field.wire_type == 2 and not replaced:
            chunks.append(encode_text(number, value))
            replaced = True
        else:
            chunks.append(field.raw)
    return b"".join(chunks)


def recategorize_item(
    source: str | Path,
    output: str | Path,
    category: str,
    *,
    expected_family: str,
    force: bool = False,
) -> Path:
    """Rewrite root group + transferable category IDs within one family."""
    target_category = resolve_category(category)
    if target_category.family != expected_family:
        raise UnsupportedFormatError(
            f"Target category family {target_category.family!r} does not match {expected_family!r}"
        )
    with CustomItemArchive(source) as archive:
        source_family = category_family(archive.category_id)
        if source_family and source_family != target_category.family:
            raise UnsupportedFormatError(
                "Cross-family category changes are unsafe: hair, clothing and "
                "accessories use different payload schemas."
            )
        root = select_root_group(archive)
        if len(root.referenced_ids) != 1:
            raise UnsupportedFormatError("The root group must reference exactly one transferable")
        transferable_entry = f"v1customitem/transferables/{root.referenced_ids[0]}"
        if transferable_entry not in archive.infos:
            raise UnsupportedFormatError("The root group references a missing transferable")

        metadata = dict(archive.metadata)
        metadata["rootTransferableGroupTypeId"] = target_category.transferable_id
        metadata_replacement = json.dumps(
            metadata,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        group_replacement = _replace_text_field(
            archive.read_bytes(root.entry, limit=64 * 1024 * 1024),
            2,
            target_category.transferable_id,
        )
        transferable_replacement = _replace_text_field(
            archive.read_bytes(transferable_entry, limit=64 * 1024 * 1024),
            2,
            target_category.transferable_type,
        )
        written = write_transformed_archive(
            archive,
            output,
            replacements={
                META_PATH: metadata_replacement,
                root.entry: group_replacement,
                transferable_entry: transferable_replacement,
            },
            force=force,
        )

    with CustomItemArchive(written) as result:
        verified_root = select_root_group(result)
        verified_transferable = f"v1customitem/transferables/{verified_root.referenced_ids[0]}"
        transferable_types = [
            field.text()
            for field in parse_fields(result.read_bytes(verified_transferable, limit=64 * 1024 * 1024))
            if field.number == 2 and field.text()
        ]
        if (
            result.category_id != target_category.transferable_id
            or verified_root.category_text != target_category.transferable_id
            or transferable_types != [target_category.transferable_type]
        ):
            written.unlink(missing_ok=True)
            raise InvalidArchiveError("Category verification failed; output removed")
    return written
