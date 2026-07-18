"""Small serializable data models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal


Severity = Literal["info", "warning", "error"]


class ThumbnailState(str, Enum):
    MISSING = "missing"
    UNREADABLE = "unreadable"
    OK = "ok"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: Severity
    code: str
    message: str
    entry: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ValidationReport:
    path: Path
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def warnings(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "valid": self.valid,
            "warnings": self.warnings,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True, slots=True)
class InspectField:
    key: str
    value: Any
    label_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InspectSection:
    id: str
    fields: tuple[InspectField, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "fields": [item.to_dict() for item in self.fields],
        }


@dataclass(frozen=True, slots=True)
class InspectReport:
    path: Path
    sections: tuple[InspectSection, ...]
    thumbnail_state: ThumbnailState
    thumbnail_bytes: bytes | None = None

    def section(self, section_id: str) -> InspectSection | None:
        return next((item for item in self.sections if item.id == section_id), None)

    def field_map(self, section_id: str) -> dict[str, Any]:
        section = self.section(section_id)
        if section is None:
            return {}
        return {item.key: item.value for item in section.fields}

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "thumbnail_state": self.thumbnail_state.value,
            "has_thumbnail_bytes": self.thumbnail_bytes is not None,
            "sections": [section.to_dict() for section in self.sections],
        }


@dataclass(frozen=True, slots=True)
class MergeReport:
    base: Path
    addon: Path
    output: Path
    family: str
    base_root_entry: str
    addon_root_entry: str
    appended_trans_items: int = 0
    appended_material_refs: int = 0
    copied_entries: int = 0
    skipped_identical_entries: int = 0
    output_sha256: str = ""
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("base", "addon", "output"):
            data[key] = str(data[key])
        data["notes"] = list(self.notes)
        return data


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    family: str | None
    can_recategorize: bool
    can_merge: bool
    recategorize_reason: str
    merge_reason: str
    calibrated: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FileFacts:
    path: Path
    size_bytes: int
    sha256: str
    modified_at: datetime
    entry_count: int
    uncompressed_bytes: int
    crc_valid: bool | None
    thumbnail_state: ThumbnailState
