#!/usr/bin/env python3
"""
System Tray Integration for Linux Armoury
Provides a system tray icon with quick access menu
"""

import gi
gi.require_version('Gtk', '4.0')
try:
    gi.require_version('Ayatana', '0.1')
    from gi.repository import Ayatana
    AYATANA_AVAILABLE = True
except (ValueError, ImportError):
    AYATANA_AVAILABLE = False
from gi.repository import Gtk
import subprocess


class SystemTrayIcon:
    """System tray icon handler using libayatana-appindicator"""
    
    def __init__(self, app_window):
        self.window = app_window
        self.indicator = None
        if AYATANA_AVAILABLE:
            self.setup_indicator()
        else:
            print("System tray not available: libayatana-appindicator not installed")
    
    def setup_indicator(self):
        """Setup the system tray indicator"""
        try:
            self.indicator = Ayatana.Indicator.new(
                "linux-armoury",
                "applications-system",
                Ayatana.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(Ayatana.IndicatorStatus.ACTIVE)
            self.indicator.set_title("Linux Armoury")
            
            # Create menu
            menu = Gtk.Menu()
            
            # Show/Hide window item
            show_item = Gtk.MenuItem.new_with_label("Show Window")
            show_item.connect("activate", self.on_show_window)
            menu.append(show_item)
            
            # Separator
            menu.append(Gtk.SeparatorMenuItem())
            
            # Quick power profiles with all 7 profiles
            profiles_menu = Gtk.Menu()
            profiles = [
                ("emergency", "Emergency (10W)"),
                ("battery", "Battery (18W)"),
                ("efficient", "Efficient (30W)"),
                ("balanced", "Balanced (40W)"),
                ("performance", "Performance (55W)"),
                ("gaming", "Gaming (70W)"),
                ("maximum", "Maximum (90W)")
            ]
            for profile_id, profile_label in profiles:
                profile_item = Gtk.MenuItem.new_with_label(profile_label)
                profile_item.connect("activate", self.on_quick_profile, profile_id)
                profiles_menu.append(profile_item)
            
            profiles_item = Gtk.MenuItem.new_with_label("Quick Profiles")
            profiles_item.set_submenu(profiles_menu)
            menu.append(profiles_item)
            
            # Quick refresh rates
            refresh_menu = Gtk.Menu()
            refresh_rates = [30, 60, 90, 120, 180]
            for rate in refresh_rates:
                rate_item = Gtk.MenuItem.new_with_label(f"{rate} Hz")
                rate_item.connect("activate", self.on_quick_refresh, rate)
                refresh_menu.append(rate_item)
            
            refresh_item = Gtk.MenuItem.new_with_label("Quick Refresh Rates")
            refresh_item.set_submenu(refresh_menu)
            menu.append(refresh_item)
            
            # Separator
            menu.append(Gtk.SeparatorMenuItem())
            
            # Quit item
            quit_item = Gtk.MenuItem.new_with_label("Quit")
            quit_item.connect("activate", self.on_quit)
            menu.append(quit_item)
            
            menu.show_all()
            self.indicator.set_menu(menu)
            
        except Exception as e:
            print(f"Could not create system tray icon: {e}")
            print("Install libayatana-appindicator for system tray support")
    
    def on_show_window(self, widget):
        """Show the main window"""
        if self.window:
            self.window.present()
    
    def on_quick_profile(self, widget, profile):
        """Apply power profile from tray menu"""
        try:
            subprocess.run(
                ["pkexec", "bash", "-c", f"command -v pwrcfg && pwrcfg {profile}"],
                timeout=10
            )
            # Update window if it exists
            if self.window:
                self.window.settings["current_power_profile"] = profile
                app = self.window.get_application()
                if app:
                    app.save_settings()
                    if hasattr(app, 'notify'):
                        app.notify("Power Profile Changed", f"Applied '{profile}' profile")
        except Exception as e:
            print(f"Error applying profile: {e}")
    
    def on_quick_refresh(self, widget, rate):
        """Apply refresh rate from tray menu"""
        try:
            # Import SystemUtils for display detection
            from system_utils import SystemUtils
            display = SystemUtils.get_primary_display()
            width, height = SystemUtils.get_display_resolution()
            
            subprocess.run(
                ["pkexec", "bash", "-c", f"xrandr --output {display} --mode {width}x{height} --rate {rate}"],
                timeout=10
            )
            # Update window if it exists
            if self.window:
                self.window.settings["current_refresh_rate"] = str(rate)
                app = self.window.get_application()
                if app:
                    app.save_settings()
                    if hasattr(app, 'notify'):
                        app.notify("Refresh Rate Changed", f"Display set to {rate} Hz")
        except Exception as e:
            print(f"Error changing refresh rate: {e}")
    
    def on_quit(self, widget):
        """Quit the application"""
        if self.window:
            app = self.window.get_application()
            if app:
                app.quit()
    
    def set_visible(self, visible):
        """Show or hide the tray icon"""
        if self.indicator:
            status = Ayatana.IndicatorStatus.ACTIVE if visible else Ayatana.IndicatorStatus.PASSIVE
            self.indicator.set_status(status)
    
    def update_status(self, status_text):
        """Update the tray icon status/tooltip"""
        if self.indicator:
            self.indicator.set_title(status_text)

