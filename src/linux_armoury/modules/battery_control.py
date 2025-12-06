#!/usr/bin/env python3
"""
Battery Control Module for Linux Armoury

Provides battery charge limit control for ASUS laptops.
"""

import glob
import os
import subprocess
from enum import IntEnum
from typing import List, Optional, Tuple

from ..system_utils import SystemUtils


class ChargeLimitPreset(IntEnum):
    """Common charge limit presets"""

    MAXIMUM = 100
    BALANCED = 80
    LIFESPAN = 60


class BatteryController:
    """Controls battery charging behavior"""

    CHARGE_LIMIT_PATHS = [
        "/sys/class/power_supply/BAT0/charge_control_end_threshold",
        "/sys/class/power_supply/BAT1/charge_control_end_threshold",
        "/sys/class/power_supply/BATT/charge_control_end_threshold",
    ]

    BATTERY_STATUS_PATHS = [
        "/sys/class/power_supply/BAT0/status",
        "/sys/class/power_supply/BAT1/status",
        "/sys/class/power_supply/BATT/status",
    ]

    BATTERY_CAPACITY_PATHS = [
        "/sys/class/power_supply/BAT0/capacity",
        "/sys/class/power_supply/BAT1/capacity",
        "/sys/class/power_supply/BATT/capacity",
    ]

    def __init__(self):
        self._charge_limit_path: Optional[str] = None
        self._battery_path: Optional[str] = None
        self._detect_paths()

    def _detect_paths(self):
        """Detect available battery paths"""
        # Use SystemUtils to find battery path
        battery_path = SystemUtils.find_battery_path()
        if battery_path:
            self._battery_path = battery_path
            self._charge_limit_path = os.path.join(
                battery_path, "charge_control_end_threshold"
            )

            # Verify charge limit path exists
            if not os.path.exists(self._charge_limit_path):
                self._charge_limit_path = None
        else:
            # Fallback to old method just in case
            for path in self.CHARGE_LIMIT_PATHS:
                if os.path.exists(path):
                    self._charge_limit_path = path
                    self._battery_path = os.path.dirname(path)
                    break

    def is_supported(self) -> bool:
        """Check if charge limit control is supported"""
        return self._charge_limit_path is not None

    def get_charge_limit(self) -> Optional[int]:
        """Get current charge limit threshold"""
        if not self._charge_limit_path:
            return None
        try:
            with open(self._charge_limit_path, "r") as f:
                return int(f.read().strip())
        except Exception:
            return None

    def set_charge_limit(self, limit: int) -> Tuple[bool, str]:
        """Set charge limit threshold (requires root)"""
        if not self.is_supported():
            return False, "Charge limit control not supported"

        if not 60 <= limit <= 100:
            return False, "Charge limit must be between 60 and 100"

        try:
            # Try direct write first (if running as root)
            with open(self._charge_limit_path, "w") as f:
                f.write(str(limit))
            return True, f"Charge limit set to {limit}%"
        except PermissionError:
            # Use pkexec for elevated privileges
            try:
                cmd = ["pkexec", "tee", self._charge_limit_path]
                result = subprocess.run(
                    cmd, input=str(limit), capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return True, f"Charge limit set to {limit}%"
                return False, f"Failed to set charge limit: {result.stderr}"
            except subprocess.TimeoutExpired:
                return False, "Command timed out"
            except Exception as e:
                return False, f"Failed to set charge limit: {e}"
        except Exception as e:
            return False, f"Failed to set charge limit: {e}"

    def set_preset(self, preset: ChargeLimitPreset) -> Tuple[bool, str]:
        """Set charge limit to a preset value"""
        return self.set_charge_limit(preset.value)

    def get_battery_status(self) -> Optional[str]:
        """Get battery charging status"""
        if not self._battery_path:
            return None
        try:
            status_path = os.path.join(self._battery_path, "status")
            with open(status_path, "r") as f:
                return f.read().strip()
        except Exception:
            return None

    def get_battery_capacity(self) -> Optional[int]:
        """Get current battery capacity percentage"""
        if not self._battery_path:
            return None
        try:
            capacity_path = os.path.join(self._battery_path, "capacity")
            with open(capacity_path, "r") as f:
                return int(f.read().strip())
        except Exception:
            return None

    def get_battery_info(self) -> dict:
        """Get comprehensive battery information"""
        info = {
            "supported": self.is_supported(),
            "charge_limit": self.get_charge_limit(),
            "status": self.get_battery_status(),
            "capacity": self.get_battery_capacity(),
        }

        # Additional info if battery path available
        if self._battery_path:
            for attr in [
                "energy_full",
                "energy_full_design",
                "voltage_now",
                "current_now",
            ]:
                path = os.path.join(self._battery_path, attr)
                if os.path.exists(path):
                    try:
                        with open(path, "r") as f:
                            info[attr] = int(f.read().strip())
                    except Exception:
                        pass

            # Calculate battery health
            if "energy_full" in info and "energy_full_design" in info:
                if info["energy_full_design"] > 0:
                    info["health"] = round(
                        info["energy_full"] / info["energy_full_design"] * 100, 1
                    )

        return info


# Global singleton
_battery_controller: Optional[BatteryController] = None


def get_battery_controller() -> BatteryController:
    """Get singleton battery controller instance"""
    global _battery_controller
    if _battery_controller is None:
        _battery_controller = BatteryController()
    return _battery_controller
