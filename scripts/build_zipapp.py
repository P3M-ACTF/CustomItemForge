"""Build a zipapp distribution for CustomItemForge (legacy entry point)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_release import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
