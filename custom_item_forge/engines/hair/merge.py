"""Preserving merge for VRoid 2.x Hair ``.transferable`` messages."""

from __future__ import annotations

from dataclasses import dataclass

from custom_item_forge.core.errors import CollisionError, UnsupportedFormatError
from custom_item_forge.core.protobuf_wire import WireField, encode_field, parse_fields


@dataclass(frozen=True, slots=True)
class HairMergeStats:
    hairs: int
    materials: int
    bones: int
    geometry_blocks: int


@dataclass(frozen=True, slots=True)
class HairReferenceMaps:
    base_bt_count: int
    addon_bt_count: int
    bt_slot: dict[int, int]
    storage_f1: dict[int, int]
    storage_f8: dict[int, int]
    storage_f9: dict[int, int]


def count_basetransferable_materials(base_transferable_data: bytes) -> int:
    """Count material records in ``basetransferable.basetransferable``."""
    try:
        payload = _bytes(_one(base_transferable_data, 3, "base transferable"), "base payload")
        store = _bytes(_one(payload, 2, "base payload"), "base material store")
    except (UnsupportedFormatError, ValueError):
        return 0
    return sum(field.number == 1 for field in parse_fields(store))


def _field_index_map(addon_data: bytes, merged_data: bytes, field_number: int) -> dict[int, int]:
    def indexed_ids(data: bytes) -> list[str | None]:
        return [_nested_id(field) for field in parse_fields(data) if field.number == field_number]

    addon_ids = indexed_ids(addon_data)
    merged_ids = indexed_ids(merged_data)
    mapping: dict[int, int] = {}
    for index, identity in enumerate(addon_ids, start=1):
        if identity and identity in merged_ids:
            mapping[index] = merged_ids.index(identity) + 1
    return mapping


def build_hair_reference_maps(
    *,
    base_bt_data: bytes,
    addon_bt_data: bytes,
    base_storage: bytes,
    addon_storage: bytes,
    merged_storage: bytes,
) -> HairReferenceMaps:
    base_bt_count = count_basetransferable_materials(base_bt_data)
    addon_bt_count = count_basetransferable_materials(addon_bt_data)
    bt_slot = {slot: slot + base_bt_count for slot in range(1, addon_bt_count + 1)}
    return HairReferenceMaps(
        base_bt_count=base_bt_count,
        addon_bt_count=addon_bt_count,
        bt_slot=bt_slot,
        storage_f1=_field_index_map(addon_storage, merged_storage, 1),
        storage_f8=_field_index_map(addon_storage, merged_storage, 8),
        storage_f9=_field_index_map(addon_storage, merged_storage, 9),
    )


def _child_remap_context(context: dict[str, bool], field_number: int) -> dict[str, bool]:
    child = dict(context)
    if context.get("hair_strand"):
        if field_number == 4:
            child["geometry"] = True
        if child.get("geometry"):
            if field_number == 5:
                child["material_wrapper"] = True
            if field_number == 3 and child.get("material_wrapper"):
                child["geometry_material"] = True
            if field_number == 1 and child.get("material_wrapper"):
                child["geometry_material"] = True
        return child
    if context.get("geometry"):
        if field_number == 5:
            child["material_wrapper"] = True
        if field_number == 3 and context.get("material_wrapper"):
            child["geometry_material"] = True
        if field_number == 1 and context.get("material_wrapper"):
            child["geometry_material"] = True
        return child
    if field_number == 3:
        child["hair_strand"] = True
    elif field_number == 4:
        child["geometry"] = True
    return child


def _remap_varint(
    field_number: int,
    value: int,
    maps: HairReferenceMaps,
    context: dict[str, bool],
) -> int:
    if field_number == 8 and context.get("geometry"):
        return maps.storage_f8.get(value, value)
    if field_number == 9 and context.get("geometry"):
        return maps.storage_f9.get(value, value)
    if field_number != 6:
        return value
    if context.get("geometry_material"):
        return maps.bt_slot.get(value, value + maps.base_bt_count)
    if context.get("geometry"):
        return value
    if context.get("hair_strand"):
        if value <= maps.addon_bt_count:
            return maps.bt_slot.get(value, value + maps.base_bt_count)
        storage_slot = value - maps.addon_bt_count
        merged_storage = maps.storage_f1.get(storage_slot, storage_slot)
        return maps.base_bt_count + merged_storage
    return value


