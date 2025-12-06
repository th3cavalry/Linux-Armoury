#!/usr/bin/env python3
"""
Linux Armoury D-Bus Service
Provides a D-Bus interface for privileged operations

This service runs as root and handles:
- TDP/power profile changes
- System configuration that requires elevated privileges
"""

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess
import os
from .system_utils import SystemUtils


DBUS_NAME = "com.github.th3cavalry.LinuxArmoury"
DBUS_PATH = "/com/github/th3cavalry/LinuxArmoury"
DBUS_INTERFACE = "com.github.th3cavalry.LinuxArmoury"


class LinuxArmouryService(dbus.service.Object):
    """D-Bus service for privileged operations"""
    
    VALID_PROFILES = ["emergency", "battery", "efficient", "balanced", "performance", "gaming", "maximum"]
    VALID_REFRESH_RATES = [30, 60, 90, 120, 180]
    
    def __init__(self, bus):
        bus_name = dbus.service.BusName(DBUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)
        print(f"Linux Armoury D-Bus service started on {DBUS_NAME}")
    
    @dbus.service.method(DBUS_INTERFACE,
                         in_signature="s", out_signature="bs")
    def SetPowerProfile(self, profile):
        """Set the power profile using pwrcfg"""
        if profile not in self.VALID_PROFILES:
            return (False, f"Invalid profile: {profile}")
        
        try:
            # Check if pwrcfg is available
            if not SystemUtils.check_command_exists("pwrcfg"):
                return (False, "pwrcfg command not found")
            
            result = subprocess.run(
                ["pwrcfg", profile],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return (True, f"Power profile set to {profile}")
            else:
                return (False, f"Failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            return (False, "Command timed out")
        except Exception as e:
            return (False, str(e))
    
    @dbus.service.method(DBUS_INTERFACE,
                         in_signature="", out_signature="a{sv}")
    def GetStatus(self):
        """Get current system status"""
        status = {}
        
        # Read CPU temperature
        try:
            for path in ["/sys/class/thermal/thermal_zone0/temp",
                         "/sys/class/hwmon/hwmon0/temp1_input"]:
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
    
    @dbus.service.method(DBUS_INTERFACE,
                         in_signature="", out_signature="s")
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
    
    service = LinuxArmouryService(bus)
    
    mainloop = GLib.MainLoop()
    print("Entering main loop...")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("\nShutting down service")


if __name__ == "__main__":
    main()
