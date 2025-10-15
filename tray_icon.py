#!/usr/bin/env python3
"""
System Tray Integration for Linux Armoury
Provides a system tray icon with quick access menu
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Ayatana', '0.1')
from gi.repository import Gtk, Ayatana
import subprocess


class SystemTrayIcon:
    """System tray icon handler using libayatana-appindicator"""
    
    def __init__(self, app_window):
        self.window = app_window
        self.indicator = None
        self.setup_indicator()
    
    def setup_indicator(self):
        """Setup the system tray indicator"""
        try:
            self.indicator = Ayatana.Indicator.new(
                "linux-armoury",
                "applications-system",
                Ayatana.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(Ayatana.IndicatorStatus.ACTIVE)
            
            # Create menu
            menu = Gtk.Menu()
            
            # Show/Hide window item
            show_item = Gtk.MenuItem.new_with_label("Show Window")
            show_item.connect("activate", self.on_show_window)
            menu.append(show_item)
            
            # Separator
            menu.append(Gtk.SeparatorMenuItem())
            
            # Quick power profiles
            profiles_menu = Gtk.Menu()
            for profile in ["battery", "balanced", "performance", "gaming"]:
                profile_item = Gtk.MenuItem.new_with_label(profile.capitalize())
                profile_item.connect("activate", self.on_quick_profile, profile)
                profiles_menu.append(profile_item)
            
            profiles_item = Gtk.MenuItem.new_with_label("Quick Profiles")
            profiles_item.set_submenu(profiles_menu)
            menu.append(profiles_item)
            
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
        except Exception as e:
            print(f"Error applying profile: {e}")
    
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
