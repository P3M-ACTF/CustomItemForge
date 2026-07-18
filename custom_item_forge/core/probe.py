"""Non-destructive heuristic detection of TransferableGroup root messages."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterator

from custom_item_forge.core.archive import (
    MAX_SINGLE_ENTRY,
    META_PATH,
    THUMBNAIL_PATH,
    CustomItemArchive,
)
from custom_item_forge.core.errors import InvalidArchiveError, UnsupportedFormatError
from custom_item_forge.core.protobuf_wire import WireField, parse_fields, summarize_fields

_ID_PATTERN = re.compile(r"^[0-9a-fA-F-]{16,64}$")
MAX_PROBE_BYTES = min(MAX_SINGLE_ENTRY, 64 * 1024 * 1024)


@dataclass(frozen=True, slots=True)
class RootGroupCandidate:
    entry: str
    score: int
    trans_items: int
    material_refs: int
    category_text: str | None
    group_edit_type: str | None
    referenced_ids: tuple[str, ...]
    field_summary: dict[int, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def iter_json_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from iter_json_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_strings(item)


def _parse_trans_ref(field: WireField) -> tuple[int, str | None]:
    if field.wire_type != 2 or not isinstance(field.value, bytes):
        return 0, None
    try:
        nested = parse_fields(field.value, max_fields=1_000)
    except UnsupportedFormatError:
        return 0, None
    template = next(
        (item.text() for item in nested if item.number == 1 and item.text()),
        None,
    )
    identifier = next(
        (item.text() for item in nested if item.number == 2 and item.text()),
        None,
    )
    score = 0
    if template:
        score += 1
        if "Hair" in template or "Transfer" in template or "Accessory" in template:
            score += 1
    if identifier:
        score += 2
        if _ID_PATTERN.fullmatch(identifier):
            score += 2
    return score, identifier


def score_root_group(
    data: bytes,
    *,
    path: str,
    metadata_hints: set[str],
) -> RootGroupCandidate:
    fields = parse_fields(data)
    field_two = [item.text() for item in fields if item.number == 2 and item.text()]
    field_three = [item.text() for item in fields if item.number == 3 and item.text()]
    trans_fields = [item for item in fields if item.number == 4 and item.wire_type == 2]
    material_fields = [item for item in fields if item.number == 5 and item.wire_type == 2]

    score = 0
    if any(hint and hint in path for hint in metadata_hints):
        score += 12
    if field_two:
        score += 2
    if field_three:
        score += 2
    if trans_fields:
        score += 6
    if material_fields:
        score += 3

    ids: list[str] = []
    for field in (*trans_fields, *material_fields):
        nested_score, identifier = _parse_trans_ref(field)
        score += nested_score
        if identifier and identifier not in ids:
            ids.append(identifier)

    return RootGroupCandidate(
        entry=path,
        score=score,
        trans_items=len(trans_fields),
        material_refs=len(material_fields),
        category_text=field_two[0] if field_two else None,
        group_edit_type=field_three[0] if field_three else None,
        referenced_ids=tuple(ids),
        field_summary=summarize_fields(fields),
    )


def probe_root_groups(archive: CustomItemArchive) -> list[RootGroupCandidate]:
    metadata_hints = {
        value
        for value in iter_json_strings(archive.metadata)
        if _ID_PATTERN.fullmatch(value)
    }
    candidates: list[RootGroupCandidate] = []
    for name in archive.binary_entry_names():
        if name in (META_PATH, THUMBNAIL_PATH):
            continue
        info = archive.infos[name]
        if info.file_size == 0 or info.file_size > MAX_PROBE_BYTES:
            continue
        try:
            data = archive.read_bytes(name, limit=MAX_PROBE_BYTES)
            candidate = score_root_group(data, path=name, metadata_hints=metadata_hints)
        except (InvalidArchiveError, UnsupportedFormatError):
            continue
        if candidate.score > 0:
            candidates.append(candidate)
    return sorted(candidates, key=lambda item: (item.score, item.trans_items), reverse=True)


def select_root_group(
    archive: CustomItemArchive,
    *,
    minimum_score: int = 8,
) -> RootGroupCandidate:
    candidates = probe_root_groups(archive)
    if not candidates or candidates[0].score < minimum_score:
        raise UnsupportedFormatError(
            f"Could not reliably locate root group in {archive.path.name}"
        )
    if len(candidates) > 1 and candidates[0].score == candidates[1].score:
        raise UnsupportedFormatError(
            f"Two root group candidates tie in confidence in {archive.path.name}"
        )
    return candidates[0]
