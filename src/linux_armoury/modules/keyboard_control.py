#!/usr/bin/env python3
"""
Keyboard Control Module for Linux Armoury

Provides keyboard backlight and Aura RGB control for ASUS laptops.
"""

import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple


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
            blue=int(hex_color[4:6], 16),
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
        self._has_aura: bool = False
        self._has_gz302_rgb: bool = False
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

        # Check for Aura support (asusctl)
        self._detect_aura_support()

        # Check for gz302-rgb support (for ROG Flow Z13)
        self._detect_gz302_rgb_support()

    def _detect_aura_support(self):
        """Check if Aura effects are supported via asusctl"""
        try:
            # Try a simple asusctl aura command to check if the interface is available
            test_result = subprocess.run(
                ["asusctl", "aura", "static"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Check if Aura interface is available
            error_output = test_result.stderr + test_result.stdout
            if "Did not find xyz.ljones.Aura" in error_output:
                self._has_aura = False
            elif test_result.returncode == 0:
                self._has_aura = True
            else:
                # Command failed but not due to missing Aura interface
                # Consider it available (may work with proper arguments)
                self._has_aura = True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            # asusctl not available or timed out - no Aura support
            self._has_aura = False

    def _detect_gz302_rgb_support(self):
        """Check if gz302-rgb tool is available for ROG Flow Z13"""
        try:
            # Try a simple gz302-rgb command to check if the tool is available
            # gz302-rgb doesn't support --help, so we try an invalid command to see if it exists
            test_result = subprocess.run(
                ["gz302-rgb", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # gz302-rgb returns 1 and shows usage for invalid commands, which means it's available
            if test_result.returncode == 1 and "GZ302 RGB Keyboard Control" in test_result.stdout:
                self._has_gz302_rgb = True
            else:
                self._has_gz302_rgb = False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            # gz302-rgb not available
            self._has_gz302_rgb = False

    def is_supported(self) -> bool:
        """Check if keyboard backlight is supported"""
        return self._backlight_path is not None

    def has_rgb(self) -> bool:
        """Check if RGB control is supported"""
        return self._has_rgb

    def has_aura(self) -> bool:
        """Check if Aura effects are supported"""
        return self._has_aura

    def has_gz302_rgb(self) -> bool:
        """Check if gz302-rgb effects are supported"""
        return self._has_gz302_rgb

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
        brightness_path = os.path.join(self._backlight_path, "brightness")

        # 1. Try direct write (fastest, works with udev rules)
        try:
            with open(brightness_path, "w") as f:
                f.write(str(level))
            return True, f"Brightness set to {level}"
        except PermissionError:
            pass  # Fall through to fallback
        except Exception as e:
            return False, str(e)

        # 2. Try pkexec (fallback)
        try:
            # Use pkexec to write to the file
            cmd = ["pkexec", "sh", "-c", f"echo {level} > {brightness_path}"]
            subprocess.run(cmd, check=True)
            return True, f"Brightness set to {level} (via pkexec)"
        except subprocess.CalledProcessError:
            return False, "Failed to set brightness (pkexec denied or failed)"
        except Exception as e:
            return False, f"Error: {e}"

    def cycle_brightness(self) -> Tuple[bool, str]:
        """Cycle to next brightness level"""
        current = self.get_brightness()
        if current is None:
            return False, "Could not read current brightness"

        next_level = (current + 1) % (self._max_brightness + 1)
        return self.set_brightness(next_level)

    def get_rgb_color(self) -> Optional[RGB]:
        """Get current RGB color (if supported)"""
        if not self._has_rgb or not self._backlight_path:
            return None

        try:
            mi_path = os.path.join(self._backlight_path, "multi_intensity")
            with open(mi_path, "r") as f:
                values = f.read().strip().split()
            if len(values) >= 3:
                return RGB(
                    red=int(values[0]), green=int(values[1]), blue=int(values[2])
                )
        except Exception:
            pass
        return None

    def set_rgb_color(self, color: RGB) -> Tuple[bool, str]:
        """Set RGB color (if supported)"""
        if not self._has_rgb or not self._backlight_path:
            return False, "RGB control not supported"

        mi_path = os.path.join(self._backlight_path, "multi_intensity")
        value = f"{color.red} {color.green} {color.blue}"

        # 1. Try direct write
        try:
            with open(mi_path, "w") as f:
                f.write(value)
            return True, f"Color set to {color.to_hex()}"
        except PermissionError:
            pass  # Fall through to fallback
        except Exception as e:
            return False, str(e)

        # 2. Try pkexec (fallback)
        try:
            cmd = ["pkexec", "sh", "-c", f"echo '{value}' > {mi_path}"]
            subprocess.run(cmd, check=True)
            return True, f"Color set to {color.to_hex()} (via pkexec)"
        except subprocess.CalledProcessError:
            return False, "Failed to set color (pkexec denied or failed)"
        except Exception as e:
            return False, f"Error: {e}"

    def set_preset_color(self, name: str) -> Tuple[bool, str]:
        """Set a preset color by name"""
        if name.lower() not in self.PRESET_COLORS:
            return False, f"Unknown color: {name}"
        return self.set_rgb_color(self.PRESET_COLORS[name.lower()])

    def set_effect(self, effect: AuraEffect) -> Tuple[bool, str]:
        """Set keyboard lighting effect using gz302-rgb or asusctl"""
        try:
            # First try gz302-rgb if available (for ROG Flow Z13)
            if self._has_gz302_rgb:
                return self._set_gz302_effect(effect)

            # Fall back to asusctl Aura effects
            if self._has_aura:
                return self._set_aura_effect(effect)

            return False, "No keyboard effect support available"

        except Exception as e:
            return False, f"Error setting effect: {e}"

    def _set_gz302_effect(self, effect: AuraEffect) -> Tuple[bool, str]:
        """Set keyboard lighting effect using gz302-rgb"""
        try:
            # Map AuraEffect enum to gz302-rgb command arguments
            # gz302-rgb commands: single_static <HEX_COLOR>, single_breathing <HEX_COLOR1> <HEX_COLOR2> <SPEED>, etc.
            effect_map = {
                AuraEffect.STATIC: ["gz302-rgb", "single_static", "FF0066"],  # ROG pink default
                AuraEffect.BREATHE: ["gz302-rgb", "single_breathing", "FF0066", "000000", "2"],  # ROG pink breathing
                AuraEffect.COLOR_CYCLE: ["gz302-rgb", "single_colorcycle", "2"],  # Color cycling
                AuraEffect.RAINBOW: ["gz302-rgb", "rainbow_cycle", "2"],  # Rainbow animation
                AuraEffect.STAR: ["gz302-rgb", "single_static", "FFFFFF"],  # White fallback
                AuraEffect.RAIN: ["gz302-rgb", "rainbow_cycle", "2"],  # Rainbow as closest match
                AuraEffect.HIGHLIGHT: ["gz302-rgb", "single_static", "00FF00"],  # Green fallback
                AuraEffect.LASER: ["gz302-rgb", "single_breathing", "FF0000", "000000", "1"],  # Red breathing
                AuraEffect.RIPPLE: ["gz302-rgb", "single_breathing", "0000FF", "000000", "2"],  # Blue breathing
                AuraEffect.STROBE: ["gz302-rgb", "single_breathing", "FFFFFF", "000000", "3"],  # White fast breathing
                AuraEffect.COMET: ["gz302-rgb", "rainbow_cycle", "3"],  # Fast rainbow
                AuraEffect.FLASH: ["gz302-rgb", "single_breathing", "FFFF00", "000000", "3"],  # Yellow fast breathing
                AuraEffect.MULTI_STATIC: ["gz302-rgb", "single_static", "FF0066"],  # ROG pink fallback
            }

            if effect not in effect_map:
                return False, f"Unsupported effect: {effect.value}"

            cmd = effect_map[effect]

            # Try direct execution
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True, f"Effect set to {effect.value} (gz302-rgb)"
            else:
                return False, f"Failed to set effect: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error setting gz302-rgb effect: {e}"

    def _set_aura_effect(self, effect: AuraEffect) -> Tuple[bool, str]:
        """Set keyboard lighting effect using asusctl"""
        try:
            # Map AuraEffect enum to asusctl command arguments
            effect_map = {
                AuraEffect.STATIC: ["asusctl", "aura", "static"],
                AuraEffect.BREATHE: ["asusctl", "aura", "breathe"],
                AuraEffect.COLOR_CYCLE: ["asusctl", "aura", "colorcycle"],
                AuraEffect.RAINBOW: ["asusctl", "aura", "rainbow"],
                AuraEffect.STAR: ["asusctl", "aura", "star"],
                AuraEffect.RAIN: ["asusctl", "aura", "rain"],
                AuraEffect.HIGHLIGHT: ["asusctl", "aura", "highlight"],
                AuraEffect.LASER: ["asusctl", "aura", "laser"],
                AuraEffect.RIPPLE: ["asusctl", "aura", "ripple"],
                AuraEffect.STROBE: ["asusctl", "aura", "strobe"],
                AuraEffect.COMET: ["asusctl", "aura", "comet"],
                AuraEffect.FLASH: ["asusctl", "aura", "flash"],
                AuraEffect.MULTI_STATIC: ["asusctl", "aura", "multistatic"],
            }

            if effect not in effect_map:
                return False, f"Unsupported effect: {effect.value}"

            cmd = effect_map[effect]

            # Try direct execution first
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return True, f"Effect set to {effect.value}"
                else:
                    # Fall back to pkexec
                    pass
            except FileNotFoundError:
                # asusctl not found, try pkexec
                pass

            # Try with pkexec
            pkexec_cmd = ["pkexec"] + cmd
            result = subprocess.run(
                pkexec_cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, f"Effect set to {effect.value} (via pkexec)"
            else:
                return False, f"Failed to set effect: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error setting Aura effect: {e}"

    def get_keyboard_info(self) -> Dict[str, Any]:
        """Get comprehensive keyboard info"""
        info: Dict[str, Any] = {
            "supported": self.is_supported(),
            "has_rgb": self.has_rgb(),
            "has_aura": self.has_aura(),
            "has_gz302_rgb": self.has_gz302_rgb(),
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
