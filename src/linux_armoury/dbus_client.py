#!/usr/bin/env python3
"""
D-Bus Client for Linux Armoury
Provides a convenient interface to communicate with the D-Bus service
"""

from typing import Any, Dict, Optional, Tuple

import dbus

DBUS_NAME = "com.github.th3cavalry.LinuxArmoury"
DBUS_PATH = "/com/github/th3cavalry/LinuxArmoury"
DBUS_INTERFACE = "com.github.th3cavalry.LinuxArmoury"


class LinuxArmouryClient:
    """Client for communicating with the Linux Armoury D-Bus service"""

    def __init__(self):
        self._proxy = None
        self._interface = None

    def _connect(self) -> bool:
        """Connect to the D-Bus service"""
        if self._proxy is not None:
            return True

        try:
            # Try system bus first
            try:
                bus = dbus.SystemBus()
            except dbus.exceptions.DBusException:
                bus = dbus.SessionBus()

            self._proxy = bus.get_object(DBUS_NAME, DBUS_PATH)
            self._interface = dbus.Interface(self._proxy, DBUS_INTERFACE)
            return True
        except dbus.exceptions.DBusException as e:
            print(f"Failed to connect to D-Bus service: {e}")
            self._proxy = None
            self._interface = None
            return False

    def is_service_available(self) -> bool:
        """Check if the D-Bus service is available"""
        return self._connect()

    def set_power_profile(self, profile: str) -> Tuple[bool, str]:
        """Set power profile via D-Bus service"""
        if not self._connect():
            return (False, "D-Bus service not available")

        try:
            success, message = self._interface.SetPowerProfile(profile)
            return (bool(success), str(message))
        except dbus.exceptions.DBusException as e:
            return (False, str(e))

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get system status from D-Bus service"""
        if not self._connect():
            return None

        try:
            status = self._interface.GetStatus()
            # Convert D-Bus types to Python types
            return {str(k): v for k, v in status.items()}
        except dbus.exceptions.DBusException:
            return None

    def get_version(self) -> Optional[str]:
        """Get service version"""
        if not self._connect():
            return None

        try:
            return str(self._interface.GetVersion())
        except dbus.exceptions.DBusException:
            return None


# Singleton instance for easy access
_client: Optional[LinuxArmouryClient] = None


def get_client() -> LinuxArmouryClient:
    """Get or create the D-Bus client singleton"""
    global _client
    if _client is None:
        _client = LinuxArmouryClient()
    return _client