def remap_addon_references(data: bytes, maps: HairReferenceMaps, *, root: str) -> bytes:
    """Remap add-on numeric material/texture indices after storage merge."""
    context: dict[str, bool] = {"hair_strand": root == "strand", "geometry": root == "geometry"}
    return _remap_nested(data, maps, context)


def _merge_base_payload_f5(base_payload: bytes, addon_payload: bytes) -> bytes:
    try:
        base_f5 = _bytes([field for field in parse_fields(base_payload) if field.number == 5][0], "base f5")
        addon_f5 = _bytes([field for field in parse_fields(addon_payload) if field.number == 5][0], "addon f5")
    except (UnsupportedFormatError, IndexError):
        return base_payload

    base_fields = parse_fields(base_f5)
    addon_fields = parse_fields(addon_f5)
    seen_f9: set[str] = set()
    merged_f5_parts: list[bytes] = []
    for field in base_fields:
        merged_f5_parts.append(field.raw)
        if field.number == 9 and field.wire_type == 2:
            identity = _nested_id(field)
            if identity:
                seen_f9.add(identity)
    for field in addon_fields:
        if field.number != 9:
            continue
        identity = _nested_id(field)
        if identity and identity in seen_f9:
            continue
        merged_f5_parts.append(field.raw)
        if identity:
            seen_f9.add(identity)
    merged_f5 = b"".join(merged_f5_parts)
    return _replace_one(base_payload, 5, merged_f5, "base payload f5")


def merge_base_transferables(base_data: bytes, addon_data: bytes) -> tuple[bytes, int]:
    try:
        base_type = _one(base_data, 2, "base transferable").text()
        addon_type = _one(addon_data, 2, "add-on base transferable").text()
        if base_type != "TransferableType.Common.Base" or addon_type != base_type:
            raise UnsupportedFormatError("Common base transferables are incompatible")
        base_payload = _bytes(_one(base_data, 3, "base transferable"), "base payload")
        addon_payload = _bytes(_one(addon_data, 3, "add-on base transferable"), "add-on payload")
        base_store = _bytes(_one(base_payload, 2, "base payload"), "base material store")
        addon_store = _bytes(_one(addon_payload, 2, "add-on payload"), "add-on material store")
    except (UnsupportedFormatError, ValueError):
        return base_data, 0

    merged_store, counts = _append_unique(
        base_store,
        addon_store,
        numbers=set(range(1, 10)),
        label="common material and texture store",
    )
    merged_payload = _replace_one(base_payload, 2, merged_store, "base payload")
    merged_payload = _merge_base_payload_f5(merged_payload, addon_payload)
    merged = _replace_one(base_data, 3, merged_payload, "base transferable")
    return merged, sum(counts.values())


def _remap_nested(data: bytes, maps: HairReferenceMaps, context: dict[str, bool]) -> bytes:
    try:
        fields = parse_fields(data)
    except UnsupportedFormatError:
        return data
    chunks: list[bytes] = []
    for field in fields:
        if field.wire_type == 0 and isinstance(field.value, int):
            remapped = _remap_varint(field.number, field.value, maps, context)
            if remapped != field.value:
                chunks.append(encode_field(field.number, 0, remapped))
            else:
                chunks.append(field.raw)
        elif field.wire_type == 2 and isinstance(field.value, bytes):
            child = _child_remap_context(context, field.number)
            inner = _remap_nested(field.value, maps, child)
            chunks.append(encode_field(field.number, 2, inner))
        else:
            chunks.append(field.raw)
    return b"".join(chunks)


def hair_transferable_counts(data: bytes) -> tuple[int, int, int]:
    payload = _bytes(_one(data, 3, "transferable"), "payload")
    storage = _bytes(_one(payload, 2, "payload"), "resources")
    hair_data = _bytes(_one(payload, 4, "payload"), "hair data")
    bones = _bytes(_one(hair_data, 1, "hair data"), "Hair Bounce")
    hairs = _bytes(_one(hair_data, 2, "hair data"), "hairs")
    return (
        sum(field.number == 3 for field in parse_fields(hairs)),
        sum(field.number == 1 for field in parse_fields(bones)),
        sum(field.number == 1 for field in parse_fields(storage)),
    )


