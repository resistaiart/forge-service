# forge_public_interface.py
from enum import Enum

class PackageGoal(str, Enum):
    T2I = "t2i"  # Text-to-Image
    T2V = "t2v"  # Text-to-Video
    I2I = "i2i"  # Image-to-Image
    I2V = "i2v"  # Image-to-Video

