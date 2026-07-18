"""CustomItemForge command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from custom_item_forge import __version__
from custom_item_forge.catalog.categories import CATEGORIES
from custom_item_forge.core.errors import ForgeError, NotCalibratedError
from custom_item_forge.engines.router import FamilyRouter
from custom_item_forge.i18n import section_title, translate
from custom_item_forge.ops.clone import clone_item
from custom_item_forge.ops.compare import compare_items
from custom_item_forge.ops.compatibility import compatibility_report
from custom_item_forge.ops.inspect import inspect_item
from custom_item_forge.ops.probe import probe_item
from custom_item_forge.ops.validate import validate_item


def _print_inspect(report, *, locale: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return 0
    print(f"Path: {report.path}")
    for section in report.sections:
        print()
        print(f"=== {section_title(section.id, locale)} ===")
        for field in section.fields:
            label = translate(field.label_key or field.key, locale)
            print(f"  {label}: {field.value}")
    return 0


def _print_validation(report, *, as_json: bool) -> int:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        for issue in report.issues:
            prefix = issue.severity.upper()
            entry = f" [{issue.entry}]" if issue.entry else ""
            print(f"{prefix}: {issue.message}{entry}")
    return 0 if report.valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cif",
        description="CustomItemForge — tools for .vroidcustomitem files (for VRoid)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--locale", choices=("en", "es"), default="en")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    sub = parser.add_subparsers(dest="command", required=True)

    inspect_cmd = sub.add_parser("inspect", help="Inspect a custom item")
    inspect_cmd.add_argument("path", type=Path)

    validate_cmd = sub.add_parser("validate", help="Validate container integrity")
    validate_cmd.add_argument("path", type=Path)
    validate_cmd.add_argument("--no-crc", action="store_true")

    clone_cmd = sub.add_parser("clone", help="Repackage without changes")
    clone_cmd.add_argument("source", type=Path)
    clone_cmd.add_argument("output", type=Path)
    clone_cmd.add_argument("--force", action="store_true")

    compare_cmd = sub.add_parser("compare", help="Compare two items")
    compare_cmd.add_argument("left", type=Path)
    compare_cmd.add_argument("right", type=Path)

    probe_cmd = sub.add_parser("probe", help="List root group candidates")
    probe_cmd.add_argument("path", type=Path)

    compat_cmd = sub.add_parser("compatibility", help="Show family compatibility")
    compat_cmd.add_argument("path", type=Path)

    categories_cmd = sub.add_parser("categories", help="List known categories")
    categories_cmd.add_argument("--family", choices=("hair", "clothing", "accessory"))

    recat_cmd = sub.add_parser("recategorize", help="Recategorize within a family")
    recat_cmd.add_argument("source", type=Path)
    recat_cmd.add_argument("output", type=Path)
    recat_cmd.add_argument("category")
    recat_cmd.add_argument("--force", action="store_true")

    merge_cmd = sub.add_parser("merge", help="Merge two items within a family")
    merge_cmd.add_argument("base", type=Path)
    merge_cmd.add_argument("addon", type=Path)
    merge_cmd.add_argument("output", type=Path)
    merge_cmd.add_argument("--force", action="store_true")

    sub.add_parser("gui", help="Launch the unified GUI")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    locale = args.locale
    as_json = args.json

    try:
        if args.command == "inspect":
            report = inspect_item(args.path, language=locale)
            return _print_inspect(report, locale=locale, as_json=as_json)

        if args.command == "validate":
            report = validate_item(args.path, verify_crc=not args.no_crc)
            return _print_validation(report, as_json=as_json)

        if args.command == "clone":
            output = clone_item(args.source, args.output, force=args.force)
            print(output)
            return 0

        if args.command == "compare":
            result = compare_items(args.left, args.right, language=locale)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        if args.command == "probe":
            result = probe_item(args.path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        if args.command == "compatibility":
            from custom_item_forge.core.archive import CustomItemArchive

            with CustomItemArchive(args.path) as archive:
                report = compatibility_report(archive.category_id, language=locale)
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "categories":
            items = CATEGORIES
            if args.family:
                items = tuple(item for item in items if item.family == args.family)
            payload = [
                {
                    "key": item.key,
                    "family": item.family,
                    "label": item.label(locale),
                    "transferable_id": item.transferable_id,
                    "transferable_type": item.transferable_type,
                }
                for item in items
            ]
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        if args.command == "recategorize":
            router = FamilyRouter()
            output = router.recategorize(args.source, args.output, args.category, force=args.force)
            print(output)
            return 0

        if args.command == "merge":
            router = FamilyRouter()
            report = router.merge(args.base, args.addon, args.output, force=args.force)
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "gui":
            from custom_item_forge.ui.app import main as gui_main

            gui_main()
            return 0

    except NotCalibratedError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ForgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