def hair_transferable_has_canonical_order(data: bytes) -> bool:
    payload = _bytes(_one(data, 3, "transferable"), "payload")
    storage = _bytes(_one(payload, 2, "payload"), "resources")
    hair_data = _bytes(_one(payload, 4, "payload"), "hair data")
    bones = _bytes(_one(hair_data, 1, "hair data"), "Hair Bounce")
    hairs = _bytes(_one(hair_data, 2, "hair data"), "hairs")
    return all(
        numbers == sorted(numbers)
        for numbers in (
            [field.number for field in parse_fields(storage)],
            [field.number for field in parse_fields(bones)],
            [field.number for field in parse_fields(hairs)],
        )
    )


def _bytes(field: WireField, label: str) -> bytes:
    if field.wire_type != 2 or not isinstance(field.value, bytes):
        raise UnsupportedFormatError(f"{label} is not a Protobuf message")
    return field.value


def _one(data: bytes, number: int, label: str) -> WireField:
    matches = [field for field in parse_fields(data) if field.number == number]
    if len(matches) != 1:
        raise UnsupportedFormatError(f"{label}: expected one field {number}, found {len(matches)}")
    return matches[0]


def _replace_one(data: bytes, number: int, value: bytes, label: str) -> bytes:
    fields = parse_fields(data)
    if sum(field.number == number for field in fields) != 1:
        raise UnsupportedFormatError(f"{label}: unrecognized structure")
    return b"".join(
        encode_field(number, 2, value) if field.number == number else field.raw
        for field in fields
    )


def _nested_id(field: WireField) -> str | None:
    try:
        nested = parse_fields(_bytes(field, "repeated entry"), max_fields=10_000)
    except UnsupportedFormatError:
        return None
    for item in nested:
        if item.number == 1:
            text = item.text()
            if text:
                return text
    return None


def _append_unique(
    base_data: bytes,
    addon_data: bytes,
    *,
    numbers: set[int],
    label: str,
) -> tuple[bytes, dict[int, int]]:
    base_fields = parse_fields(base_data)
    addon_fields = parse_fields(addon_data)
    identities: dict[tuple[int, str], bytes] = {}
    raw_seen: set[tuple[int, bytes]] = set()
    for field in base_fields:
        identity = _nested_id(field)
        if identity is not None:
            identities[(field.number, identity)] = field.raw
        raw_seen.add((field.number, field.raw))

    additions: list[bytes] = []
    counts: dict[int, int] = {}
    for field in addon_fields:
        if field.number not in numbers:
            continue
        identity = _nested_id(field)
        if identity is not None and (field.number, identity) in identities:
            if identities[(field.number, identity)] != field.raw:
                raise CollisionError(f"Duplicate internal ID in {label}: {identity}")
            continue
        if (field.number, field.raw) in raw_seen:
            continue
        additions.append(field.raw)
        counts[field.number] = counts.get(field.number, 0) + 1
        if identity is not None:
            identities[(field.number, identity)] = field.raw
        raw_seen.add((field.number, field.raw))

    merged_fields = [*base_fields]
    addition_fields = parse_fields(b"".join(additions)) if additions else []
    merged_fields.extend(addition_fields)
    merged_fields.sort(key=lambda field: field.number)
    return b"".join(field.raw for field in merged_fields), counts


def _hair_type(field: WireField) -> int | None:
    nested = parse_fields(_bytes(field, "hair definition"), max_fields=10_000)
    return next(
        (item.value for item in nested if item.number == 6 and isinstance(item.value, int)),
        None,
    )


def _merge_hair_store(
    base_data: bytes,
    addon_data: bytes,
    *,
    reference_maps: HairReferenceMaps | None = None,
) -> tuple[bytes, int, int]:
    addon_fields = parse_fields(addon_data)
    hair_fields = [field for field in addon_fields if field.number == 3]
    base_hairs = [field for field in parse_fields(base_data) if field.number == 3]
    if any(_hair_type(field) == 3 for field in hair_fields):
        raise UnsupportedFormatError(
            "Add-on contains base hair type 3; it cannot be duplicated safely"
        )

    base_ids = {_nested_id(field) for field in base_hairs}
    addon_ids = {_nested_id(field) for field in hair_fields}
    duplicate = (base_ids & addon_ids) - {None}
    if duplicate:
        raise CollisionError(f"Duplicate hair ID: {sorted(duplicate)[0]}")

    geometry = [field for field in addon_fields if field.number == 4]
    passthrough = [field for field in addon_fields if field.number not in (3, 4)]
    if passthrough:
        raise UnsupportedFormatError("Hair store contains unrecognized fields")

    if reference_maps is not None:
        hair_fields = parse_fields(
            b"".join(
                encode_field(
                    3,
                    2,
                    remap_addon_references(_bytes(field, "hair strand"), reference_maps, root="strand"),
                )
                for field in hair_fields
            )
        )
        geometry = parse_fields(
            b"".join(
                encode_field(
                    4,
                    2,
                    remap_addon_references(_bytes(field, "geometry"), reference_maps, root="geometry"),
                )
                for field in geometry
            )
        )

    merged_fields = [*parse_fields(base_data), *hair_fields, *geometry]
    merged_fields.sort(key=lambda field: field.number)
    return b"".join(field.raw for field in merged_fields), len(hair_fields), len(geometry)


