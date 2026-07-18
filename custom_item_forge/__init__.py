"""CustomItemForge — tools for .vroidcustomitem files (for VRoid)."""

from custom_item_forge.core.model import (
    InspectReport,
    MergeReport,
    ThumbnailState,
    ValidationReport,
)

__all__ = [
    "InspectReport",
    "MergeReport",
    "ThumbnailState",
    "ValidationReport",
    "__version__",
    "REPO_URL",
]

__version__ = "0.1.0"
REPO_URL = "https://github.com/P3M-ACTF/VRoidTools"
