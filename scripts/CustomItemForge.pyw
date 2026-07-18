"""Development GUI launcher — runs from source (not the release bundle).

For end users, build and use dist/CustomItemForge.pyw instead:
  python scripts/build_release.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

runpy.run_module("custom_item_forge.ui.app", run_name="__main__")