def merge_hair_transferables(
    base_data: bytes,
    addon_data: bytes,
    *,
    include_storage: bool = True,
    include_bones: bool = True,
    include_hairs: bool = True,
    base_bt_data: bytes | None = None,
    addon_bt_data: bytes | None = None,
) -> tuple[bytes, HairMergeStats]:
    base_type = _one(base_data, 2, "base transferable").text()
    addon_type = _one(addon_data, 2, "add-on transferable").text()
    if (
        not base_type
        or base_type != addon_type
        or not base_type.startswith("TransferableType.N00.")
        or "Hair" not in base_type
    ):
        raise UnsupportedFormatError(
            "The transferables are not compatible hair items of the same category"
        )

    base_payload = _bytes(_one(base_data, 3, "base transferable"), "base payload")
    addon_payload = _bytes(_one(addon_data, 3, "add-on transferable"), "add-on payload")

    base_storage = _bytes(_one(base_payload, 2, "base payload"), "base resources")
    addon_storage = _bytes(_one(addon_payload, 2, "add-on payload"), "add-on resources")
    if include_storage:
        merged_storage, storage_counts = _append_unique(
            base_storage,
            addon_storage,
            numbers=set(range(1, 10)),
            label="resource store",
        )
    else:
        merged_storage, storage_counts = base_storage, {}

    reference_maps: HairReferenceMaps | None = None
    if include_hairs and base_bt_data is not None and addon_bt_data is not None:
        reference_maps = build_hair_reference_maps(
            base_bt_data=base_bt_data,
            addon_bt_data=addon_bt_data,
            base_storage=base_storage,
            addon_storage=addon_storage,
            merged_storage=merged_storage,
        )

    base_hair_data = _bytes(_one(base_payload, 4, "base payload"), "base hair data")
    addon_hair_data = _bytes(_one(addon_payload, 4, "add-on payload"), "add-on hair data")
    base_bones = _bytes(_one(base_hair_data, 1, "base hair data"), "base Hair Bounce")
    addon_bones = _bytes(_one(addon_hair_data, 1, "add-on hair data"), "add-on Hair Bounce")
    if include_bones:
        merged_bones, bone_counts = _append_unique(
            base_bones,
            addon_bones,
            numbers={1},
            label="Hair Bounce groups",
        )
    else:
        merged_bones, bone_counts = base_bones, {}

    base_hairs = _bytes(_one(base_hair_data, 2, "base hair data"), "base hairs")
    addon_hairs = _bytes(_one(addon_hair_data, 2, "add-on hair data"), "add-on hairs")
    if include_hairs:
        merged_hairs, hair_count, geometry_count = _merge_hair_store(
            base_hairs,
            addon_hairs,
            reference_maps=reference_maps,
        )
    else:
        merged_hairs, hair_count, geometry_count = base_hairs, 0, 0

    merged_hair_data = _replace_one(base_hair_data, 1, merged_bones, "hair data")
    merged_hair_data = _replace_one(merged_hair_data, 2, merged_hairs, "hair data")
    merged_payload = _replace_one(base_payload, 2, merged_storage, "payload")
    merged_payload = _replace_one(merged_payload, 4, merged_hair_data, "payload")
    merged = _replace_one(base_data, 3, merged_payload, "transferable")

    return merged, HairMergeStats(
        hairs=hair_count,
        materials=storage_counts.get(1, 0),
        bones=bone_counts.get(1, 0),
        geometry_blocks=geometry_count,
    )
