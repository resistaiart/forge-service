# forge/public_interface.py
from enum import Enum
from typing import List


class PackageGoal(str, Enum):
    """Enumeration of supported Forge package goals."""
    T2I = "t2i"          # Text-to-Image
    T2V = "t2v"          # Text-to-Video
    I2I = "i2i"          # Image-to-Image
    I2V = "i2v"          # Image-to-Video
    UPSCALE = "upscale"  # Image Upscaling
    INTERROGATE = "interrogate"  # Image Interrogation / Captioning


def valid_goals() -> List[str]:
    """Return a list of all valid package goals."""
    return [g.value for g in PackageGoal]


def is_valid_goal(goal: str) -> bool:
    """Check if a goal string is a valid Forge package goal."""
    return goal in valid_goals()
