"""Text helpers for compact UI rendering."""

from __future__ import annotations


def format_field_value(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple, set)):
        if not value:
            return "—"
        return ", ".join(str(item) for item in value)
    return str(value)


def is_wide_value(value: object, *, threshold: int = 48) -> bool:
    text = format_field_value(value)
    return len(text) > threshold or "\n" in text
