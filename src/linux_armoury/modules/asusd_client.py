#!/usr/bin/env python3
"""
asusd D-Bus Client for Linux Armoury

Provides integration with asusd daemon for ASUS laptop control.
Falls back to direct sysfs access when asusd is not available.
"""

import subprocess
from enum import Enum
from typing import Any, Dict, List, Optional


class ThrottlePolicy(Enum):
    """Platform throttle policies supported by asusd"""

    BALANCED = 0
    PERFORMANCE = 1
    QUIET = 2


class GpuMode(Enum):
    """GPU modes supported by supergfxctl"""

    HYBRID = "Hybrid"
    INTEGRATED = "Integrated"
    DEDICATED = "Dedicated"
    VFIO = "Vfio"
    EGPU = "Egpu"
    ASUSEGPU = "AsusEgpu"
    ASUSMUXDGPU = "AsusMuxDgpu"
    NONE = "None"


class AuraEffect(Enum):
    """Aura keyboard lighting effects"""

    STATIC = "Static"
    BREATHE = "Breathe"
    STROBE = "Strobe"
    RAINBOW = "Rainbow"
    STAR = "Star"
    RAIN = "Rain"
    HIGHLIGHT = "Highlight"
    LASER = "Laser"
    RIPPLE = "Ripple"
    PULSE = "Pulse"
    COMET = "Comet"
    FLASH = "Flash"


class AsusdClient:
    """D-Bus client for asusd daemon"""

    PLATFORM_IFACE = "org.asuslinux.Platform"
    PLATFORM_PATH = "/org/asuslinux/Platform"
    LED_IFACE = "org.asuslinux.Led"
    LED_PATH = "/org/asuslinux/Led"
    ANIME_IFACE = "org.asuslinux.Anime"
    ANIME_PATH = "/org/asuslinux/Anime"
    SERVICE_NAME = "org.asuslinux.Daemon"

    def __init__(self):
        self._bus = None
        self._available = None
        self._platform_proxy = None
        self._led_proxy = None
        self._anime_proxy = None

    def _get_bus(self):
        """Get D-Bus system bus connection"""
        if self._bus is None:
            try:
                import dbus

                self._bus = dbus.SystemBus()
            except Exception:
                self._bus = False
        return self._bus if self._bus else None

    def is_available(self) -> bool:
        """Check if asusd daemon is running and accessible"""
        if self._available is not None:
            return self._available

        bus = self._get_bus()
        if not bus:
            self._available = False
            return False

        try:
            import dbus

            proxy = bus.get_object(self.SERVICE_NAME, self.PLATFORM_PATH)
            proxy.Introspect(dbus_interface=dbus.INTROSPECTABLE_IFACE)
            self._available = True
        except Exception:
            self._available = False

        return self._available

    def _get_platform_proxy(self):
        """Get platform interface proxy"""
        if not self.is_available():
            return None
        if self._platform_proxy is None:
            import dbus

            self._platform_proxy = dbus.Interface(
                self._bus.get_object(self.SERVICE_NAME, self.PLATFORM_PATH),
                self.PLATFORM_IFACE,
            )
        return self._platform_proxy

    def _get_led_proxy(self):
        """Get LED interface proxy"""
        if not self.is_available():
            return None
        if self._led_proxy is None:
            import dbus

            self._led_proxy = dbus.Interface(
                self._bus.get_object(self.SERVICE_NAME, self.LED_PATH), self.LED_IFACE
            )
        return self._led_proxy

    # Platform Profile Methods
    def get_throttle_policy(self) -> Optional[ThrottlePolicy]:
        """Get current platform throttle policy"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return None
        try:
            policy = proxy.ThrottleThermalPolicy()
            return ThrottlePolicy(policy)
        except Exception:
            return None

    def set_throttle_policy(self, policy: ThrottlePolicy) -> bool:
        """Set platform throttle policy"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return False
        try:
            proxy.SetThrottleThermalPolicy(policy.value)
            return True
        except Exception:
            return False

    # Charge Control Methods
    def get_charge_limit(self) -> Optional[int]:
        """Get battery charge control end threshold (percentage)"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return None
        try:
            return int(proxy.ChargeControlEndThreshold())
        except Exception:
            return None

    def set_charge_limit(self, limit: int) -> bool:
        """Set battery charge control end threshold (60-100)"""
        if not 60 <= limit <= 100:
            return False
        proxy = self._get_platform_proxy()
        if not proxy:
            return False
        try:
            proxy.SetChargeControlEndThreshold(limit)
            return True
        except Exception:
            return False

    # Panel Overdrive Methods
    def get_panel_overdrive(self) -> Optional[bool]:
        """Get panel overdrive (OD) status"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return None
        try:
            return bool(proxy.PanelOd())
        except Exception:
            return None

    def set_panel_overdrive(self, enabled: bool) -> bool:
        """Set panel overdrive (OD) status"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return False
        try:
            proxy.SetPanelOd(enabled)
            return True
        except Exception:
            return False

    # GPU MUX Methods
    def get_gpu_mux_mode(self) -> Optional[str]:
        """Get current GPU MUX mode"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return None
        try:
            return str(proxy.GpuMuxMode())
        except Exception:
            return None

    def set_gpu_mux_mode(self, dedicated: bool) -> bool:
        """Set GPU MUX mode (True for dedicated, False for hybrid)"""
        proxy = self._get_platform_proxy()
        if not proxy:
            return False
        try:
            proxy.SetGpuMuxMode(1 if dedicated else 0)
            return True
        except Exception:
            return False


