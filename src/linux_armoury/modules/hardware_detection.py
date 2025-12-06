#!/usr/bin/env python3
"""
Hardware Detection Module for Linux Armoury

Detects ASUS laptop hardware capabilities and available features.
"""

import glob
import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set


class HardwareFeature(Enum):
    """Available hardware features"""

    PLATFORM_PROFILE = auto()
    CHARGE_CONTROL = auto()
    KEYBOARD_BACKLIGHT = auto()
    KEYBOARD_RGB = auto()
    FAN_CURVES = auto()
    GPU_MUX = auto()
    DGPU = auto()
    ANIME_MATRIX = auto()
    PANEL_OVERDRIVE = auto()


@dataclass
class HardwareCapabilities:
    """Detected hardware capabilities"""

    is_asus_laptop: bool = False
    laptop_model: str = ""
    kernel_version: str = ""
    features: Set[HardwareFeature] = field(default_factory=set)
    asusd_available: bool = False
    supergfxctl_available: bool = False
    platform_profiles: List[str] = field(default_factory=list)
    charge_limit_path: str = ""
    kbd_backlight_path: str = ""
    fan_curve_paths: List[str] = field(default_factory=list)
    dgpu_path: str = ""


class HardwareDetector:
    """Detects ASUS hardware and capabilities"""

    SYSFS_PATHS = {
        "asus_wmi": "/sys/devices/platform/asus-nb-wmi",
        "platform_profile": "/sys/firmware/acpi/platform_profile",
        "platform_profile_choices": "/sys/firmware/acpi/platform_profile_choices",
        "charge_control": "/sys/class/power_supply/BAT*/charge_control_end_threshold",
        "kbd_backlight": "/sys/class/leds/*::kbd_backlight",
        "anime_matrix": "/sys/class/leds/asus::anime_matrix",
        "fan_curves": "/sys/devices/platform/asus-nb-wmi/fan_curve_*",
        "dgpu": "/sys/bus/pci/devices/0000:01:00.0",
        "panel_od": "/sys/devices/platform/asus-nb-wmi/panel_od",
    }

    DMI_PATHS = {
        "product_name": "/sys/class/dmi/id/product_name",
        "sys_vendor": "/sys/class/dmi/id/sys_vendor",
        "board_name": "/sys/class/dmi/id/board_name",
    }

    def __init__(self):
        self._capabilities: Optional[HardwareCapabilities] = None

    def detect(self, force: bool = False) -> HardwareCapabilities:
        """Detect hardware capabilities"""
        if self._capabilities is not None and not force:
            return self._capabilities

        caps = HardwareCapabilities()

        # Check if this is an ASUS laptop
        caps.is_asus_laptop = self._is_asus_laptop()
        caps.laptop_model = self._get_laptop_model()
        caps.kernel_version = self._get_kernel_version()

        # Check for asusd/supergfxctl
        caps.asusd_available = self._check_asusd()
        caps.supergfxctl_available = self._check_supergfxctl()

        # Detect features
        if self._path_exists(self.SYSFS_PATHS["platform_profile"]):
            caps.features.add(HardwareFeature.PLATFORM_PROFILE)
            caps.platform_profiles = self._get_platform_profiles()

        charge_paths = glob.glob(self.SYSFS_PATHS["charge_control"])
        if charge_paths:
            caps.features.add(HardwareFeature.CHARGE_CONTROL)
            caps.charge_limit_path = charge_paths[0]

        if self._path_exists(self.SYSFS_PATHS["kbd_backlight"]):
            caps.features.add(HardwareFeature.KEYBOARD_BACKLIGHT)
            # Resolve wildcard path
            paths = glob.glob(self.SYSFS_PATHS["kbd_backlight"])
            if paths:
                caps.kbd_backlight_path = paths[0]

            # Check for RGB support
            if self._has_rgb_keyboard():
                caps.features.add(HardwareFeature.KEYBOARD_RGB)

        fan_paths = glob.glob(self.SYSFS_PATHS["fan_curves"])
        if fan_paths:
            caps.features.add(HardwareFeature.FAN_CURVES)
            caps.fan_curve_paths = fan_paths

        if self._path_exists(self.SYSFS_PATHS["dgpu"]):
            caps.features.add(HardwareFeature.DGPU)
            caps.dgpu_path = self.SYSFS_PATHS["dgpu"]

        if self._path_exists(self.SYSFS_PATHS["anime_matrix"]):
            caps.features.add(HardwareFeature.ANIME_MATRIX)

        if self._path_exists(self.SYSFS_PATHS["panel_od"]):
            caps.features.add(HardwareFeature.PANEL_OVERDRIVE)

        # Check GPU MUX
        if caps.asusd_available or self._has_gpu_mux():
            caps.features.add(HardwareFeature.GPU_MUX)

        self._capabilities = caps
        return caps

    def _path_exists(self, path: str) -> bool:
        """Check if a sysfs path exists"""
        if "*" in path:
            return bool(glob.glob(path))
        return os.path.exists(path)

    def _read_file(self, path: str) -> str:
        """Read content from a file"""
        try:
            with open(path, "r") as f:
                return f.read().strip()
        except Exception:
            return ""

    def _is_asus_laptop(self) -> bool:
        """Check if this is an ASUS laptop"""
        vendor = self._read_file(self.DMI_PATHS["sys_vendor"]).lower()
        return "asus" in vendor

    def _get_laptop_model(self) -> str:
        """Get laptop model name"""
        product = self._read_file(self.DMI_PATHS["product_name"])
        board = self._read_file(self.DMI_PATHS["board_name"])
        return product or board

    def _get_kernel_version(self) -> str:
        """Get kernel version"""
        try:
            result = subprocess.run(
                ["uname", "-r"], capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _get_platform_profiles(self) -> List[str]:
        """Get available platform profiles"""
        choices = self._read_file(self.SYSFS_PATHS["platform_profile_choices"])
        if choices:
            return choices.split()
        return []

    def _check_asusd(self) -> bool:
        """Check if asusd is available"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "asusd"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False

    def _check_supergfxctl(self) -> bool:
        """Check if supergfxctl is available"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "supergfxd"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False

    def _has_rgb_keyboard(self) -> bool:
        """Check if keyboard has RGB support"""
        # Check for aura devices
        aura_paths = glob.glob(
            "/sys/class/leds/asus::kbd_backlight/device/leds/*/brightness"
        )
        if aura_paths:
            return True
        # Check for multi_intensity support
        mi_path = "/sys/class/leds/asus::kbd_backlight/multi_intensity"
        return os.path.exists(mi_path)

    def _has_gpu_mux(self) -> bool:
        """Check if GPU MUX is available"""
        mux_path = "/sys/devices/platform/asus-nb-wmi/dgpu_disable"
        return os.path.exists(mux_path)

    def get_feature_status(self) -> Dict[str, bool]:
        """Get status of all features"""
        caps = self.detect()
        return {
            "Platform Profile": HardwareFeature.PLATFORM_PROFILE in caps.features,
            "Battery Charge Control": HardwareFeature.CHARGE_CONTROL in caps.features,
            "Keyboard Backlight": HardwareFeature.KEYBOARD_BACKLIGHT in caps.features,
            "Keyboard RGB": HardwareFeature.KEYBOARD_RGB in caps.features,
            "Fan Curves": HardwareFeature.FAN_CURVES in caps.features,
            "GPU Switching": HardwareFeature.GPU_MUX in caps.features,
            "Discrete GPU": HardwareFeature.DGPU in caps.features,
            "Anime Matrix": HardwareFeature.ANIME_MATRIX in caps.features,
            "Panel Overdrive": HardwareFeature.PANEL_OVERDRIVE in caps.features,
            "asusd Available": caps.asusd_available,
            "supergfxctl Available": caps.supergfxctl_available,
        }


# Global singleton
_detector: Optional[HardwareDetector] = None


def get_hardware_detector() -> HardwareDetector:
    """Get singleton hardware detector instance"""
    global _detector
    if _detector is None:
        _detector = HardwareDetector()
    return _detector


def detect_hardware() -> HardwareCapabilities:
    """Convenience function to detect hardware"""
    return get_hardware_detector().detect()
