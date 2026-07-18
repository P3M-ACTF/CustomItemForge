"""Minimal schema-agnostic Protocol Buffers wire reader/writer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from custom_item_forge.core.errors import UnsupportedFormatError


@dataclass(frozen=True, slots=True)
class WireField:
    number: int
    wire_type: int
    value: int | bytes
    raw: bytes

    def text(self) -> str | None:
        if self.wire_type != 2 or not isinstance(self.value, bytes):
            return None
        try:
            result = self.value.decode("utf-8")
        except UnicodeDecodeError:
            return None
        if not result or any(ord(char) < 0x20 and char not in "\t\r\n" for char in result):
            return None
        return result


def decode_varint(data: bytes, offset: int = 0) -> tuple[int, int]:
    value = 0
    shift = 0
    for index in range(offset, min(len(data), offset + 10)):
        byte = data[index]
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, index + 1
        shift += 7
    raise UnsupportedFormatError("Truncated or oversized varint")


def encode_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("encode_varint only accepts non-negative integers")
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def encode_field(number: int, wire_type: int, value: int | bytes) -> bytes:
    if number <= 0:
        raise ValueError("Field number must be positive")
    key = encode_varint((number << 3) | wire_type)
    if wire_type == 0:
        if not isinstance(value, int):
            raise TypeError("varint requires an integer")
        return key + encode_varint(value)
    if wire_type == 1:
        if not isinstance(value, bytes) or len(value) != 8:
            raise TypeError("fixed64 requires exactly 8 bytes")
        return key + value
    if wire_type == 2:
        if not isinstance(value, bytes):
            raise TypeError("length-delimited field requires bytes")
        return key + encode_varint(len(value)) + value
    if wire_type == 5:
        if not isinstance(value, bytes) or len(value) != 4:
            raise TypeError("fixed32 requires exactly 4 bytes")
        return key + value
    raise ValueError(f"Unsupported wire type: {wire_type}")


def encode_text(number: int, value: str) -> bytes:
    return encode_field(number, 2, value.encode("utf-8"))


def parse_fields(data: bytes, *, max_fields: int = 100_000) -> list[WireField]:
    fields: list[WireField] = []
    offset = 0
    while offset < len(data):
        if len(fields) >= max_fields:
            raise UnsupportedFormatError("Protobuf message exceeds field limit")
        start = offset
        key, offset = decode_varint(data, offset)
        number = key >> 3
        wire_type = key & 0x07
        if number == 0:
            raise UnsupportedFormatError("Protobuf field number zero")

        if wire_type == 0:
            value, offset = decode_varint(data, offset)
        elif wire_type == 1:
            end = offset + 8
            if end > len(data):
                raise UnsupportedFormatError("Truncated fixed64 field")
            value = data[offset:end]
            offset = end
        elif wire_type == 2:
            length, offset = decode_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise UnsupportedFormatError("Truncated length-delimited field")
            value = data[offset:end]
            offset = end
        elif wire_type == 5:
            end = offset + 4
            if end > len(data):
                raise UnsupportedFormatError("Truncated fixed32 field")
            value = data[offset:end]
            offset = end
        elif wire_type in (3, 4):
            raise UnsupportedFormatError("Legacy Protobuf groups are not supported")
        else:
            raise UnsupportedFormatError(f"Invalid wire type: {wire_type}")

        fields.append(WireField(number, wire_type, value, data[start:offset]))
    return fields


def summarize_fields(fields: list[WireField]) -> dict[int, dict[str, Any]]:
    summary: dict[int, dict[str, Any]] = {}
    for field in fields:
        item = summary.setdefault(
            field.number,
            {"count": 0, "wire_types": set(), "text_samples": []},
        )
        item["count"] += 1
        item["wire_types"].add(field.wire_type)
        text = field.text()
        if text is not None and len(item["text_samples"]) < 3:
            item["text_samples"].append(text[:160])
    for item in summary.values():
        item["wire_types"] = sorted(item["wire_types"])
    return summary