class SupergfxClient:
    """D-Bus client for supergfxctl daemon"""

    IFACE = "org.supergfxctl.Daemon"
    PATH = "/org/supergfxctl/Gfx"
    SERVICE_NAME = "org.supergfxctl.Daemon"

    def __init__(self):
        self._bus = None
        self._available = None
        self._proxy = None

    def _get_bus(self):
        """Get D-Bus system bus connection"""
        if self._bus is None:
            try:
                import dbus

                self._bus = dbus.SystemBus()
            except Exception:
                self._bus = False
        return self._bus if self._bus else None

    def is_available(self) -> bool:
        """Check if supergfxctl daemon is running and accessible"""
        if self._available is not None:
            return self._available

        bus = self._get_bus()
        if not bus:
            self._available = False
            return False

        try:
            import dbus

            proxy = bus.get_object(self.SERVICE_NAME, self.PATH)
            proxy.Introspect(dbus_interface=dbus.INTROSPECTABLE_IFACE)
            self._available = True
        except Exception:
            self._available = False

        return self._available

    def _get_proxy(self):
        """Get daemon interface proxy"""
        if not self.is_available():
            return None
        if self._proxy is None:
            import dbus

            self._proxy = dbus.Interface(
                self._bus.get_object(self.SERVICE_NAME, self.PATH), self.IFACE
            )
        return self._proxy

    def get_mode(self) -> Optional[GpuMode]:
        """Get current GPU mode"""
        proxy = self._get_proxy()
        if not proxy:
            return None
        try:
            mode = str(proxy.Mode())
            return GpuMode(mode)
        except Exception:
            return None

    def set_mode(self, mode: GpuMode) -> bool:
        """Set GPU mode (may require logout/reboot)"""
        proxy = self._get_proxy()
        if not proxy:
            return False
        try:
            proxy.SetMode(mode.value)
            return True
        except Exception:
            return False

    def get_supported_modes(self) -> List[GpuMode]:
        """Get list of supported GPU modes"""
        proxy = self._get_proxy()
        if not proxy:
            return []
        try:
            modes = proxy.Supported()
            return [GpuMode(m) for m in modes]
        except Exception:
            return []

    def get_power_status(self) -> Optional[str]:
        """Get dGPU power status"""
        proxy = self._get_proxy()
        if not proxy:
            return None
        try:
            return str(proxy.Power())
        except Exception:
            return None


# Global singleton instances
_asusd_client = None
_supergfx_client = None


def get_asusd_client() -> AsusdClient:
    """Get singleton asusd client instance"""
    global _asusd_client
    if _asusd_client is None:
        _asusd_client = AsusdClient()
    return _asusd_client


def get_supergfx_client() -> SupergfxClient:
    """Get singleton supergfxctl client instance"""
    global _supergfx_client
    if _supergfx_client is None:
        _supergfx_client = SupergfxClient()
    return _supergfx_client
