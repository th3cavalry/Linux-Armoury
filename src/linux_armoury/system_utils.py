#!/usr/bin/env python3
"""
System utilities for hardware detection and monitoring
"""

import os
import re
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple


class DisplayBackend:
    """Enum-like class for display backend types"""

    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class SystemUtils:
    """System utility functions for hardware detection and monitoring"""

    @staticmethod
    def get_display_backend() -> str:
        """
        Detect if running under X11 or Wayland.

        Returns:
            str: 'x11', 'wayland', or 'unknown'
        """
        # Check XDG_SESSION_TYPE first (most reliable)
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type == "wayland":
            return DisplayBackend.WAYLAND
        if session_type == "x11":
            return DisplayBackend.X11

        # Check for Wayland display
        if os.environ.get("WAYLAND_DISPLAY"):
            return DisplayBackend.WAYLAND

        # Check for X11 display
        if os.environ.get("DISPLAY"):
            return DisplayBackend.X11

        return DisplayBackend.UNKNOWN

    @staticmethod
    def get_wayland_tool() -> Optional[str]:
        """
        Detect available Wayland display configuration tool.

        Returns:
            Optional[str]: Name of available tool or None
        """
        # Priority order of Wayland tools
        wayland_tools = [
            "wlr-randr",  # wlroots compositors (Sway, etc.)
            "gnome-randr",  # GNOME-specific (if available)
            "kscreen-doctor",  # KDE Plasma
        ]

        for tool in wayland_tools:
            if SystemUtils.check_command_exists(tool):
                return tool

        return None

    @staticmethod
    def get_primary_display() -> str:
        """
        Auto-detect the primary display output name.
        Works with both X11 and Wayland.

        Returns:
            str: Display output name (e.g., 'eDP-1', 'eDP-2')
        """
        backend = SystemUtils.get_display_backend()

        if backend == DisplayBackend.WAYLAND:
            return SystemUtils._get_primary_display_wayland()
        else:
            return SystemUtils._get_primary_display_x11()

    @staticmethod
    def _get_primary_display_x11() -> str:
        """Get primary display for X11"""
        try:
            result = subprocess.run(
                ["xrandr", "--query"], capture_output=True, text=True, timeout=5
            )

            # Look for connected displays
            for line in result.stdout.split("\n"):
                # First try to find primary display
                if " connected primary" in line:
                    return line.split()[0]

            # If no primary, find first connected display
            for line in result.stdout.split("\n"):
                if " connected" in line and "disconnected" not in line:
                    return line.split()[0]

        except Exception as e:
            print(f"Error detecting X11 display: {e}")

        # Fallback to common default
        return "eDP-1"

    @staticmethod
    def _get_primary_display_wayland() -> str:
        """Get primary display for Wayland"""
        tool = SystemUtils.get_wayland_tool()

        if tool == "wlr-randr":
            try:
                result = subprocess.run(
                    ["wlr-randr"], capture_output=True, text=True, timeout=5
                )
                # Parse wlr-randr output - first output is usually the display name
                for line in result.stdout.split("\n"):
                    if line and not line.startswith(" "):
                        # Output name is the first word
                        return line.split()[0]
            except Exception as e:
                print(f"Error detecting Wayland display with wlr-randr: {e}")

        elif tool == "kscreen-doctor":
            try:
                result = subprocess.run(
                    ["kscreen-doctor", "-o"], capture_output=True, text=True, timeout=5
                )
                # Parse kscreen-doctor output
                for line in result.stdout.split("\n"):
                    if "Output" in line:
                        match = re.search(r"Output:\s+(\d+)\s+(\S+)", line)
                        if match:
                            return match.group(2)
            except Exception as e:
                print(f"Error detecting Wayland display with kscreen-doctor: {e}")

        # Fallback - try to detect from GNOME settings
        try:
            result = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    "text-scaling-factor",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )
            # If gsettings works, we're probably on GNOME
            # GNOME Wayland uses display IDs like 'eDP-1'
            return "eDP-1"
        except Exception:
            pass

        return "eDP-1"

    @staticmethod
    def get_display_resolution() -> Tuple[int, int]:
        """
        Get current display resolution. Works with both X11 and Wayland.

        Returns:
            Tuple[int, int]: (width, height)
        """
        backend = SystemUtils.get_display_backend()

        if backend == DisplayBackend.WAYLAND:
            return SystemUtils._get_display_resolution_wayland()
        else:
            return SystemUtils._get_display_resolution_x11()

    @staticmethod
    def _get_display_resolution_x11() -> Tuple[int, int]:
        """Get display resolution for X11"""
        try:
            result = subprocess.run(
                ["xrandr", "--query"], capture_output=True, text=True, timeout=5
            )

            for line in result.stdout.split("\n"):
                if "*" in line:  # Current resolution marked with *
                    match = re.search(r"(\d+)x(\d+)", line)
                    if match:
                        return (int(match.group(1)), int(match.group(2)))

        except Exception as e:
            print(f"Error getting X11 resolution: {e}")

        return (1920, 1080)  # Fallback default resolution

    @staticmethod
    def _get_display_resolution_wayland() -> Tuple[int, int]:
        """Get display resolution for Wayland"""
        tool = SystemUtils.get_wayland_tool()

        if tool == "wlr-randr":
            try:
                result = subprocess.run(
                    ["wlr-randr"], capture_output=True, text=True, timeout=5
                )
                # Parse resolution from wlr-randr output
                # Format: "  2560x1600 px, 60.000000 Hz (current)"
                for line in result.stdout.split("\n"):
                    if "current" in line.lower():
                        match = re.search(r"(\d+)x(\d+)", line)
                        if match:
                            return (int(match.group(1)), int(match.group(2)))
            except Exception as e:
                print(f"Error getting Wayland resolution with wlr-randr: {e}")

        elif tool == "kscreen-doctor":
            try:
                result = subprocess.run(
                    ["kscreen-doctor", "-o"], capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split("\n"):
                    match = re.search(r"(\d+)x(\d+)@", line)
                    if match:
                        return (int(match.group(1)), int(match.group(2)))
            except Exception as e:
                print(f"Error getting Wayland resolution with kscreen-doctor: {e}")

        return (1920, 1080)  # Fallback default resolution

    @staticmethod
    def get_current_refresh_rate() -> Optional[int]:
        """
        Get current display refresh rate. Works with both X11 and Wayland.

        Returns:
            Optional[int]: Refresh rate in Hz
        """
        backend = SystemUtils.get_display_backend()

        if backend == DisplayBackend.WAYLAND:
            return SystemUtils._get_current_refresh_rate_wayland()
        else:
            return SystemUtils._get_current_refresh_rate_x11()

    @staticmethod
    def get_supported_refresh_rates() -> List[int]:
        """
        Get list of supported refresh rates for the primary display.

        Returns:
            List[int]: List of refresh rates in Hz (e.g. [60, 120, 144])
        """
        backend = SystemUtils.get_display_backend()

        if backend == DisplayBackend.WAYLAND:
            return SystemUtils._get_supported_refresh_rates_wayland()
        else:
            return SystemUtils._get_supported_refresh_rates_x11()

    @staticmethod
    def _get_supported_refresh_rates_x11() -> List[int]:
        rates = set()
        try:
            # Get current resolution first
            width, height = SystemUtils._get_display_resolution_x11()
            res_str = f"{width}x{height}"

            result = subprocess.run(
                ["xrandr", "--query"], capture_output=True, text=True, timeout=5
            )

            # Parse output
            # 1920x1080     60.00*+  120.00  144.00
            for line in result.stdout.split("\n"):
                if res_str in line:
                    # Extract all numbers that look like rates
                    # Skip the resolution part
                    parts = line.split()
                    if parts[0] == res_str:
                        for part in parts[1:]:
                            # Remove * and +
                            clean_part = part.replace("*", "").replace("+", "")
                            try:
                                rate = float(clean_part)
                                rates.add(int(round(rate)))
                            except ValueError:
                                pass
        except Exception as e:
            print(f"Error getting X11 rates: {e}")

        return sorted(list(rates))

    @staticmethod
    def _get_supported_refresh_rates_wayland() -> List[int]:
        rates = set()
        tool = SystemUtils.get_wayland_tool()

        if tool == "wlr-randr":
            try:
                result = subprocess.run(["wlr-randr"], capture_output=True, text=True)
                # Output format needs parsing. Usually lists modes.
                # 1920x1080 px, 144.000000 Hz
                # 1920x1080 px, 60.000000 Hz

                # Let's get current resolution first
                width, height = SystemUtils._get_display_resolution_wayland()
                res_str = f"{width}x{height}"

                for line in result.stdout.split("\n"):
                    if res_str in line and "Hz" in line:
                        match = re.search(r"(\d+\.?\d*)\s*Hz", line)
                        if match:
                            rates.add(int(round(float(match.group(1)))))
            except Exception:
                pass

        elif tool == "kscreen-doctor":
            # kscreen-doctor -o output
            # Mode: 1920x1080@144 ...
            # Mode: 1920x1080@60 ...
            try:
                width, height = SystemUtils._get_display_resolution_wayland()
                res_str = f"{width}x{height}"

                result = subprocess.run(
                    ["kscreen-doctor", "-o"], capture_output=True, text=True
                )
                for line in result.stdout.split("\n"):
                    if "Mode:" in line and res_str in line:
                        match = re.search(r"@(\d+)", line)
                        if match:
                            rates.add(int(match.group(1)))
            except Exception:
                pass

        return sorted(list(rates))

    @staticmethod
    def _get_current_refresh_rate_x11() -> Optional[int]:
        """Get refresh rate for X11"""
        try:
            result = subprocess.run(
                ["xrandr", "--query"], capture_output=True, text=True, timeout=5
            )

            for line in result.stdout.split("\n"):
                if "*" in line:  # Current mode
                    match = re.search(r"(\d+\.\d+)\*", line)
                    if match:
                        return int(float(match.group(1)))

        except Exception as e:
            print(f"Error getting refresh rate: {e}")

        return None

    @staticmethod
    def _get_current_refresh_rate_wayland() -> Optional[int]:
        """Get refresh rate for Wayland"""
        tool = SystemUtils.get_wayland_tool()

        if tool == "wlr-randr":
            try:
                result = subprocess.run(
                    ["wlr-randr"], capture_output=True, text=True, timeout=5
                )
                # Parse refresh rate from wlr-randr output
                # Format: "  2560x1600 px, 60.000000 Hz (current)"
                for line in result.stdout.split("\n"):
                    if "current" in line.lower():
                        match = re.search(r"(\d+\.?\d*)\s*Hz", line)
                        if match:
                            return int(float(match.group(1)))
            except Exception as e:
                print(f"Error getting Wayland refresh rate with wlr-randr: {e}")

        elif tool == "kscreen-doctor":
            try:
                result = subprocess.run(
                    ["kscreen-doctor", "-o"], capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split("\n"):
                    match = re.search(r"@(\d+)", line)
                    if match:
                        return int(match.group(1))
            except Exception as e:
                print(f"Error getting Wayland refresh rate with kscreen-doctor: {e}")

        return None

    @staticmethod
    def set_refresh_rate(rate: int) -> Tuple[bool, str]:
        """
        Set display refresh rate. Works with both X11 and Wayland.

        Args:
            rate: Refresh rate in Hz

        Returns:
            Tuple[bool, str]: (success, message)
        """
        backend = SystemUtils.get_display_backend()

        if backend == DisplayBackend.WAYLAND:
            return SystemUtils._set_refresh_rate_wayland(rate)
        else:
            return SystemUtils._set_refresh_rate_x11(rate)

    @staticmethod
    def _set_refresh_rate_x11(rate: int) -> Tuple[bool, str]:
        """Set refresh rate for X11"""
        display = SystemUtils._get_primary_display_x11()
        width, height = SystemUtils._get_display_resolution_x11()

        # Sanitize display name
        if not all(c.isalnum() or c in "-_" for c in display):
            return (False, f"Invalid display name: {display}")

        mode = f"{width}x{height}"
        try:
            result = subprocess.run(
                ["xrandr", "--output", display, "--mode", mode, "--rate", str(rate)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return (True, f"Refresh rate set to {rate} Hz")
            else:
                return (False, f"Failed to set refresh rate: {result.stderr}")
        except Exception as e:
            return (False, f"Error: {str(e)}")

    @staticmethod
    def _set_refresh_rate_wayland(rate: int) -> Tuple[bool, str]:
        """Set refresh rate for Wayland"""
        tool = SystemUtils.get_wayland_tool()

        if not tool:
            return (
                False,
                "No Wayland display configuration tool found. "
                "Install wlr-randr or use GNOME Settings.",
            )

        display = SystemUtils._get_primary_display_wayland()
        width, height = SystemUtils._get_display_resolution_wayland()

        if tool == "wlr-randr":
            try:
                # wlr-randr --output eDP-1 --mode 2560x1600@90
                mode = f"{width}x{height}@{rate}"
                result = subprocess.run(
                    ["wlr-randr", "--output", display, "--mode", mode],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    return (True, f"Refresh rate set to {rate} Hz (Wayland)")
                else:
                    return (False, f"Failed to set refresh rate: {result.stderr}")
            except Exception as e:
                return (False, f"Error: {str(e)}")

        elif tool == "kscreen-doctor":
            try:
                # kscreen-doctor output.eDP-1.mode.2560x1600@90
                mode_arg = f"output.{display}.mode.{width}x{height}@{rate}"
                result = subprocess.run(
                    ["kscreen-doctor", mode_arg],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    return (True, f"Refresh rate set to {rate} Hz (Wayland/KDE)")
                else:
                    return (False, f"Failed to set refresh rate: {result.stderr}")
            except Exception as e:
                return (False, f"Error: {str(e)}")

        return (False, "No supported Wayland tool available")

    @staticmethod
    def get_cpu_temperature() -> Optional[float]:
        """
        Get CPU temperature from hwmon.

        Returns:
            Optional[float]: Temperature in Celsius
        """
        try:
            # Try different hwmon paths
            hwmon_paths = [
                "/sys/class/hwmon/hwmon0/temp1_input",
                "/sys/class/hwmon/hwmon1/temp1_input",
                "/sys/class/hwmon/hwmon2/temp1_input",
                "/sys/class/hwmon/hwmon3/temp1_input",
            ]

            for path in hwmon_paths:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        # Temperature in millidegrees
                        temp = int(f.read().strip()) / 1000.0
                        if 0 < temp < 150:  # Sanity check
                            return temp

            # Try sensors command if available
            result = subprocess.run(
                ["sensors", "-A"], capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "Tctl" in line or "CPU" in line:
                        match = re.search(r"(\d+\.\d+)°C", line)
                        if match:
                            return float(match.group(1))

        except Exception as e:
            print(f"Error reading temperature: {e}")

        return None

    @staticmethod
    def get_gpu_temperature() -> Optional[float]:
        """
        Get GPU temperature.

        Returns:
            Optional[float]: Temperature in Celsius
        """
        try:
            # For AMD integrated graphics
            result = subprocess.run(
                ["sensors"], capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "edge" in line.lower() or "gpu" in line.lower():
                        match = re.search(r"(\d+\.\d+)°C", line)
                        if match:
                            return float(match.group(1))

        except Exception as e:
            print(f"Error reading GPU temperature: {e}")

        return None

    @staticmethod
    def is_on_ac_power() -> bool:
        """
        Check if system is running on AC power.

        Returns:
            bool: True if on AC power, False if on battery
        """
        try:
            # Check via /sys/class/power_supply
            ac_online_path = "/sys/class/power_supply/AC/online"
            if os.path.exists(ac_online_path):
                with open(ac_online_path, "r") as f:
                    return f.read().strip() == "1"

            # Alternative paths
            for power_supply in os.listdir("/sys/class/power_supply"):
                path = f"/sys/class/power_supply/{power_supply}/online"
                if os.path.exists(path) and "AC" in power_supply:
                    with open(path, "r") as f:
                        return f.read().strip() == "1"

        except Exception as e:
            print(f"Error checking AC power: {e}")

        return True  # Assume AC as safe default

    @staticmethod
    def get_battery_percentage() -> Optional[int]:
        """
        Get battery charge percentage.

        Returns:
            Optional[int]: Battery percentage (0-100)
        """
        try:
            for power_supply in os.listdir("/sys/class/power_supply"):
                if "BAT" in power_supply:
                    capacity_path = f"/sys/class/power_supply/{power_supply}/capacity"
                    if os.path.exists(capacity_path):
                        with open(capacity_path, "r") as f:
                            return int(f.read().strip())

        except Exception as e:
            print(f"Error reading battery: {e}")

        return None

    @staticmethod
    def check_command_exists(command: str) -> bool:
        return shutil.which(command) is not None

    @staticmethod
    def get_current_power_profile() -> Optional[str]:
        """
        Get the current power/performance profile.
        Supports pwrcfg, asusctl, power-profiles-daemon, and sysfs.
        """
        # 1. pwrcfg (Legacy/GZ302)
        if SystemUtils.check_command_exists("pwrcfg"):
            # pwrcfg status parsing is complex, skip for now or implement if needed
            pass

        # 2. asusctl
        if SystemUtils.check_command_exists("asusctl"):
            try:
                result = subprocess.run(
                    ["asusctl", "profile", "-p"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    # "Active profile: Balanced"
                    output = result.stdout.strip()
                    if "Active profile:" in output:
                        return output.split(":")[-1].strip()
            except Exception:
                pass

        # 3. power-profiles-daemon
        if SystemUtils.check_command_exists("powerprofilesctl"):
            try:
                result = subprocess.run(
                    ["powerprofilesctl", "get"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass

        # 4. Sysfs
        platform_profile_path = "/sys/firmware/acpi/platform_profile"
        try:
            if os.path.exists(platform_profile_path):
                with open(platform_profile_path, "r") as f:
                    return f.read().strip()
        except Exception:
            pass

        return None

    @staticmethod
    def get_available_power_profiles() -> List[str]:
        """
        Get list of available power profiles.
        """
        # 1. pwrcfg
        if SystemUtils.check_command_exists("pwrcfg"):
            return [
                "emergency",
                "battery",
                "efficient",
                "balanced",
                "performance",
                "gaming",
                "maximum",
            ]

        # 2. asusctl
        if SystemUtils.check_command_exists("asusctl"):
            return ["Quiet", "Balanced", "Performance"]

        # 3. power-profiles-daemon
        if SystemUtils.check_command_exists("powerprofilesctl"):
            return ["power-saver", "balanced", "performance"]

        # 4. Sysfs
        choices_path = "/sys/firmware/acpi/platform_profile_choices"
        try:
            if os.path.exists(choices_path):
                with open(choices_path, "r") as f:
                    return f.read().strip().split()
        except Exception:
            pass

        return ["balanced"]

    @staticmethod
    def set_power_profile(profile: str) -> Tuple[bool, str]:
        """
        Set the power/performance profile.
        """
        # 1. pwrcfg
        if SystemUtils.check_command_exists("pwrcfg"):
            try:
                subprocess.run(["pkexec", "pwrcfg", profile], check=True)
                return True, f"Set profile to {profile}"
            except subprocess.CalledProcessError as e:
                return False, f"pwrcfg failed: {e}"

        # 2. asusctl
        if SystemUtils.check_command_exists("asusctl"):
            target = profile
            # Map generic names
            p_lower = profile.lower()
            if p_lower in ["silent", "battery", "power-saver", "low-power"]:
                target = "Quiet"
            elif p_lower in ["balanced"]:
                target = "Balanced"
            elif p_lower in ["performance", "gaming", "turbo", "maximum"]:
                target = "Performance"

            try:
                subprocess.run(["asusctl", "profile", "-P", target], check=True)
                return True, f"Set profile to {target}"
            except subprocess.CalledProcessError as e:
                return False, f"asusctl failed: {e}"

        # 3. power-profiles-daemon
        if SystemUtils.check_command_exists("powerprofilesctl"):
            target = profile
            p_lower = profile.lower()
            if p_lower in ["silent", "quiet", "battery", "low-power"]:
                target = "power-saver"
            elif p_lower in ["balanced"]:
                target = "balanced"
            elif p_lower in ["performance", "gaming", "turbo", "maximum"]:
                target = "performance"

            try:
                subprocess.run(["powerprofilesctl", "set", target], check=True)
                return True, f"Set profile to {target}"
            except subprocess.CalledProcessError as e:
                return False, f"powerprofilesctl failed: {e}"

        # 4. Sysfs (requires root)
        platform_profile_path = "/sys/firmware/acpi/platform_profile"
        try:
            with open(platform_profile_path, "w") as f:
                f.write(profile)
            return True, f"Set profile to {profile}"
        except PermissionError:
            return False, "Permission denied (need root)"
        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def get_current_tdp() -> Optional[int]:
        """
        Get current TDP limit (requires ryzenadj or similar).

        Returns:
            Optional[int]: TDP in Watts
        """
        try:
            # Try ryzenadj if available
            result = subprocess.run(
                ["ryzenadj", "-i"], capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "STAPM LIMIT" in line:
                        match = re.search(r"(\d+)", line)
                        if match:
                            return int(match.group(1))

        except Exception:
            pass

        return None

    @staticmethod
    def find_battery_path() -> Optional[str]:
        """Find the primary battery path in /sys/class/power_supply"""
        base_path = "/sys/class/power_supply"
        if not os.path.exists(base_path):
            return None

        # Try common names first
        for name in ["BAT0", "BAT1", "BATT"]:
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                return path

        # Search for any BAT*
        for item in os.listdir(base_path):
            if item.startswith("BAT"):
                return os.path.join(base_path, item)

        return None

    @staticmethod
    def find_hwmon_path(name_pattern: str) -> Optional[str]:
        """Find a hwmon path by matching its name file"""
        base_path = "/sys/class/hwmon"
        if not os.path.exists(base_path):
            return None

        for item in os.listdir(base_path):
            path = os.path.join(base_path, item)
            name_file = os.path.join(path, "name")
            if os.path.exists(name_file):
                try:
                    with open(name_file, "r") as f:
                        name = f.read().strip()
                        if name_pattern in name:
                            return path
                except Exception:
                    continue
        return None

    @staticmethod
    def find_ac_path() -> Optional[str]:
        """Find the AC power supply path"""
        base_path = "/sys/class/power_supply"
        if not os.path.exists(base_path):
            return None

        # Common names
        for name in ["AC", "AC0", "ADP0", "ADP1", "ACAD"]:
            path = os.path.join(base_path, name)
            if os.path.exists(path):
                return path

        # Search for type=Mains
        for item in os.listdir(base_path):
            path = os.path.join(base_path, item)
            type_file = os.path.join(path, "type")
            if os.path.exists(type_file):
                try:
                    with open(type_file, "r") as f:
                        if f.read().strip() == "Mains":
                            return path
                except Exception:
                    continue
        return None

    @staticmethod
    def get_running_processes() -> List[str]:
        """
        Get list of running process names.

        Returns:
            List[str]: Process names
        """
        try:
            result = subprocess.run(
                ["ps", "-eo", "comm"], capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                processes = result.stdout.split("\n")[1:]  # Skip header
                return [p.strip() for p in processes if p.strip()]

        except Exception as e:
            print(f"Error getting processes: {e}")

        return []

    @staticmethod
    def detect_gaming_apps() -> bool:
        """
        Detect if any gaming applications are running.

        Returns:
            bool: True if gaming app detected
        """
        gaming_apps = [
            "steam",
            "lutris",
            "heroic",
            "bottles",
            "wine",
            "proton",
            "gamemoded",
            "gamemode",
            "minecraft",
            "dotnet",
        ]

        processes = SystemUtils.get_running_processes()
        process_lower = [p.lower() for p in processes]

        for game_app in gaming_apps:
            if any(game_app in p for p in process_lower):
                return True

        return False

    @staticmethod
    def detect_laptop_model() -> Optional[Dict[str, str]]:
        """
        Detect laptop model information.

        Returns:
            Optional[Dict[str, str]]: Model info (vendor, product, version)
        """
        model_info = {}

        try:
            # Read DMI information
            dmi_paths = {
                "vendor": "/sys/class/dmi/id/sys_vendor",
                "product": "/sys/class/dmi/id/product_name",
                "version": "/sys/class/dmi/id/product_version",
                "board": "/sys/class/dmi/id/board_name",
            }

            for key, path in dmi_paths.items():
                if os.path.exists(path):
                    with open(path, "r") as f:
                        model_info[key] = f.read().strip()

            return model_info if model_info else None

        except Exception as e:
            print(f"Error detecting laptop model: {e}")

        return None

    @staticmethod
    def is_asus_laptop() -> bool:
        """
        Check if the system is an ASUS laptop.

        Returns:
            bool: True if ASUS laptop detected
        """
        model_info = SystemUtils.detect_laptop_model()
        if model_info and "vendor" in model_info:
            vendor = model_info["vendor"].lower()
            return "asus" in vendor or "asustek" in vendor
        return False

    @staticmethod
    def get_supported_models() -> List[str]:
        """
        Get list of supported ASUS laptop models.

        Returns:
            List[str]: List of supported model identifiers
        """
        # Return supported model families / example model identifiers
        return [
            "ROG_FLOW_Z13",
            "ROG_ZEPHYRUS",
            "ROG_STRIX",
            "ASUS_TUF",
            "OTHER_ASUS_GAMING",
        ]

    @staticmethod
    def get_cpu_info() -> Dict[str, str]:
        """
        Get detailed CPU information.

        Returns:
            Dict[str, str]: CPU information including model, cores, frequency
        """
        info = {
            "model": "Unknown",
            "cores": "0",
            "threads": "0",
            "max_freq": "0 MHz",
            "architecture": "Unknown",
        }

        try:
            # Get CPU model from /proc/cpuinfo
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()

            # Extract model name
            model_match = re.search(r"model name\s*:\s*(.+)", cpuinfo)
            if model_match:
                info["model"] = model_match.group(1).strip()

            # Count physical cores and threads
            cores = set()
            threads = 0
            for line in cpuinfo.split("\n"):
                if line.startswith("core id"):
                    cores.add(line.split(":")[1].strip())
                if line.startswith("processor"):
                    threads += 1

            info["cores"] = str(len(cores)) if cores else str(threads)
            info["threads"] = str(threads)

            # Get architecture
            result = subprocess.run(["uname", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                info["architecture"] = result.stdout.strip()

            # Get max frequency
            freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
            if os.path.exists(freq_path):
                with open(freq_path, "r") as f:
                    freq_khz = int(f.read().strip())
                    info["max_freq"] = f"{freq_khz / 1000000:.2f} GHz"

        except Exception as e:
            print(f"Error getting CPU info: {e}")

        return info

    @staticmethod
    def get_gpu_info() -> List[Dict[str, str]]:
        """
        Get GPU information for all graphics devices.

        Returns:
            List[Dict[str, str]]: List of GPU information dictionaries
        """
        gpus = []

        try:
            # Use lspci to detect GPUs
            result = subprocess.run(["lspci", "-nn"], capture_output=True, text=True)

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "VGA" in line or "3D" in line or "Display" in line:
                        gpu_info = {
                            "name": "Unknown GPU",
                            "type": "Unknown",
                            "pci_id": "",
                        }

                        # Extract GPU name
                        match = re.search(r":\s*(.+)\s*\[", line)
                        if match:
                            gpu_info["name"] = match.group(1).strip()
                        else:
                            # Try alternative pattern
                            parts = line.split(":")
                            if len(parts) >= 3:
                                gpu_info["name"] = parts[2].strip()

                        # Determine GPU type
                        name_lower = gpu_info["name"].lower()
                        if "nvidia" in name_lower:
                            gpu_info["type"] = "NVIDIA (Discrete)"
                        elif "amd" in name_lower or "radeon" in name_lower:
                            if (
                                "vega" in name_lower
                                or "integrated" in name_lower
                                or "apu" in name_lower
                            ):
                                gpu_info["type"] = "AMD (Integrated)"
                            else:
                                gpu_info["type"] = "AMD (Discrete)"
                        elif "intel" in name_lower:
                            gpu_info["type"] = "Intel (Integrated)"

                        # Extract PCI ID
                        pci_match = re.search(
                            r"\[([0-9a-f]{4}:[0-9a-f]{4})\]", line, re.I
                        )
                        if pci_match:
                            gpu_info["pci_id"] = pci_match.group(1)

                        gpus.append(gpu_info)

        except Exception as e:
            print(f"Error getting GPU info: {e}")

        return gpus if gpus else [{"name": "Unknown", "type": "Unknown", "pci_id": ""}]

    @staticmethod
    def get_memory_info() -> Dict[str, str]:
        """
        Get RAM information.

        Returns:
            Dict[str, str]: Memory information
        """
        info = {
            "total": "0 GB",
            "used": "0 GB",
            "available": "0 GB",
            "percent_used": "0%",
        }

        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = f.read()

            total_match = re.search(r"MemTotal:\s*(\d+)", meminfo)
            available_match = re.search(r"MemAvailable:\s*(\d+)", meminfo)

            if total_match:
                total_kb = int(total_match.group(1))
                total_gb = total_kb / (1024 * 1024)
                info["total"] = f"{total_gb:.1f} GB"

                if available_match:
                    available_kb = int(available_match.group(1))
                    available_gb = available_kb / (1024 * 1024)
                    used_gb = total_gb - available_gb
                    percent = (used_gb / total_gb) * 100

                    info["available"] = f"{available_gb:.1f} GB"
                    info["used"] = f"{used_gb:.1f} GB"
                    info["percent_used"] = f"{percent:.0f}%"

        except Exception as e:
            print(f"Error getting memory info: {e}")

        return info

    @staticmethod
    def get_storage_info() -> List[Dict[str, str]]:
        """
        Get storage device information.

        Returns:
            List[Dict[str, str]]: List of storage devices with usage info
        """
        devices = []

        try:
            result = subprocess.run(
                ["df", "-h", "--output=source,size,used,avail,pcent,target"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        source = parts[0]
                        # Only include real filesystems
                        if source.startswith("/dev/") and "loop" not in source:
                            devices.append(
                                {
                                    "device": source,
                                    "size": parts[1],
                                    "used": parts[2],
                                    "available": parts[3],
                                    "percent_used": parts[4],
                                    "mount_point": parts[5],
                                }
                            )

        except Exception as e:
            print(f"Error getting storage info: {e}")

        return devices

    @staticmethod
    def get_os_info() -> Dict[str, str]:
        """
        Get operating system information.

        Returns:
            Dict[str, str]: OS information
        """
        info = {
            "name": "Unknown",
            "version": "Unknown",
            "kernel": "Unknown",
            "desktop": "Unknown",
            "uptime": "Unknown",
        }

        try:
            # Get OS name and version from os-release
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info["name"] = line.split("=")[1].strip().strip('"')
                        elif line.startswith("VERSION="):
                            info["version"] = line.split("=")[1].strip().strip('"')

            # Get kernel version
            result = subprocess.run(["uname", "-r"], capture_output=True, text=True)
            if result.returncode == 0:
                info["kernel"] = result.stdout.strip()

            # Get desktop environment
            desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
            if desktop:
                info["desktop"] = desktop
            else:
                # Try to detect from session
                session = os.environ.get("DESKTOP_SESSION", "")
                if session:
                    info["desktop"] = session.capitalize()

            # Get uptime
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)

                if days > 0:
                    info["uptime"] = f"{days}d {hours}h {minutes}m"
                elif hours > 0:
                    info["uptime"] = f"{hours}h {minutes}m"
                else:
                    info["uptime"] = f"{minutes}m"

        except Exception as e:
            print(f"Error getting OS info: {e}")

        return info

    @staticmethod
    def get_panel_overdrive_status() -> Optional[bool]:
        """
        Get current panel overdrive status.

        Returns:
            Optional[bool]: True if enabled, False if disabled, None if not supported
        """
        # Check asusd panel_od
        try:
            result = subprocess.run(
                ["asusctl", "panel-od", "-g"], capture_output=True, text=True
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                return "on" in output or "true" in output or "enabled" in output
        except FileNotFoundError:
            pass

        # Check sysfs
        od_path = "/sys/class/drm/card0/device/panel_overdrive"
        if os.path.exists(od_path):
            try:
                with open(od_path, "r") as f:
                    return f.read().strip() == "1"
            except Exception:
                pass

        return None

    @staticmethod
    def set_panel_overdrive(enabled: bool) -> Tuple[bool, str]:
        """
        Enable or disable panel overdrive.

        Args:
            enabled: True to enable, False to disable

        Returns:
            Tuple[bool, str]: Success status and message
        """
        # Try asusctl first
        try:
            state = "on" if enabled else "off"
            result = subprocess.run(
                ["asusctl", "panel-od", state], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True, f"Panel overdrive {'enabled' if enabled else 'disabled'}"
        except FileNotFoundError:
            pass

        return False, "Panel overdrive control not available"

    @staticmethod
    def get_boot_sound_status() -> Optional[bool]:
        """
        Get POST sound status.

        Returns:
            Optional[bool]: True if enabled, False if disabled, None if not supported
        """
        try:
            result = subprocess.run(
                ["asusctl", "bios", "post-sound", "-g"], capture_output=True, text=True
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                return "on" in output or "true" in output or "enabled" in output
        except FileNotFoundError:
            pass

        return None

    @staticmethod
    def set_boot_sound(enabled: bool) -> Tuple[bool, str]:
        """
        Enable or disable POST boot sound.

        Args:
            enabled: True to enable, False to disable

        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            state = "on" if enabled else "off"
            result = subprocess.run(
                ["asusctl", "bios", "post-sound", state], capture_output=True, text=True
            )
            if result.returncode == 0:
                return True, f"Boot sound {'enabled' if enabled else 'disabled'}"
            return False, result.stderr.strip() or "Command failed"
        except FileNotFoundError:
            return False, "asusctl not found"
        except Exception as e:
            return False, str(e)
