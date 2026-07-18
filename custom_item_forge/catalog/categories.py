"""Conservative catalog of known VRoid Studio 2.x categories."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ItemCategory:
    key: str
    label_en: str
    label_es: str
    suffix: str
    family: str
    template_hint: str | None = None

    @property
    def transferable_id(self) -> str:
        return f"TransferableGroupType.N00.Level1.{self.suffix}"

    @property
    def transferable_type(self) -> str:
        return f"TransferableType.N00.{self.suffix}"

    @property
    def internal_name(self) -> str:
        return f"N00-{self.suffix}"

    def label(self, language: str = "en") -> str:
        return self.label_es if language == "es" else self.label_en

    def display(self, language: str = "en") -> str:
        return f"{self.label(language)} — {self.internal_name}"


CATEGORIES: tuple[ItemCategory, ...] = (
    ItemCategory("all-hair", "Overall hair", "Cabello completo", "AllHair", "hair"),
    ItemCategory("base-hair", "Base hair", "Cabello base", "BaseHair", "hair"),
    ItemCategory("hair-front", "Front hair", "Cabello frontal", "HairFront", "hair"),
    ItemCategory("hair-back", "Back hair", "Cabello trasero", "HairBack", "hair"),
    ItemCategory("hair-side", "Sideburns", "Patillas", "HairSideburns", "hair"),
    ItemCategory("hair-tied", "Extensions", "Extensiones", "HairTied", "hair"),
    ItemCategory("hair-ahoge", "Ahoge", "Ahoge", "HairAhoge", "hair"),
    ItemCategory("hair-extra", "Extra", "Extra", "HairHanege", "hair"),
    ItemCategory("tops", "Tops", "Prendas superiores", "Tops", "clothing"),
    ItemCategory("bottoms", "Bottoms", "Prendas inferiores", "Bottoms", "clothing"),
    ItemCategory("onepiece", "One-piece", "Prenda de una pieza", "Onepiece", "clothing"),
    ItemCategory("shoes", "Shoes", "Calzado", "Shoes", "clothing"),
    ItemCategory("socks", "Socks", "Calcetines", "Socks", "clothing"),
    ItemCategory(
        "glasses",
        "Glasses",
        "Gafas",
        "Glasses",
        "accessory",
        template_hint="Accessory_GlassesHi",
    ),
    ItemCategory(
        "neck-accessory",
        "Neck accessory",
        "Accesorio de cuello",
        "NeckAccessory",
        "accessory",
    ),
    ItemCategory(
        "arm-accessory",
        "Arm accessory",
        "Accesorio de brazo",
        "ArmAccessory",
        "accessory",
    ),
    ItemCategory(
        "leg-accessory",
        "Leg accessory",
        "Accesorio de pierna",
        "LegAccessory",
        "accessory",
    ),
)

BY_KEY = {category.key: category for category in CATEGORIES}
BY_ID = {category.transferable_id: category for category in CATEGORIES}
BY_SUFFIX = {category.suffix: category for category in CATEGORIES}
ALIASES = {
    "overall": "all-hair",
    "base": "base-hair",
    "front": "hair-front",
    "back": "hair-back",
    "side": "hair-side",
    "extension": "hair-tied",
    "ahoge": "hair-ahoge",
    "extra": "hair-extra",
}


def resolve_category(value: str) -> ItemCategory:
    normalized = value.strip()
    if normalized in BY_ID:
        return BY_ID[normalized]
    if normalized in BY_SUFFIX:
        return BY_SUFFIX[normalized]
    if normalized.lower() in ALIASES:
        return BY_KEY[ALIASES[normalized.lower()]]
    try:
        return BY_KEY[normalized.lower()]
    except KeyError as exc:
        options = ", ".join(BY_KEY)
        raise ValueError(f"Unknown category: {value!r}. Options: {options}") from exc


def category_label(identifier: str | None, language: str = "en") -> str:
    if identifier is None:
        return "Desconocida" if language == "es" else "Unknown"
    category = BY_ID.get(identifier)
    return category.label(language) if category else identifier.rsplit(".", 1)[-1]


def category_family(identifier: str | None) -> str | None:
    category = BY_ID.get(identifier or "")
    return category.family if category else None


def categories_for_family(family: str, *, language: str = "en") -> list[ItemCategory]:
    return [item for item in CATEGORIES if item.family == family]
