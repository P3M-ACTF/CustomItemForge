"""Build release artifacts into the CustomItemForge project root."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipapp
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "release"
DIST = ROOT / "dist"
PYZ_NAME = "CustomItemForge.pyz"
PYW_NAME = "CustomItemForge_Win.pyw"
SH_NAME = "CustomItemForge.sh"
README_NAME = "RELEASE.txt"
RELEASE_FILES = (PYZ_NAME, PYW_NAME, SH_NAME, README_NAME)

# No CLI args → GUI. With args → CLI (inspect, gui, validate, …).
MAIN_PY = """\
import sys


def _run_gui() -> None:
    from custom_item_forge.ui.app import main
    main()


def _run_cli() -> int:
    from custom_item_forge.cli.main import main
    return main()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _run_gui()
    else:
        raise SystemExit(_run_cli())
"""

PYW_RELEASE = f'''\
"""CustomItemForge GUI launcher (release). Double-click to open the app (no console)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYZ = HERE / "{PYZ_NAME}"

if not PYZ.is_file():
    raise SystemExit(
        f"Missing {{PYZ.name}} in {{HERE}}. Run scripts/build_release.py first."
    )

# Import from the .pyz inside this pythonw process.
# Do NOT exec python.exe / the .pyz - that opens a console window on Windows.
sys.path.insert(0, str(PYZ) + "/site-packages")
from custom_item_forge.ui.app import main

main()
'''

SH_RELEASE = f"""\
#!/bin/sh
# CustomItemForge GUI launcher (release)
DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
PYZ="$DIR/{PYZ_NAME}"
if [ ! -f "$PYZ" ]; then
  echo "Missing {PYZ_NAME} in $DIR" >&2
  exit 1
fi
if [ "$#" -eq 0 ]; then
  exec python3 "$PYZ"
fi
exec python3 "$PYZ" "$@"
"""

README_RELEASE = f"""\
CustomItemForge (for VRoid) — release bundle
============================================

Requirements: Python 3.12 or newer with Tkinter.

Windows
-------
  GUI (no console): double-click {PYW_NAME}
  CLI:              python {PYZ_NAME} inspect item.vroidcustomitem

macOS / Linux
-------------
  GUI:  ./{SH_NAME}
  CLI:  python3 {PYZ_NAME} inspect item.vroidcustomitem

Notes
-----
- For the GUI on Windows, use {PYW_NAME} — do not double-click {PYZ_NAME}
  (that opens a console). The .pyz file is for the command line.
- Original .vroidcustomitem files are never modified.
- Merge and recategorize may be unavailable until calibration samples are provided.
- Thumbnail previews work best when Pillow is available in the build (included in release).
"""


def _safe_rmtree(path: Path) -> None:
    if not path.exists():
        return

    def _onexc(_func, target: str, _exc: BaseException) -> None:
        import os
        import stat

        os.chmod(target, stat.S_IWRITE)
        if os.path.isdir(target):
            shutil.rmtree(target, onexc=_onexc)
        else:
            os.remove(target)

    shutil.rmtree(path, onexc=_onexc)


def build_pyz(*, clean: bool = True) -> Path:
    if clean and BUILD.exists():
        _safe_rmtree(BUILD)
    BUILD.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            ".[gui]",
            "--target",
            str(BUILD / "site-packages"),
            "--upgrade",
        ],
        cwd=ROOT,
        check=True,
    )

    (BUILD / "__main__.py").write_text(MAIN_PY, encoding="utf-8")

    output = ROOT / PYZ_NAME
    zipapp.create_archive(
        BUILD,
        target=output,
        interpreter="/usr/bin/env python3",
        compressed=True,
    )
    return output


def write_launchers() -> list[Path]:
    written: list[Path] = []

    pyw = ROOT / PYW_NAME
    pyw.write_text(PYW_RELEASE, encoding="utf-8")
    written.append(pyw)

    sh = ROOT / SH_NAME
    sh.write_text(SH_RELEASE, encoding="utf-8", newline="\n")
    sh.chmod(sh.stat().st_mode | 0o111)
    written.append(sh)

    readme = ROOT / README_NAME
    readme.write_text(README_RELEASE, encoding="utf-8")
    written.append(readme)

    return written


def _release_label(tag: str | None) -> str:
    if tag:
        return tag.removeprefix("refs/tags/").lstrip("v")
    from custom_item_forge import __version__

    return __version__


def pack_zip(*, tag: str | None = None, output_dir: Path | None = None) -> Path:
    """Pack release artifacts into CustomItemForge-<label>.zip with one root folder."""
    label = _release_label(tag)
    folder_name = f"CustomItemForge-{label}"
    out_dir = output_dir or DIST
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{folder_name}.zip"

    missing = [name for name in RELEASE_FILES if not (ROOT / name).is_file()]
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing release file(s): {missing_list}. Run build_release.py first."
        )

    staging = out_dir / folder_name
    if staging.exists():
        _safe_rmtree(staging)
    staging.mkdir(parents=True)

    for name in RELEASE_FILES:
        shutil.copy2(ROOT / name, staging / name)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in staging.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(out_dir).as_posix())

    _safe_rmtree(staging)
    return zip_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CustomItemForge release bundle")
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Reuse existing build/ release staging folder",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create dist/CustomItemForge-<version>.zip for GitHub Releases",
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Release tag for zip name (e.g. v0.1.0-preview). Defaults to package version.",
    )
    args = parser.parse_args(argv)

    pyz = build_pyz(clean=not args.no_clean)
    launchers = write_launchers()

    print(f"Created {pyz} ({pyz.stat().st_size:,} bytes)")
    for path in launchers:
        print(f"Created {path}")
    print()
    print("Release bundle ready in:", ROOT)
    print(f"  Windows GUI : {PYW_NAME}")
    print(f"  Unix GUI    : {SH_NAME}")
    print(f"  CLI example : python {PYZ_NAME} inspect item.vroidcustomitem")

    if args.zip:
        zip_path = pack_zip(tag=args.tag)
        print()
        print(f"Release zip : {zip_path} ({zip_path.stat().st_size:,} bytes)")
        print("  Upload this file as a GitHub Release asset, or publish a Release to build it in CI.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
