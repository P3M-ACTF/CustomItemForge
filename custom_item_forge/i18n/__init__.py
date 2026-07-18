"""Lightweight i18n for UI and domain messages."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "es")


@lru_cache(maxsize=8)
def _load_catalog(locale: str) -> dict[str, str]:
    normalized = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    filename = f"{normalized}.json"
    with resources.files("custom_item_forge.i18n").joinpath(filename).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def translate(key: str, locale: str = DEFAULT_LOCALE, **kwargs: Any) -> str:
    catalog = _load_catalog(locale)
    template = catalog.get(key) or _load_catalog(DEFAULT_LOCALE).get(key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def section_title(section_id: str, locale: str = DEFAULT_LOCALE) -> str:
    mapping = {
        "vroid": "section.vroid",
        "vroidcustomitem": "section.vroidcustomitem",
        "file": "section.file",
    }
    return translate(mapping.get(section_id, section_id), locale)
