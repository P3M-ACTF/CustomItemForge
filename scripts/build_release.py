"""Build release artifacts into the CustomItemForge project root."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipapp
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "release"
PYZ_NAME = "CustomItemForge.pyz"
PYW_NAME = "CustomItemForge_Win.pyw"
SH_NAME = "CustomItemForge.sh"
README_NAME = "RELEASE.txt"

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
"""CustomItemForge GUI launcher (release). Double-click to open the app."""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYZ = HERE / "{PYZ_NAME}"

if not PYZ.is_file():
    raise SystemExit(
        f"Missing {{PYZ.name}} in {{HERE}}. Run scripts/build_release.py first."
    )

os.execv(sys.executable, [sys.executable, str(PYZ)])
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
                    python {PYZ_NAME} gui

macOS / Linux
-------------
  GUI:  ./{SH_NAME}
  CLI:  python3 {PYZ_NAME} inspect item.vroidcustomitem
        python3 {PYZ_NAME} gui

Notes
-----
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CustomItemForge release bundle")
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Reuse existing build/ release staging folder",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
