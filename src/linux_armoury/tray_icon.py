#!/usr/bin/env python3
"""
System Tray Integration for Linux Armoury
Provides system tray icon using multiple backends:
1. D-Bus StatusNotifierItem (SNI) - Modern standard
2. libayatana-appindicator - Legacy fallback
3. Background service mode - When no tray is available
"""

import os
from typing import Any, Callable, Dict, List, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib  # noqa: E402

# Try to import AppIndicator libraries
APPINDICATOR_AVAILABLE = False
AppIndicator = None

try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import (  # type: ignore  # noqa: E402
        AyatanaAppIndicator3 as AppIndicator,
    )

    APPINDICATOR_AVAILABLE = True
except (ValueError, ImportError):
    try:
        gi.require_version("AppIndicator3", "0.1")
        from gi.repository import (  # type: ignore  # noqa: E402
            AppIndicator3 as AppIndicator,
        )

        APPINDICATOR_AVAILABLE = True
    except (ValueError, ImportError):
        pass


class TrayIconStatus:
    """Status values for tray icon"""

    PASSIVE = "passive"
    ACTIVE = "active"
    ATTENTION = "attention"


class StatusNotifierItem:
    """D-Bus StatusNotifierItem implementation for modern desktops"""

    # D-Bus interface XML for StatusNotifierItem
    SNI_XML = """
    <node>
        <interface name="org.kde.StatusNotifierItem">
            <property name="Category" type="s" access="read"/>
            <property name="Id" type="s" access="read"/>
            <property name="Title" type="s" access="read"/>
            <property name="Status" type="s" access="read"/>
            <property name="IconName" type="s" access="read"/>
            <property name="Menu" type="o" access="read"/>
            <signal name="NewStatus">
                <arg type="s" name="status"/>
            </signal>
            <signal name="NewIcon"/>
            <signal name="NewTitle"/>
        </interface>
    </node>
    """

    def __init__(self, app_id: str, icon_name: str, title: str):
        self.app_id = app_id
        self.icon_name = icon_name
        self.title = title
        self.status = TrayIconStatus.ACTIVE
        self.menu_path = "/MenuBar"
        self.connection: Optional[Gio.DBusConnection] = None
        self.registration_id = 0
        self.watcher_id = 0
        self.menu_items: List[Dict[str, Any]] = []

    def register(self):
        """Register the StatusNotifierItem with D-Bus"""
        try:
            self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

            # Register our service name
            bus_name = f"org.kde.StatusNotifierItem-{os.getpid()}-1"
            Gio.bus_own_name_on_connection(
                self.connection, bus_name, Gio.BusNameOwnerFlags.NONE, None, None
            )

            # Register the StatusNotifierItem interface
            node_info = Gio.DBusNodeInfo.new_for_xml(self.SNI_XML)
            interface_info = node_info.interfaces[0]

            self.registration_id = self.connection.register_object(
                "/StatusNotifierItem",
                interface_info,
                self._handle_method_call,
                self._handle_get_property,
                None,
            )

            # Register with the StatusNotifierWatcher
            self.connection.call_sync(
                "org.kde.StatusNotifierWatcher",
                "/StatusNotifierWatcher",
                "org.kde.StatusNotifierWatcher",
                "RegisterStatusNotifierItem",
                GLib.Variant("(s)", (bus_name,)),
                None,
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )

            return True
        except Exception as e:
            print(f"Failed to register StatusNotifierItem: {e}")
            return False

    def _handle_method_call(
        self,
        connection,
        sender,
        object_path,
        interface_name,
        method_name,
        parameters,
        invocation,
    ):
        """Handle D-Bus method calls"""
        if method_name == "Activate":
            # Primary action (left click)
            if self.on_activate:
                self.on_activate()
        elif method_name == "ContextMenu":
            # Context menu (right click)
            if self.on_context_menu:
                self.on_context_menu()
        elif method_name == "SecondaryActivate":
            # Secondary action (middle click)
            pass

        invocation.return_value(None)

    def _handle_get_property(
        self, connection, sender, object_path, interface_name, property_name
    ):
        """Handle D-Bus property reads"""
        if property_name == "Category":
            return GLib.Variant("s", "ApplicationStatus")
        elif property_name == "Id":
            return GLib.Variant("s", self.app_id)
        elif property_name == "Title":
            return GLib.Variant("s", self.title)
        elif property_name == "Status":
            return GLib.Variant("s", self.status.capitalize())
        elif property_name == "IconName":
            return GLib.Variant("s", self.icon_name)
        elif property_name == "Menu":
            return GLib.Variant("o", self.menu_path)
        return None

    def set_status(self, status: str):
        """Set the status icon state"""
        self.status = status
        if self.connection:
            self.connection.emit_signal(
                None,
                "/StatusNotifierItem",
                "org.kde.StatusNotifierItem",
                "NewStatus",
                GLib.Variant("(s)", (status.capitalize(),)),
            )

    def set_title(self, title: str):
        """Set the icon title/tooltip"""
        self.title = title
        if self.connection:
            self.connection.emit_signal(
                None,
                "/StatusNotifierItem",
                "org.kde.StatusNotifierItem",
                "NewTitle",
                None,
            )

    def unregister(self):
        """Unregister from D-Bus"""
        if self.connection and self.registration_id:
            self.connection.unregister_object(self.registration_id)
            self.registration_id = 0


