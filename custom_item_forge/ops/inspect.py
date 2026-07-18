"""Build categorized inspect reports."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from custom_item_forge.catalog.categories import category_family, category_label, resolve_category
from custom_item_forge.core.archive import (
    BASE_TRANSFERABLE_PATH,
    META_PATH,
    THUMBNAIL_PATH,
    CustomItemArchive,
    sha256_file,
    validate_archive,
)
from custom_item_forge.core.model import InspectField, InspectReport, InspectSection, ThumbnailState
from custom_item_forge.core.probe import probe_root_groups
from custom_item_forge.core.thumbnail import load_thumbnail
from custom_item_forge.engines.router import FamilyRouter


def _metadata_version(metadata: dict[str, Any]) -> Any:
    for key in (
        "customItemVersion",
        "customItemDataVersion",
        "schemaVersion",
        "version",
    ):
        if key in metadata:
            return metadata[key]
    return None


def _detect_template_hint(archive: CustomItemArchive, family: str | None) -> str | None:
    category = None
    if archive.category_id:
        try:
            from custom_item_forge.catalog.categories import BY_ID

            category = BY_ID.get(archive.category_id)
        except Exception:  # noqa: BLE001
            category = None
    if category and category.template_hint:
        return category.template_hint
    if family == "accessory" and archive.category_id and "Glasses" in archive.category_id:
        return "Accessory_GlassesHi"
    return None


def inspect_item(path: str | Path, *, language: str = "en") -> InspectReport:
    resolved = Path(path).expanduser().resolve()
    stat = resolved.stat()
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    with CustomItemArchive(resolved) as archive:
        thumbnail = load_thumbnail(archive)
        candidates = probe_root_groups(archive)
        candidate = candidates[0] if candidates else None
        family = category_family(archive.category_id)
        validation = validate_archive(resolved, verify_crc=True)
        crc_valid = validation.valid or not any(
            issue.code == "crc_mismatch" for issue in validation.issues
        )
        template_hint = _detect_template_hint(archive, family)
        transferable_type = None
        if archive.category_id:
            try:
                transferable_type = resolve_category(archive.category_id).transferable_type
            except ValueError:
                suffix = archive.category_id.rsplit(".", 1)[-1]
                transferable_type = f"TransferableType.N00.{suffix}"

        compatibility = FamilyRouter().compatibility(archive.category_id, language=language)

        vroid_fields = (
            InspectField("family", family or "unknown", "inspect.family"),
            InspectField(
                "category_label",
                category_label(archive.category_id, language),
                "inspect.category_label",
            ),
            InspectField("category_id", archive.category_id, "inspect.category_id"),
            InspectField("internal_name", transferable_type and transferable_type.rsplit(".", 1)[-1], "inspect.internal_name"),
            InspectField("transferable_group_type", archive.category_id, "inspect.transferable_group_type"),
            InspectField("transferable_type", transferable_type, "inspect.transferable_type"),
            InspectField("template_hint", template_hint, "inspect.template_hint"),
            InspectField(
                "slot_compatibility",
                compatibility.recategorize_reason if compatibility.can_recategorize else compatibility.merge_reason,
                "inspect.slot_compatibility",
            ),
        )

        custom_item_fields = (
            InspectField("metadata_version", _metadata_version(archive.metadata), "inspect.metadata_version"),
            InspectField(
                "root_group_entry",
                candidate.entry if candidate else None,
                "inspect.root_group_entry",
            ),
            InspectField(
                "root_group_score",
                candidate.score if candidate else 0,
                "inspect.root_group_score",
            ),
            InspectField(
                "root_trans_items",
                candidate.trans_items if candidate else 0,
                "inspect.root_trans_items",
            ),
            InspectField(
                "root_material_refs",
                candidate.material_refs if candidate else 0,
                "inspect.root_material_refs",
            ),
            InspectField(
                "binary_entry_count",
                len(archive.binary_entry_names()),
                "inspect.binary_entry_count",
            ),
            InspectField(
                "has_base_transferable",
                BASE_TRANSFERABLE_PATH in archive.infos,
                "inspect.has_base_transferable",
            ),
            InspectField(
                "validation_valid",
                validation.valid,
                "inspect.validation_valid",
            ),
            InspectField(
                "validation_warnings",
                validation.warnings,
                "inspect.validation_warnings",
            ),
        )

        file_fields = (
            InspectField("path", str(resolved), "inspect.path"),
            InspectField("size_bytes", stat.st_size, "inspect.size_bytes"),
            InspectField("sha256", sha256_file(resolved), "inspect.sha256"),
            InspectField("entry_count", len(archive.infos), "inspect.entry_count"),
            InspectField("uncompressed_bytes", archive.total_uncompressed, "inspect.uncompressed_bytes"),
            InspectField("crc_valid", crc_valid, "inspect.crc_valid"),
            InspectField("thumbnail_state", thumbnail.state.value, "inspect.thumbnail_state"),
            InspectField("modified_at", modified.isoformat(), "inspect.modified_at"),
            InspectField("has_meta_json", META_PATH in archive.infos, "inspect.has_meta_json"),
            InspectField("has_thumbnail_entry", THUMBNAIL_PATH in archive.infos, "inspect.has_thumbnail_entry"),
        )

        return InspectReport(
            path=resolved,
            sections=(
                InspectSection("vroid", vroid_fields),
                InspectSection("vroidcustomitem", custom_item_fields),
                InspectSection("file", file_fields),
            ),
            thumbnail_state=thumbnail.state,
            thumbnail_bytes=thumbnail.data if thumbnail.state == ThumbnailState.OK else None,
        )
