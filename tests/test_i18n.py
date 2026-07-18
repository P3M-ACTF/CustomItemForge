from custom_item_forge.i18n import translate


def test_translate_en_default() -> None:
    assert translate("app.title", "en") == "CustomItemForge"


def test_translate_es() -> None:
    assert translate("menu.open", "es") == "Abrir…"


def test_translate_fallback() -> None:
    assert translate("app.title", "xx") == "CustomItemForge"
