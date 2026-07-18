"""Domain exceptions with user-facing messages."""


class ForgeError(Exception):
    """Expected error during a CustomItemForge operation."""


class InvalidArchiveError(ForgeError):
    """The file is not a compatible container or is unsafe."""


class UnsupportedFormatError(ForgeError):
    """The file is valid but its variant is not supported yet."""


class CollisionError(ForgeError):
    """Two incompatible resources would occupy the same container path."""


class UnsafeOutputError(ForgeError):
    """The requested output could overwrite an input or lose data."""


class NotCalibratedError(ForgeError):
    """A family engine needs real calibration samples before this operation."""
