"""Hair recategorize and merge operations (ported from VRoidHairComposer 0.4.x)."""

from __future__ import annotations

from pathlib import Path

from custom_item_forge.core.archive import (
    BASE_OWNED_ENTRIES,
    BASE_TRANSFERABLE_PATH,
    THUMBNAIL_PATH,
    CustomItemArchive,
    ensure_safe_output,
    sha256_file,
    write_transformed_archive,
)
from custom_item_forge.core.errors import CollisionError, InvalidArchiveError, UnsupportedFormatError
from custom_item_forge.core.model import MergeReport
from custom_item_forge.core.probe import select_root_group
from custom_item_forge.core.thumbnail_compose import compose_merge_thumbnail
from custom_item_forge.engines.common import recategorize_item
from custom_item_forge.engines.hair.merge import (
    hair_transferable_counts,
    hair_transferable_has_canonical_order,
    merge_base_transferables,
    merge_hair_transferables,
)

_HAIR_PREFIX = "TransferableGroupType.N00.Level1."


def _same_entry(first: CustomItemArchive, second: CustomItemArchive, name: str) -> bool:
    left = first.infos[name]
    right = second.infos[name]
    if left.is_dir() and right.is_dir():
        return True
    if (left.file_size, left.CRC) != (right.file_size, right.CRC):
        return False
    return first.hash_entry(name) == second.hash_entry(name)


def recategorize_hair_item(
    source: str | Path,
    output: str | Path,
    category: str,
    *,
    force: bool = False,
) -> Path:
    return recategorize_item(
        source,
        output,
        category,
        expected_family="hair",
        force=force,
    )


def merge_hair_items(
    base_path: str | Path,
    addon_path: str | Path,
    output: str | Path,
    *,
    force: bool = False,
) -> MergeReport:
    destination = ensure_safe_output(
        output,
        inputs=[base_path, addon_path],
        force=force,
    )
    with CustomItemArchive(base_path) as base, CustomItemArchive(addon_path) as addon:
        if base.category_id is None or addon.category_id is None:
            raise UnsupportedFormatError("Both items must declare a category")
        if not base.category_id.startswith(_HAIR_PREFIX) or not addon.category_id.startswith(_HAIR_PREFIX):
            raise UnsupportedFormatError("Only hair categories are supported")
        if base.category_id != addon.category_id:
            raise UnsupportedFormatError(
                "Base and add-on must share the same hair category"
            )

        base_root = select_root_group(base)
        addon_root = select_root_group(addon)
        if len(base_root.referenced_ids) != 1 or len(addon_root.referenced_ids) != 1:
            raise UnsupportedFormatError(
                "Each VRoid 2.x group must reference exactly one transferable"
            )
        base_transferable = f"v1customitem/transferables/{base_root.referenced_ids[0]}"
        addon_transferable = f"v1customitem/transferables/{addon_root.referenced_ids[0]}"
        if base_transferable not in base.infos or addon_transferable not in addon.infos:
            raise UnsupportedFormatError("Root group references a missing transferable")

        base_transferable_data = base.read_bytes(base_transferable, limit=64 * 1024 * 1024)
        addon_transferable_data = addon.read_bytes(addon_transferable, limit=64 * 1024 * 1024)
        base_bt_data = base.read_bytes(BASE_TRANSFERABLE_PATH, limit=512 * 1024 * 1024)
        addon_bt_data = (
            addon.read_bytes(BASE_TRANSFERABLE_PATH, limit=512 * 1024 * 1024)
            if BASE_TRANSFERABLE_PATH in addon.infos
            else b""
        )
        base_counts = hair_transferable_counts(base_transferable_data)
        merged_transferable, stats = merge_hair_transferables(
            base_transferable_data,
            addon_transferable_data,
            base_bt_data=base_bt_data,
            addon_bt_data=addon_bt_data,
        )
        merged_base_transferable = base_bt_data
        common_material_records = 0
        if addon_bt_data:
            merged_base_transferable, common_material_records = merge_base_transferables(
                base_bt_data,
                addon_bt_data,
            )

        replacements: dict[str, bytes] = {
            base_transferable: merged_transferable,
            BASE_TRANSFERABLE_PATH: merged_base_transferable,
        }
        merge_thumbnail = compose_merge_thumbnail(base.path, addon.path)
        if merge_thumbnail:
            replacements[THUMBNAIL_PATH] = merge_thumbnail

        additions: list[tuple[CustomItemArchive, str, str | None]] = []
        skipped_identical = 0
        excluded = {
            *BASE_OWNED_ENTRIES,
            addon_root.entry,
            addon_transferable,
        }
        for name in addon.names:
            if name in excluded:
                continue
            if name in base.infos:
                if _same_entry(base, addon, name):
                    skipped_identical += 1
                    continue
                raise CollisionError(
                    f"Resource collision at {name!r}; aborting without writing output"
                )
            additions.append((addon, name, None))

        written = write_transformed_archive(
            base,
            destination,
            replacements=replacements,
            additions=additions,
            force=force,
        )

    with CustomItemArchive(written) as result:
        result_root = select_root_group(result)
        if result_root.entry != base_root.entry or result_root.trans_items != 1:
            written.unlink(missing_ok=True)
            raise InvalidArchiveError("Verification changed the base item root group")
        result_counts = hair_transferable_counts(
            result.read_bytes(base_transferable, limit=64 * 1024 * 1024)
        )
        result_transferable = result.read_bytes(base_transferable, limit=64 * 1024 * 1024)
        if not hair_transferable_has_canonical_order(result_transferable):
            written.unlink(missing_ok=True)
            raise InvalidArchiveError("Output does not preserve VRoid's required field order")
        expected_counts = (
            base_counts[0] + stats.hairs,
            base_counts[1] + stats.bones,
            base_counts[2] + stats.materials,
        )
        if result_counts != expected_counts:
            written.unlink(missing_ok=True)
            raise InvalidArchiveError("Post-merge verification failed")

    return MergeReport(
        base=Path(base_path).expanduser().resolve(),
        addon=Path(addon_path).expanduser().resolve(),
        output=written,
        family="hair",
        base_root_entry=base_root.entry,
        addon_root_entry=addon_root.entry,
        appended_trans_items=stats.hairs,
        appended_material_refs=stats.materials + common_material_records,
        copied_entries=len(additions),
        skipped_identical_entries=skipped_identical,
        output_sha256=sha256_file(written),
    )
