"""Conservative read/write for ``.vroidcustomitem`` ZIP containers."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import zipfile
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

from custom_item_forge.core.errors import InvalidArchiveError, UnsafeOutputError
from custom_item_forge.core.model import ValidationIssue, ValidationReport

ROOT_META_PATH = "meta.json"
META_PATH = "v1customitem/meta.json"
THUMBNAIL_PATH = "thumbnails/thumbnail.png"
BASE_TRANSFERABLE_PATH = "v1customitem/basetransferable.basetransferable"
BASE_OWNED_ENTRIES = frozenset(
    {ROOT_META_PATH, META_PATH, THUMBNAIL_PATH, BASE_TRANSFERABLE_PATH}
)

MAX_ENTRIES = 10_000
MAX_TOTAL_UNCOMPRESSED = 2 * 1024 * 1024 * 1024
MAX_SINGLE_ENTRY = 512 * 1024 * 1024
MAX_META_BYTES = 4 * 1024 * 1024
COPY_BUFFER = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(COPY_BUFFER), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _unsafe_entry_reason(name: str) -> str | None:
    if not name:
        return "empty name"
    if "\x00" in name:
        return "contains a null byte"
    if "\\" in name:
        return "uses Windows separators"
    if name.startswith("/"):
        return "absolute path"
    trimmed = name[:-1] if name.endswith("/") else name
    if not trimmed:
        return "ambiguous root directory"
    raw_parts = trimmed.split("/")
    if any(part in ("", ".", "..") for part in raw_parts):
        return "ambiguous path or '..'"
    if ":" in raw_parts[0]:
        return "possible Windows drive letter"
    return None


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_IFMT(mode) == stat.S_IFLNK


def clone_zipinfo(info: zipfile.ZipInfo, *, filename: str | None = None) -> zipfile.ZipInfo:
    clone = zipfile.ZipInfo(filename or info.filename, date_time=info.date_time)
    clone.compress_type = info.compress_type
    clone.comment = info.comment
    clone.extra = info.extra
    clone.create_system = info.create_system
    clone.create_version = info.create_version
    clone.extract_version = info.extract_version
    clone.external_attr = info.external_attr
    clone.internal_attr = info.internal_attr
    clone.flag_bits = info.flag_bits & ~0x1
    return clone


class CustomItemArchive:
    """Read-only view of a Custom Item container."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path).expanduser().resolve()
        self._zip: zipfile.ZipFile | None = None
        self._infos: dict[str, zipfile.ZipInfo] = {}
        self._metadata: dict[str, Any] | None = None

    def __enter__(self) -> CustomItemArchive:
        if not self.path.is_file():
            raise InvalidArchiveError(f"File does not exist: {self.path}")
        if not zipfile.is_zipfile(self.path):
            raise InvalidArchiveError(
                f"{self.path.name} is not a valid ZIP / .vroidcustomitem container"
            )
        try:
            self._zip = zipfile.ZipFile(self.path, "r")
            infos = self._zip.infolist()
        except (OSError, zipfile.BadZipFile) as exc:
            raise InvalidArchiveError(f"Cannot open {self.path.name}: {exc}") from exc

        if len(infos) > MAX_ENTRIES:
            self.close()
            raise InvalidArchiveError(
                f"Container has too many entries ({len(infos)} > {MAX_ENTRIES})"
            )

        total = 0
        casefold_names: set[str] = set()
        for info in infos:
            reason = _unsafe_entry_reason(info.filename)
            if reason:
                self.close()
                raise InvalidArchiveError(f"Unsafe entry {info.filename!r}: {reason}")
            if info.filename in self._infos:
                self.close()
                raise InvalidArchiveError(f"Duplicate entry: {info.filename}")
            folded = info.filename.casefold()
            if folded in casefold_names:
                self.close()
                raise InvalidArchiveError(
                    f"Paths collide on Windows: {info.filename}"
                )
            casefold_names.add(folded)
            if info.flag_bits & 0x1:
                self.close()
                raise InvalidArchiveError(f"Encrypted entry not supported: {info.filename}")
            if _is_symlink(info):
                self.close()
                raise InvalidArchiveError(f"Symlink not allowed: {info.filename}")
            if info.file_size > MAX_SINGLE_ENTRY:
                self.close()
                raise InvalidArchiveError(
                    f"Entry too large: {info.filename} ({info.file_size} bytes)"
                )
            total += info.file_size
            if total > MAX_TOTAL_UNCOMPRESSED:
                self.close()
                raise InvalidArchiveError("Uncompressed size exceeds safety limit")
            self._infos[info.filename] = info

        if META_PATH not in self._infos:
            self.close()
            raise InvalidArchiveError(f"Missing required entry {META_PATH}")
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        if self._zip is not None:
            self._zip.close()
            self._zip = None

    @property
    def zip_file(self) -> zipfile.ZipFile:
        if self._zip is None:
            raise RuntimeError("Archive must be opened with 'with CustomItemArchive(...)'")
        return self._zip

    @property
    def infos(self) -> Mapping[str, zipfile.ZipInfo]:
        return self._infos

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._infos)

    @property
    def total_uncompressed(self) -> int:
        return sum(info.file_size for info in self._infos.values())

    @property
    def metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            raw = self.read_bytes(META_PATH, limit=MAX_META_BYTES)
            try:
                parsed = json.loads(raw.decode("utf-8-sig"))
            except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
                raise InvalidArchiveError(
                    f"{META_PATH} does not contain valid UTF-8 JSON: {exc}"
                ) from exc
            if not isinstance(parsed, dict):
                raise InvalidArchiveError(f"{META_PATH} must contain a JSON object")
            self._metadata = parsed
        return self._metadata

    @property
    def category_id(self) -> str | None:
        value = self.metadata.get("rootTransferableGroupTypeId")
        return value if isinstance(value, str) else None

    def open_entry(self, name: str) -> BinaryIO:
        if name not in self._infos:
            raise InvalidArchiveError(f"Entry does not exist: {name!r}")
        return self.zip_file.open(name, "r")

    def read_bytes(self, name: str, *, limit: int = MAX_SINGLE_ENTRY) -> bytes:
        info = self._infos.get(name)
        if info is None:
            raise InvalidArchiveError(f"Entry does not exist: {name!r}")
        if info.file_size > limit:
            raise InvalidArchiveError(
                f"{name} exceeds read limit ({info.file_size} > {limit} bytes)"
            )
        with self.zip_file.open(info, "r") as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise InvalidArchiveError(f"{name} exceeds read limit")
        return data

    def hash_entry(self, name: str) -> str:
        digest = hashlib.sha256()
        with self.open_entry(name) as stream:
            for chunk in iter(lambda: stream.read(COPY_BUFFER), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def binary_entry_names(self) -> tuple[str, ...]:
        ignored_suffixes = {".json", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".md"}
        result = []
        for name, info in self._infos.items():
            if info.is_dir():
                continue
            if PurePosixPath(name).suffix.lower() not in ignored_suffixes:
                result.append(name)
        return tuple(result)


def validate_archive(
    path: str | os.PathLike[str],
    *,
    verify_crc: bool = True,
) -> ValidationReport:
    resolved = Path(path).expanduser().resolve()
    report = ValidationReport(resolved)
    try:
        with CustomItemArchive(resolved) as archive:
            metadata_valid = True
            try:
                _ = archive.metadata
            except InvalidArchiveError as exc:
                metadata_valid = False
                report.issues.append(
                    ValidationIssue("error", "invalid_metadata", str(exc), META_PATH)
                )

            if metadata_valid and archive.category_id is None:
                report.issues.append(
                    ValidationIssue(
                        "warning",
                        "missing_category",
                        "rootTransferableGroupTypeId not found in metadata",
                        META_PATH,
                    )
                )
            if THUMBNAIL_PATH not in archive.infos:
                report.issues.append(
                    ValidationIssue(
                        "warning",
                        "missing_thumbnail",
                        "Container does not include the conventional thumbnail",
                        THUMBNAIL_PATH,
                    )
                )
            if verify_crc:
                bad_entry = archive.zip_file.testzip()
                if bad_entry:
                    report.issues.append(
                        ValidationIssue(
                            "error",
                            "crc_mismatch",
                            "CRC check failed",
                            bad_entry,
                        )
                    )
            if not report.issues:
                report.issues.append(
                    ValidationIssue("info", "ok", "Container and metadata are valid")
                )
    except InvalidArchiveError as exc:
        report.issues.append(ValidationIssue("error", "invalid_archive", str(exc)))
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        report.issues.append(ValidationIssue("error", "io_error", str(exc)))
    return report


def ensure_safe_output(
    output: str | os.PathLike[str],
    *,
    inputs: Iterable[str | os.PathLike[str]],
    force: bool = False,
) -> Path:
    resolved = Path(output).expanduser().resolve()
    input_paths = {Path(path).expanduser().resolve() for path in inputs}
    if resolved in input_paths:
        raise UnsafeOutputError("Output cannot be the same file as an input")
    if resolved.exists() and not force:
        raise UnsafeOutputError(
            f"Output already exists: {resolved}. Use --force to replace it"
        )
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _copy_entry(
    source: CustomItemArchive,
    source_name: str,
    destination: zipfile.ZipFile,
    *,
    destination_name: str | None = None,
) -> None:
    source_info = source.infos[source_name]
    info = clone_zipinfo(source_info, filename=destination_name)
    if source_info.is_dir():
        destination.writestr(info, b"")
        return
    with source.open_entry(source_name) as reader, destination.open(info, "w") as writer:
        shutil.copyfileobj(reader, writer, length=COPY_BUFFER)


def write_transformed_archive(
    base: CustomItemArchive,
    output: str | os.PathLike[str],
    *,
    replacements: Mapping[str, bytes] | None = None,
    skip: Iterable[str] = (),
    additions: Iterable[tuple[CustomItemArchive, str, str | None]] = (),
    force: bool = False,
) -> Path:
    destination = ensure_safe_output(output, inputs=[base.path], force=force)
    replacements = dict(replacements or {})
    skipped = set(skip)
    additions = list(additions)

    final_names = {name for name in base.names if name not in skipped}
    for archive, source_name, destination_name in additions:
        if source_name not in archive.infos:
            raise InvalidArchiveError(f"Additional entry does not exist: {source_name!r}")
        target = destination_name or source_name
        if target in final_names:
            raise InvalidArchiveError(f"Output would contain duplicate path: {target}")
        reason = _unsafe_entry_reason(target)
        if reason:
            raise InvalidArchiveError(f"Unsafe additional path {target!r}: {reason}")
        final_names.add(target)

    unknown_replacements = set(replacements) - set(base.names)
    if unknown_replacements:
        names = ", ".join(sorted(unknown_replacements))
        raise InvalidArchiveError(f"Cannot replace non-existent entries: {names}")

    temp_path: Path | None = None
    try:
        handle = tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        )
        temp_path = Path(handle.name)
        handle.close()

        with zipfile.ZipFile(temp_path, "w", allowZip64=True) as target_zip:
            target_zip.comment = base.zip_file.comment
            for name in base.names:
                if name in skipped:
                    continue
                if name in replacements:
                    info = clone_zipinfo(base.infos[name])
                    target_zip.writestr(info, replacements[name])
                else:
                    _copy_entry(base, name, target_zip)
            for archive, source_name, destination_name in additions:
                _copy_entry(
                    archive,
                    source_name,
                    target_zip,
                    destination_name=destination_name,
                )

        with CustomItemArchive(temp_path) as written:
            bad_entry = written.zip_file.testzip()
            if bad_entry:
                raise InvalidArchiveError(
                    f"Temporary output has invalid CRC: {bad_entry}"
                )
            _ = written.metadata

        os.replace(temp_path, destination)
        temp_path = None
        return destination
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
