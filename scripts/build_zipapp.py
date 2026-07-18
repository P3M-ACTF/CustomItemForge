"""Build a zipapp distribution for CustomItemForge."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipapp
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUILD = ROOT / "build" / "zipapp"


def main() -> int:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    DIST.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [sys.executable, "-m", "pip", "install", ".", "--target", str(BUILD / "site-packages")],
        cwd=ROOT,
        check=True,
    )

    main_script = BUILD / "__main__.py"
    main_script.write_text(
        "from custom_item_forge.cli.main import main\n"
        "raise SystemExit(main())\n",
        encoding="utf-8",
    )

    output = DIST / "CustomItemForge.pyz"
    zipapp.create_archive(
        BUILD,
        target=output,
        interpreter="/usr/bin/env python3",
        compressed=True,
    )
    print(f"Created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