class SystemTrayIcon:
    """System tray icon handler with multiple backend support"""

    def __init__(self, app_window=None, app_id: str = "linux-armoury"):
        self.window = app_window
        self.app_id = app_id
        self.indicator: Any = None
        self.sni: Optional[StatusNotifierItem] = None
        self.is_active = False

        # Callbacks
        self.on_show_window: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        self.on_profile_change: Optional[Callable] = None
        self.on_refresh_change: Optional[Callable] = None

        # Initialize with best available backend
        self._init_tray()

    def _init_tray(self):
        """Initialize tray icon with best available backend"""
        # Try SNI first (modern standard)
        if self._try_sni():
            print("Using StatusNotifierItem for system tray")
            self.is_active = True
            return

        # Fall back to AppIndicator
        if APPINDICATOR_AVAILABLE and self._try_appindicator():
            print("Using AppIndicator for system tray")
            self.is_active = True
            return

        print("No system tray support available")
        print("Install AppIndicator or use a desktop with SNI support")
        print("The app will run in background mode when closed")

    def _try_sni(self) -> bool:
        """Try to use StatusNotifierItem"""
        try:
            self.sni = StatusNotifierItem(
                self.app_id, "applications-system", "Linux Armoury"
            )
            if self.sni:
                return self.sni.register()
            return False
        except Exception as e:
            print(f"SNI not available: {e}")
            return False

    def _try_appindicator(self) -> bool:
        """Try to use AppIndicator"""
        if not APPINDICATOR_AVAILABLE or AppIndicator is None:
            return False

        try:
            self.indicator = AppIndicator.Indicator.new(
                self.app_id,
                "applications-system",
                AppIndicator.IndicatorCategory.APPLICATION_STATUS,
            )
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self.indicator.set_title("Linux Armoury")

            # Create menu (requires GTK3 Menu for AppIndicator)
            self._create_appindicator_menu()

            return True
        except Exception as e:
            print(f"AppIndicator failed: {e}")
            return False

    def _create_appindicator_menu(self):
        """Create menu for AppIndicator (GTK3-based)"""
        if not self.indicator:
            return

        # Import GTK3 for AppIndicator menu
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk as Gtk3  # noqa: E402

        menu = Gtk3.Menu()

        # Show Window
        show_item = Gtk3.MenuItem.new_with_label("Show Window")
        show_item.connect("activate", lambda w: self._on_show())
        menu.append(show_item)

        menu.append(Gtk3.SeparatorMenuItem())

        # Quick Profiles submenu
        profiles_menu = Gtk3.Menu()
        profiles = [
            ("emergency", "Emergency (10W)"),
            ("battery", "Battery (18W)"),
            ("efficient", "Efficient (30W)"),
            ("balanced", "Balanced (40W)"),
            ("performance", "Performance (55W)"),
            ("gaming", "Gaming (70W)"),
            ("maximum", "Maximum (90W)"),
        ]
        for profile_id, profile_label in profiles:
            item = Gtk3.MenuItem.new_with_label(profile_label)
            item.connect("activate", lambda w, p=profile_id: self._on_profile(p))
            profiles_menu.append(item)

        profiles_item = Gtk3.MenuItem.new_with_label("Power Profiles")
        profiles_item.set_submenu(profiles_menu)
        menu.append(profiles_item)

        # Refresh Rates submenu
        refresh_menu = Gtk3.Menu()
        for rate in [30, 60, 90, 120, 180]:
            item = Gtk3.MenuItem.new_with_label(f"{rate} Hz")
            item.connect("activate", lambda w, r=rate: self._on_refresh(r))
            refresh_menu.append(item)

        refresh_item = Gtk3.MenuItem.new_with_label("Refresh Rate")
        refresh_item.set_submenu(refresh_menu)
        menu.append(refresh_item)

        menu.append(Gtk3.SeparatorMenuItem())

        # Quit
        quit_item = Gtk3.MenuItem.new_with_label("Quit")
        quit_item.connect("activate", lambda w: self._on_quit())
        menu.append(quit_item)

        menu.show_all()
        self.indicator.set_menu(menu)

    def _on_show(self):
        """Handle show window action"""
        if self.window:
            self.window.present()
        elif self.on_show_window:
            self.on_show_window()

    def _on_quit(self):
        """Handle quit action"""
        if self.on_quit:
            self.on_quit()
        elif self.window:
            app = self.window.get_application()
            if app:
                app.quit()

    def _on_profile(self, profile: str):
        """Handle profile change from tray"""
        if self.on_profile_change:
            self.on_profile_change(profile)
        else:
            self._apply_profile(profile)

    def _on_refresh(self, rate: int):
        """Handle refresh rate change from tray"""
        if self.on_refresh_change:
            self.on_refresh_change(rate)
        else:
            self._apply_refresh(rate)

    def _apply_profile(self, profile: str):
        """Apply power profile"""
        valid_profiles = [
            "emergency",
            "battery",
            "efficient",
            "balanced",
            "performance",
            "gaming",
            "maximum",
        ]
        if profile not in valid_profiles:
            return

        try:
            from .system_utils import SystemUtils

            success, message = SystemUtils.set_power_profile(profile)

            if success and self.window:
                self.window.settings["current_power_profile"] = profile
                app = self.window.get_application()
                if app:
                    app.save_settings()
        except Exception as e:
            print(f"Error applying profile: {e}")

    def _apply_refresh(self, rate: int):
        """Apply refresh rate"""
        valid_rates = [30, 60, 90, 120, 180]
        if rate not in valid_rates:
            return

        try:
            from .system_utils import SystemUtils

            success, message = SystemUtils.set_refresh_rate(rate)

            if success and self.window:
                self.window.settings["current_refresh_rate"] = str(rate)
                app = self.window.get_application()
                if app:
                    app.save_settings()
        except Exception as e:
            print(f"Error applying refresh rate: {e}")

    def set_visible(self, visible: bool):
        """Show or hide the tray icon"""
        if self.sni:
            self.sni.set_status(
                TrayIconStatus.ACTIVE if visible else TrayIconStatus.PASSIVE
            )
        elif self.indicator and AppIndicator:
            status = (
                AppIndicator.IndicatorStatus.ACTIVE
                if visible
                else AppIndicator.IndicatorStatus.PASSIVE
            )
            self.indicator.set_status(status)

    def set_status(self, status: str):
        """Set tray icon status (active/attention/passive)"""
        if self.sni:
            self.sni.set_status(status)
        elif self.indicator and AppIndicator:
            if status == TrayIconStatus.ATTENTION:
                self.indicator.set_status(AppIndicator.IndicatorStatus.ATTENTION)
            elif status == TrayIconStatus.PASSIVE:
                self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
            else:
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def set_title(self, title: str):
        """Update the tray icon title/tooltip"""
        if self.sni:
            self.sni.set_title(title)
        elif self.indicator:
            self.indicator.set_title(title)

    def update_status_text(
        self,
        cpu_temp: Optional[float] = None,
        battery: Optional[int] = None,
        profile: Optional[str] = None,
    ):
        """Update tooltip with current status"""
        parts = ["Linux Armoury"]

        if cpu_temp is not None:
            parts.append(f"CPU: {cpu_temp:.0f}°C")
        if battery is not None:
            parts.append(f"Battery: {battery}%")
        if profile:
            parts.append(f"Profile: {profile.capitalize()}")

        self.set_title(" | ".join(parts))

    def cleanup(self):
        """Clean up tray resources"""
        if self.sni:
            self.sni.unregister()
            self.sni = None
        self.indicator = None
        self.is_active = False


def create_tray_icon(app_window=None) -> SystemTrayIcon:
    """Factory function to create a tray icon"""
    return SystemTrayIcon(app_window)
