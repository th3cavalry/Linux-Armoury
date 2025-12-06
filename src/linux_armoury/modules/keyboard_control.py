#!/usr/bin/env python3
"""
Keyboard Control Module for Linux Armoury

Provides keyboard backlight and Aura RGB control for ASUS laptops.
"""

import os
import glob
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum


class AuraEffect(Enum):
    """Aura RGB lighting effects"""
    STATIC = "Static"
    BREATHE = "Breathe"
    COLOR_CYCLE = "ColorCycle"
    RAINBOW = "Rainbow"
    STAR = "Star"
    RAIN = "Rain"
    HIGHLIGHT = "Highlight"
    LASER = "Laser"
    RIPPLE = "Ripple"
    STROBE = "Strobe"
    COMET = "Comet"
    FLASH = "Flash"
    MULTI_STATIC = "MultiStatic"


@dataclass
class RGB:
    """RGB color value"""
    red: int
    green: int
    blue: int

    def __post_init__(self):
        self.red = max(0, min(255, self.red))
        self.green = max(0, min(255, self.green))
        self.blue = max(0, min(255, self.blue))

    def to_hex(self) -> str:
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    @classmethod
    def from_hex(cls, hex_color: str) -> "RGB":
        hex_color = hex_color.lstrip("#")
        return cls(
            red=int(hex_color[0:2], 16),
            green=int(hex_color[2:4], 16),
            blue=int(hex_color[4:6], 16)
        )


class KeyboardController:
    """Controls keyboard backlight and Aura RGB"""

    KBD_BACKLIGHT_PATH = "/sys/class/leds/asus::kbd_backlight"

    # Predefined colors
    PRESET_COLORS = {
        "red": RGB(255, 0, 0),
        "green": RGB(0, 255, 0),
        "blue": RGB(0, 0, 255),
        "white": RGB(255, 255, 255),
        "yellow": RGB(255, 255, 0),
        "cyan": RGB(0, 255, 255),
        "magenta": RGB(255, 0, 255),
        "orange": RGB(255, 165, 0),
        "purple": RGB(128, 0, 128),
        "pink": RGB(255, 192, 203),
    }

    def __init__(self):
        self._backlight_path: Optional[str] = None
        self._max_brightness: int = 3
        self._has_rgb: bool = False
        self._detect_hardware()

    def _detect_hardware(self):
        """Detect keyboard backlight hardware"""
        if os.path.exists(self.KBD_BACKLIGHT_PATH):
            self._backlight_path = self.KBD_BACKLIGHT_PATH

            # Get max brightness
            max_path = os.path.join(self._backlight_path, "max_brightness")
            if os.path.exists(max_path):
                try:
                    with open(max_path, "r") as f:
                        self._max_brightness = int(f.read().strip())
                except Exception:
                    pass

            # Check for RGB support
            multi_intensity = os.path.join(self._backlight_path, "multi_intensity")
            if os.path.exists(multi_intensity):
                self._has_rgb = True

    def is_supported(self) -> bool:
        """Check if keyboard backlight is supported"""
        return self._backlight_path is not None

    def has_rgb(self) -> bool:
        """Check if RGB control is supported"""
        return self._has_rgb

    def get_brightness(self) -> Optional[int]:
        """Get current backlight brightness (0 to max)"""
        if not self._backlight_path:
            return None
        try:
            brightness_path = os.path.join(self._backlight_path, "brightness")
            with open(brightness_path, "r") as f:
                return int(f.read().strip())
        except Exception:
            return None

    def get_max_brightness(self) -> int:
        """Get maximum brightness level"""
        return self._max_brightness

    def set_brightness(self, level: int) -> Tuple[bool, str]:
        """Set backlight brightness (0 to max)"""
        if not self._backlight_path:
            return False, "Keyboard backlight not supported"

        level = max(0, min(self._max_brightness, level))

        try:
            brightness_path = os.path.join(self._backlight_path, "brightness")
            with open(brightness_path, "w") as f:
                f.write(str(level))
            return True, f"Brightness set to {level}"
        except PermissionError:
            return False, "Permission denied. Try running as root."
        except Exception as e:
            return False, str(e)

    def cycle_brightness(self) -> Tuple[bool, str]:
        """Cycle to next brightness level"""
        current = self.get_brightness()
        if current is None:
            return False, "Could not read current brightness"

        next_level = (current + 1) % (self._max_brightness + 1)
        return self.set_brightness(next_level)

    def get_rgb_color(self) -> Optional[RGB]:
        """Get current RGB color (if supported)"""
        if not self._has_rgb:
            return None

        try:
            mi_path = os.path.join(self._backlight_path, "multi_intensity")
            with open(mi_path, "r") as f:
                values = f.read().strip().split()
            if len(values) >= 3:
                return RGB(
                    red=int(values[0]),
                    green=int(values[1]),
                    blue=int(values[2])
                )
        except Exception:
            pass
        return None

    def set_rgb_color(self, color: RGB) -> Tuple[bool, str]:
        """Set RGB color (if supported)"""
        if not self._has_rgb:
            return False, "RGB control not supported"

        try:
            mi_path = os.path.join(self._backlight_path, "multi_intensity")
            value = f"{color.red} {color.green} {color.blue}"
            with open(mi_path, "w") as f:
                f.write(value)
            return True, f"Color set to {color.to_hex()}"
        except PermissionError:
            return False, "Permission denied. Try running as root."
        except Exception as e:
            return False, str(e)

    def set_preset_color(self, name: str) -> Tuple[bool, str]:
        """Set a preset color by name"""
        if name.lower() not in self.PRESET_COLORS:
            return False, f"Unknown color: {name}"
        return self.set_rgb_color(self.PRESET_COLORS[name.lower()])

    def get_keyboard_info(self) -> Dict:
        """Get comprehensive keyboard info"""
        info = {
            "supported": self.is_supported(),
            "has_rgb": self.has_rgb(),
            "brightness": self.get_brightness(),
            "max_brightness": self._max_brightness,
        }

        if self._has_rgb:
            color = self.get_rgb_color()
            if color:
                info["color"] = color.to_hex()

        return info


# Global singleton
_kbd_controller: Optional[KeyboardController] = None


def get_keyboard_controller() -> KeyboardController:
    """Get singleton keyboard controller instance"""
    global _kbd_controller
    if _kbd_controller is None:
        _kbd_controller = KeyboardController()
    return _kbd_controller
