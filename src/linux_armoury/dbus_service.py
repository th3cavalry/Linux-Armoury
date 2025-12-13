#!/usr/bin/env python3
"""
Linux Armoury D-Bus Service
Provides a D-Bus interface for privileged operations

This service runs as root and handles:
- TDP/power profile changes
- System configuration that requires elevated privileges
"""

import os

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

from .system_utils import SystemUtils

DBUS_NAME = "com.github.th3cavalry.LinuxArmoury"
DBUS_PATH = "/com/github/th3cavalry/LinuxArmoury"
DBUS_INTERFACE = "com.github.th3cavalry.LinuxArmoury"


class LinuxArmouryService(dbus.service.Object):
    """D-Bus service for privileged operations"""

    VALID_PROFILES = [
        "emergency",
        "battery",
        "efficient",
        "balanced",
        "performance",
        "gaming",
        "maximum",
        "Quiet",
        "Balanced",
        "Performance",
        "power-saver",
    ]
    VALID_REFRESH_RATES = [30, 60, 90, 120, 180]

    def __init__(self, bus):
        bus_name = dbus.service.BusName(DBUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        print(f"Linux Armoury D-Bus service started on {DBUS_NAME}")

    @dbus.service.method(DBUS_INTERFACE, in_signature="s", out_signature="bs")
    def SetPowerProfile(self, profile):
        """Set the power profile"""
        # Basic validation (case-insensitive)
        if not isinstance(profile, str) or not profile:
            return (False, "Invalid profile name")

        # Basic validation (case-insensitive)
        if profile.lower() not in [p.lower() for p in self.VALID_PROFILES]:
            return (False, f"Unknown or unsupported profile: {profile}")

        try:
            success, message = SystemUtils.set_power_profile(profile)
            return (success, message)
        except Exception as e:
            return (False, f"An unexpected error occurred: {e!s}")

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="a{sv}")
    def GetStatus(self):
        """Get current system status"""
        status = {}

        # Read CPU temperature
        try:
            for path in [
                "/sys/class/thermal/thermal_zone0/temp",
                "/sys/class/hwmon/hwmon0/temp1_input",
            ]:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        temp = int(f.read().strip()) / 1000
                        status["cpu_temperature"] = dbus.Double(temp)
                        break
        except Exception:
            pass

        # Check if on AC power
        try:
            ac_path = SystemUtils.find_ac_path()
            if ac_path:
                online_path = os.path.join(ac_path, "online")
                if os.path.exists(online_path):
                    with open(online_path, "r") as f:
                        status["on_ac_power"] = dbus.Boolean(f.read().strip() == "1")
        except Exception:
            pass

        return status

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def GetVersion(self):
        """Return service version"""
        return "1.2.0"


def main():
    """Start the D-Bus service"""
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Try system bus first (for privileged operations), fall back to session
    try:
        bus = dbus.SystemBus()
        print("Using system bus")
    except dbus.exceptions.DBusException:
        bus = dbus.SessionBus()
        print("Falling back to session bus")

    # keep a reference to the service object so it isn't garbage collected
    # and flagged by linters as unused
    service = LinuxArmouryService(bus)  # noqa: F841

    mainloop = GLib.MainLoop()
    print("Entering main loop...")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("\nShutting down service")


if __name__ == "__main__":
    main()
