#!/usr/bin/env python3
"""
Fan Control Module for Linux Armoury

Provides fan curve and fan speed control for ASUS laptops.
"""

import glob
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class FanProfile(Enum):
    """Fan control profiles"""

    QUIET = "quiet"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    FULL_SPEED = "full_speed"


@dataclass
class FanCurvePoint:
    """A point on the fan curve"""

    temperature: int  # Celsius
    fan_speed: int  # Percentage (0-100)


@dataclass
class FanStatus:
    """Current fan status"""

    rpm: int
    pwm: int
    name: str


class FanController:
    """Controls fan behavior on ASUS laptops"""

    HWMON_PATH = "/sys/class/hwmon"
    PLATFORM_PATH = "/sys/devices/platform/asus-nb-wmi"

    # Default fan curve presets (temperature, speed %)
    CURVE_PRESETS = {
        FanProfile.QUIET: [
            FanCurvePoint(30, 0),
            FanCurvePoint(40, 10),
            FanCurvePoint(50, 25),
            FanCurvePoint(60, 35),
            FanCurvePoint(70, 50),
            FanCurvePoint(80, 65),
            FanCurvePoint(90, 80),
            FanCurvePoint(100, 100),
        ],
        FanProfile.BALANCED: [
            FanCurvePoint(30, 0),
            FanCurvePoint(40, 20),
            FanCurvePoint(50, 35),
            FanCurvePoint(60, 50),
            FanCurvePoint(70, 65),
            FanCurvePoint(80, 80),
            FanCurvePoint(90, 95),
            FanCurvePoint(100, 100),
        ],
        FanProfile.PERFORMANCE: [
            FanCurvePoint(30, 20),
            FanCurvePoint(40, 35),
            FanCurvePoint(50, 50),
            FanCurvePoint(60, 65),
            FanCurvePoint(70, 80),
            FanCurvePoint(80, 90),
            FanCurvePoint(90, 100),
            FanCurvePoint(100, 100),
        ],
        FanProfile.FULL_SPEED: [
            FanCurvePoint(30, 100),
            FanCurvePoint(40, 100),
            FanCurvePoint(50, 100),
            FanCurvePoint(60, 100),
            FanCurvePoint(70, 100),
            FanCurvePoint(80, 100),
            FanCurvePoint(90, 100),
            FanCurvePoint(100, 100),
        ],
    }

    def __init__(self):
        self._hwmon_path: Optional[str] = None
        self._fan_curve_path: Optional[str] = None
        self._fans: List[Dict] = []
        self._detect_hardware()

    def _detect_hardware(self):
        """Detect fan hardware"""
        # Find ASUS hwmon device
        for hwmon in glob.glob(f"{self.HWMON_PATH}/hwmon*"):
            name_path = os.path.join(hwmon, "name")
            if os.path.exists(name_path):
                try:
                    with open(name_path, "r") as f:
                        name = f.read().strip()
                    if name in ["asus", "asus-nb-wmi", "asus_wmi_sensors"]:
                        self._hwmon_path = hwmon
                        break
                except Exception:
                    pass

        # Detect fans
        if self._hwmon_path:
            for i in range(1, 5):  # Check up to 4 fans
                rpm_path = os.path.join(self._hwmon_path, f"fan{i}_input")
                if os.path.exists(rpm_path):
                    label_path = os.path.join(self._hwmon_path, f"fan{i}_label")
                    label = "Fan " + str(i)
                    if os.path.exists(label_path):
                        try:
                            with open(label_path, "r") as f:
                                label = f.read().strip()
                        except Exception:
                            pass
                    self._fans.append(
                        {
                            "id": i,
                            "name": label,
                            "rpm_path": rpm_path,
                        }
                    )

        # Check for fan curve support
        curve_enable_path = os.path.join(self.PLATFORM_PATH, "fan_curve_enable")
        if os.path.exists(curve_enable_path):
            self._fan_curve_path = curve_enable_path

    def is_supported(self) -> bool:
        """Check if fan control is supported"""
        return len(self._fans) > 0

    def has_fan_curves(self) -> bool:
        """Check if custom fan curves are supported"""
        return self._fan_curve_path is not None

    def get_fan_count(self) -> int:
        """Get number of detected fans"""
        return len(self._fans)

    def get_fan_rpm(self, fan_id: int = 1) -> Optional[int]:
        """Get current fan RPM"""
        for fan in self._fans:
            if fan["id"] == fan_id:
                try:
                    with open(fan["rpm_path"], "r") as f:
                        return int(f.read().strip())
                except Exception:
                    return None
        return None

    def get_all_fan_speeds(self) -> List[FanStatus]:
        """Get speed of all detected fans"""
        result = []
        for fan in self._fans:
            try:
                with open(fan["rpm_path"], "r") as f:
                    rpm = int(f.read().strip())
                result.append(
                    FanStatus(rpm=rpm, pwm=0, name=fan["name"])  # Not always available
                )
            except Exception:
                pass
        return result

    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature"""
        # Try various temperature sources
        temp_paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/devices/platform/coretemp.0/hwmon/hwmon*/temp1_input",
        ]

        for pattern in temp_paths:
            for path in glob.glob(pattern):
                try:
                    with open(path, "r") as f:
                        temp = int(f.read().strip())
                    # Convert millidegrees to degrees if needed
                    if temp > 1000:
                        temp = temp // 1000
                    return temp
                except Exception:
                    continue
        return None

    def get_gpu_temperature(self) -> Optional[float]:
        """Get GPU temperature (if available)"""
        # Try NVIDIA
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass

        # Try AMD
        for hwmon in glob.glob(f"{self.HWMON_PATH}/hwmon*"):
            name_path = os.path.join(hwmon, "name")
            if os.path.exists(name_path):
                try:
                    with open(name_path, "r") as f:
                        name = f.read().strip()
                    if "amdgpu" in name:
                        temp_path = os.path.join(hwmon, "temp1_input")
                        if os.path.exists(temp_path):
                            with open(temp_path, "r") as f:
                                temp = int(f.read().strip())
                            return temp / 1000
                except Exception:
                    pass

        return None

    def enable_custom_fan_curve(self, enable: bool = True) -> Tuple[bool, str]:
        """Enable or disable custom fan curve"""
        if not self.has_fan_curves() or not self._fan_curve_path:
            return False, "Custom fan curves not supported"

        value = "1" if enable else "0"
        status_msg = "enabled" if enable else "disabled"
        try:
            with open(self._fan_curve_path, "w") as f:
                f.write(value)
            return True, f"Custom fan curve {status_msg}"
        except PermissionError:
            try:
                cmd = ["pkexec", "tee", self._fan_curve_path]
                result = subprocess.run(
                    cmd, input=value, capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return True, f"Custom fan curve {status_msg}"
                return False, f"Failed: {result.stderr}"
            except Exception as e:
                return False, str(e)
        except Exception as e:
            return False, str(e)

    def get_temperatures(self) -> Dict[str, Optional[float]]:
        """Get all available temperatures"""
        return {
            "cpu": self.get_cpu_temperature(),
            "gpu": self.get_gpu_temperature(),
        }


# Global singleton
_fan_controller: Optional[FanController] = None


def get_fan_controller() -> FanController:
    """Get singleton fan controller instance"""
    global _fan_controller
    if _fan_controller is None:
        _fan_controller = FanController()
    return _fan_controller
