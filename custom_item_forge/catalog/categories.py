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
    # Studio 2.14.0 top-level tab where the slot appears in the UI
    studio_tab: str = ""

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
    # Hairstyle
    ItemCategory("all-hair", "Overall hair", "Cabello completo", "AllHair", "hair", studio_tab="Hairstyle"),
    ItemCategory("base-hair", "Base hair", "Cabello base", "BaseHair", "hair", studio_tab="Hairstyle"),
    ItemCategory("hair-front", "Front hair", "Cabello frontal", "HairFront", "hair", studio_tab="Hairstyle"),
    ItemCategory("hair-back", "Back hair", "Cabello trasero", "HairBack", "hair", studio_tab="Hairstyle"),
    ItemCategory("hair-side", "Sideburns", "Patillas", "HairSideburns", "hair", studio_tab="Hairstyle"),
    ItemCategory("hair-tied", "Extensions", "Extensiones", "HairTied", "hair", studio_tab="Hairstyle"),
    ItemCategory("hair-ahoge", "Ahoge", "Ahoge", "HairAhoge", "hair", studio_tab="Hairstyle"),
    ItemCategory("hair-extra", "Extra", "Extra", "HairHanege", "hair", studio_tab="Hairstyle"),
    # Outfit (clothing family)
    ItemCategory("tops", "Tops", "Prendas superiores", "Tops", "clothing", studio_tab="Outfit"),
    ItemCategory("bottoms", "Bottoms", "Prendas inferiores", "Bottoms", "clothing", studio_tab="Outfit"),
    ItemCategory("onepiece", "Dresses / one-piece", "Vestidos / prenda de una pieza", "Onepiece", "clothing", studio_tab="Outfit"),
    ItemCategory("shoes", "Shoes", "Calzado", "Shoes", "clothing", studio_tab="Outfit"),
    ItemCategory("socks", "Socks", "Calcetines", "Socks", "clothing", studio_tab="Outfit"),
    # Outfit UI slots that use accessory payloads (family = accessory until Studio says otherwise)
    ItemCategory(
        "neck-accessory",
        "Neck accessory",
        "Accesorio de cuello",
        "NeckAccessory",
        "accessory",
        studio_tab="Outfit",
    ),
    ItemCategory(
        "arm-accessory",
        "Arm accessory",
        "Accesorio de brazo",
        "ArmAccessory",
        "accessory",
        studio_tab="Outfit",
    ),
    ItemCategory(
        "leg-accessory",
        "Leg accessory",
        "Accesorio de pierna",
        "LegAccessory",
        "accessory",
        studio_tab="Outfit",
    ),
    # Accessories tab
    ItemCategory(
        "glasses",
        "Glasses",
        "Gafas",
        "Glasses",
        "accessory",
        template_hint="Accessory_GlassesHi",
        studio_tab="Accessories",
    ),
)

# Studio 2.14.0 UI slots whose TransferableGroupType suffix is not yet confirmed
# by a real .vroidcustomitem probe. Do not invent suffixes — add ItemCategory entries
# only after `cif probe` on an export.
UNCONFIRMED_STUDIO_SLOTS: tuple[dict[str, str], ...] = (
    {"ui": "Inner_Top", "studio_tab": "Outfit", "expected_family": "clothing"},
    {"ui": "Inner_Bottom", "studio_tab": "Outfit", "expected_family": "clothing"},
    {"ui": "FurryEars", "studio_tab": "Accessories", "expected_family": "accessory"},
    {"ui": "Tail", "studio_tab": "Accessories", "expected_family": "accessory"},
    {"ui": "Hats", "studio_tab": "Accessories", "expected_family": "accessory"},
    {"ui": "Custom", "studio_tab": "Accessories", "expected_family": "accessory"},
    {"ui": "Hairstyle_Sets", "studio_tab": "Hairstyle", "expected_family": "hair", "note": "no Custom — skip"},
    {"ui": "Whole_Set", "studio_tab": "Outfit", "expected_family": "clothing", "note": "no Custom — skip"},
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
    "extensions": "hair-tied",
    "ahoge": "hair-ahoge",
    "extra": "hair-extra",
    "dresses": "onepiece",
    "dress": "onepiece",
    "one-piece": "onepiece",
}


def resolve_category(value: str) -> ItemCategory:
    normalized = value.strip()
    if normalized in BY_ID:
        return BY_ID[normalized]
    if normalized in BY_SUFFIX:
        return BY_SUFFIX[normalized]
    lowered = normalized.lower()
    if lowered in ALIASES:
        return BY_KEY[ALIASES[lowered]]
    try:
        return BY_KEY[lowered]
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
