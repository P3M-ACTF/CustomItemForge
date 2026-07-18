"""Windows launcher without console window."""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

runpy.run_module("custom_item_forge.ui.app", run_name="__main__")
