"""Linux Armoury - GTK4/libadwaita control center for ASUS ROG laptops."""

__version__ = "1.2.0"
__author__ = "th3cavalry"

from .config import Config
from .system_utils import DisplayBackend, SystemUtils

__all__ = ["Config", "SystemUtils", "DisplayBackend", "__version__", "__author__"]
