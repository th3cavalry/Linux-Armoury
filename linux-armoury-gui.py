#!/usr/bin/env python3
"""
Linux Armoury - GUI Control Center for ASUS GZ302EA Laptop
A lightweight control tool similar to G-Helper and ROG Control Center
Features: TDP control, refresh rate management, light/dark mode, system tray
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import sys
import os
import json
from typing import Optional

# New modules for configuration and system utilities
try:
    from config import Config
except Exception:
    class Config:  # minimal fallback if config.py not installed
        APP_ID = 'com.github.th3cavalry.linux-armoury'
        DEFAULT_RESOLUTION = '2560x1600'
        VERSION = '1.0.0'

try:
    from system_utils import SystemUtils
except Exception:
    class SystemUtils:  # minimal fallbacks
        @staticmethod
        def get_primary_display():
            return "eDP-1"
        @staticmethod
        def get_display_resolution():
            try:
                w, h = Config.DEFAULT_RESOLUTION.split('x')
                return (int(w), int(h))
            except Exception:
                return (2560, 1600)
        @staticmethod
        def get_current_refresh_rate():
            return None
        @staticmethod
        def get_current_tdp():
            return None

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/linux-armoury")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

class LinuxArmouryApp(Adw.Application):
    """Main application class"""
    
    def __init__(self):
        # Prefer Config.APP_ID if available
        app_id = getattr(Config, 'APP_ID', 'com.github.th3cavalry.linux-armoury')
        super().__init__(application_id=app_id,
                        flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.settings = self.load_settings()
        
        # Track last notification id counter
        self._notify_counter = 0

        # Application-level actions
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda a, p: self.quit())
        self.add_action(quit_action)
        # Global accelerators
        try:
            accel = getattr(Config, 'SHORTCUTS', {}).get('quit', '<Control>q')
            self.set_accels_for_action("app.quit", [accel])
        except Exception:
            pass
        
    def do_activate(self):
        """Called when the application is activated"""
        if not self.window:
            self.window = MainWindow(application=self, settings=self.settings)
        self.window.present()
    
    def load_settings(self):
        """Load application settings from file"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        default_settings = {
            "theme": "auto",  # auto, light, dark
            "autostart": False,
            "minimize_to_tray": True,
            "current_power_profile": "balanced",
            "current_refresh_rate": "balanced"
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save application settings to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def notify(self, title: str, body: str, priority: str = "normal"):
        """Send a desktop notification via Gio.Notification."""
        try:
            n = Gio.Notification.new(title)
            n.set_body(body)
            pr_map = {
                'low': Gio.NotificationPriority.LOW,
                'normal': Gio.NotificationPriority.NORMAL,
                'high': Gio.NotificationPriority.HIGH,
                'urgent': Gio.NotificationPriority.URGENT,
            }
            n.set_priority(pr_map.get(priority, Gio.NotificationPriority.NORMAL))
            # Unique id per notification
            self._notify_counter += 1
            self.send_notification(f"linux-armoury-{self._notify_counter}", n)
        except Exception as e:
            # Notifications are optional; log and continue
            print(f"Notification error: {e}")


class MainWindow(Adw.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop('settings', {})
        super().__init__(*args, **kwargs)
        
        self.set_title("Linux Armoury")
        self.set_default_size(800, 600)
        
        # Apply theme
        self.apply_theme(self.settings.get("theme", "auto"))
        
        # Build UI
        self.setup_ui()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Load current status
        self.refresh_status()
    
    def apply_theme(self, theme):
        """Apply light/dark theme"""
        style_manager = Adw.StyleManager.get_default()
        if theme == "light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme == "dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:  # auto
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
    
    def setup_ui(self):
        """Build the user interface"""
        # Main box container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header bar
        header = Adw.HeaderBar()
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        
        # Theme submenu
        theme_menu = Gio.Menu()
        theme_menu.append("Light Mode", "win.theme-light")
        theme_menu.append("Dark Mode", "win.theme-dark")
        theme_menu.append("Auto", "win.theme-auto")
        menu.append_submenu("Theme", theme_menu)
        
        # Other menu items
        menu.append("Preferences", "win.preferences")
        menu.append("About", "win.about")
        menu.append("Quit", "app.quit")
        
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        main_box.append(header)
        
        # Content area with scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Status section
        status_group = self.create_status_section()
        content_box.append(status_group)
        
        # Power profile section
        power_group = self.create_power_profile_section()
        content_box.append(power_group)
        
        # Refresh rate section
        refresh_group = self.create_refresh_rate_section()
        content_box.append(refresh_group)
        
        scrolled.set_child(content_box)
        main_box.append(scrolled)
        
        self.set_content(main_box)
        
        # Setup actions
        self.setup_actions()

    def setup_shortcuts(self):
        """Add a few useful keyboard shortcuts (Ctrl+Q, F5)."""
        try:
            controller = Gtk.ShortcutController()
            controller.set_scope(Gtk.ShortcutScope.MANAGED)
            # Quit with Ctrl+Q
            controller.add_shortcut(
                Gtk.Shortcut.new(
                    Gtk.ShortcutTrigger.parse_string("<Control>q"),
                    Gtk.CallbackAction.new(lambda *_: self.get_application().quit())
                )
            )
            # Refresh status with F5
            controller.add_shortcut(
                Gtk.Shortcut.new(
                    Gtk.ShortcutTrigger.parse_string("F5"),
                    Gtk.CallbackAction.new(lambda *_: self.refresh_status())
                )
            )
            self.add_controller(controller)
        except Exception as e:
            print(f"Shortcut setup failed: {e}")
    
    def create_status_section(self):
        """Create the status information section"""
        group = Adw.PreferencesGroup()
        group.set_title("System Status")
        group.set_description("Current system performance status")
        
        # Current power profile
        self.power_status_row = Adw.ActionRow()
        self.power_status_row.set_title("Power Profile")
        self.power_status_row.set_subtitle("Loading...")
        group.add(self.power_status_row)
        
        # Current refresh rate
        self.refresh_status_row = Adw.ActionRow()
        self.refresh_status_row.set_title("Refresh Rate")
        self.refresh_status_row.set_subtitle("Loading...")
        group.add(self.refresh_status_row)
        
        # TDP status
        self.tdp_status_row = Adw.ActionRow()
        self.tdp_status_row.set_title("TDP Settings")
        self.tdp_status_row.set_subtitle("Loading...")
        group.add(self.tdp_status_row)
        
        return group
    
    def create_power_profile_section(self):
        """Create the power profile control section"""
        group = Adw.PreferencesGroup()
        group.set_title("Power Profiles")
        group.set_description("Control system TDP and performance")
        
        # Power profiles list
        profiles = [
            ("emergency", "Emergency", "10W @ 30Hz - Critical battery preservation"),
            ("battery", "Battery Saver", "18W @ 30Hz - Maximum battery life"),
            ("efficient", "Efficient", "30W @ 60Hz - Balanced efficiency"),
            ("balanced", "Balanced", "40W @ 90Hz - Default balanced mode"),
            ("performance", "Performance", "55W @ 120Hz - High performance"),
            ("gaming", "Gaming", "70W @ 180Hz - Gaming optimized"),
            ("maximum", "Maximum", "90W @ 180Hz - Absolute maximum"),
        ]
        
        for profile_id, title, description in profiles:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(description)
            
            # Add button to apply profile
            button = Gtk.Button()
            button.set_label("Apply")
            button.set_valign(Gtk.Align.CENTER)
            button.connect("clicked", self.on_power_profile_clicked, profile_id)
            row.add_suffix(button)
            
            group.add(row)
        
        return group
    
    def create_refresh_rate_section(self):
        """Create the refresh rate control section"""
        group = Adw.PreferencesGroup()
        group.set_title("Refresh Rate Profiles")
        group.set_description("Control display refresh rate")
        
        # Refresh rate profiles
        profiles = [
            ("30", "30 Hz", "Power saving mode"),
            ("60", "60 Hz", "Standard"),
            ("90", "90 Hz", "Smooth"),
            ("120", "120 Hz", "High refresh"),
            ("180", "180 Hz", "Maximum gaming"),
        ]
        
        for profile_id, title, description in profiles:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(description)
            
            # Add button to apply profile
            button = Gtk.Button()
            button.set_label("Apply")
            button.set_valign(Gtk.Align.CENTER)
            button.connect("clicked", self.on_refresh_rate_clicked, profile_id)
            row.add_suffix(button)
            
            group.add(row)
        
        return group
    
    def setup_actions(self):
        """Setup window and application actions"""
        # Theme actions
        light_action = Gio.SimpleAction.new("theme-light", None)
        light_action.connect("activate", lambda a, p: self.change_theme("light"))
        self.add_action(light_action)
        
        dark_action = Gio.SimpleAction.new("theme-dark", None)
        dark_action.connect("activate", lambda a, p: self.change_theme("dark"))
        self.add_action(dark_action)
        
        auto_action = Gio.SimpleAction.new("theme-auto", None)
        auto_action.connect("activate", lambda a, p: self.change_theme("auto"))
        self.add_action(auto_action)
        
        # Preferences action
        pref_action = Gio.SimpleAction.new("preferences", None)
        pref_action.connect("activate", self.show_preferences)
        self.add_action(pref_action)
        
        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.show_about)
        self.add_action(about_action)
    
    def change_theme(self, theme):
        """Change application theme"""
        self.apply_theme(theme)
        self.settings["theme"] = theme
        self.get_application().save_settings()
    
    def on_power_profile_clicked(self, button, profile):
        """Handle power profile button click"""
        try:
            # Run pwrcfg command to set power profile
            result = subprocess.run(
                ["pkexec", "bash", "-c", f"command -v pwrcfg >/dev/null 2>&1 && pwrcfg {profile} || echo 'pwrcfg not found'"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                if "not found" in result.stdout:
                    self.show_error_dialog(
                        "pwrcfg command not found.\n\n"
                        "Linux Armoury requires the GZ302-Linux-Setup tools for power management.\n\n"
                        "Quick install:\n"
                        "1) curl -L https://raw.githubusercontent.com/th3cavalry/GZ302-Linux-Setup/main/gz302-main.sh -o gz302-main.sh\n"
                        "2) chmod +x gz302-main.sh\n"
                        "3) sudo ./gz302-main.sh\n\n"
                        "More info: https://github.com/th3cavalry/GZ302-Linux-Setup"
                    )
                else:
                    self.settings["current_power_profile"] = profile
                    self.get_application().save_settings()
                    self.show_success_dialog(f"Power profile set to {profile}")
                    # Notify
                    app = self.get_application()
                    if hasattr(app, 'notify'):
                        app.notify("Power Profile Changed", f"Applied '{profile}' profile successfully")
                    self.refresh_status()
            else:
                self.show_error_dialog(f"Failed to set power profile: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.show_error_dialog("Command timed out")
        except Exception as e:
            self.show_error_dialog(f"Error: {str(e)}")
    
    def on_refresh_rate_clicked(self, button, rate):
        """Handle refresh rate button click"""
        try:
            # Detect display and resolution
            display = SystemUtils.get_primary_display()
            width, height = SystemUtils.get_display_resolution()
            # Run xrandr command to set refresh rate
            result = subprocess.run(
                ["pkexec", "bash", "-c", f"xrandr --output {display} --mode {width}x{height} --rate {rate} 2>&1 || echo 'xrandr failed'"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                if "failed" in result.stdout:
                    self.show_error_dialog("Failed to set refresh rate. Display may not support this mode.")
                else:
                    self.settings["current_refresh_rate"] = rate
                    self.get_application().save_settings()
                    self.show_success_dialog(f"Refresh rate set to {rate} Hz")
                    # Notify
                    app = self.get_application()
                    if hasattr(app, 'notify'):
                        app.notify("Refresh Rate Changed", f"Display set to {rate} Hz")
                    self.refresh_status()
            else:
                self.show_error_dialog(f"Failed to set refresh rate: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.show_error_dialog("Command timed out")
        except Exception as e:
            self.show_error_dialog(f"Error: {str(e)}")
    
    def refresh_status(self):
        """Refresh the status information"""
        # Update power profile status
        current_profile = self.settings.get("current_power_profile", "Unknown")
        self.power_status_row.set_subtitle(current_profile.capitalize())
        
        # Update refresh rate status
        detected_rate = SystemUtils.get_current_refresh_rate()
        if detected_rate:
            self.refresh_status_row.set_subtitle(f"{detected_rate} Hz")
        else:
            current_rate = self.settings.get("current_refresh_rate", "Unknown")
            self.refresh_status_row.set_subtitle(f"{current_rate} Hz")
        
        # Update TDP status (attempt to read actual system values)
        tdp = SystemUtils.get_current_tdp()
        if tdp:
            self.tdp_status_row.set_subtitle(f"Current TDP: {tdp} W")
        else:
            self.tdp_status_row.set_subtitle("Available via power profiles")
    
    def show_success_dialog(self, message):
        """Show success message dialog"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Success")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present()
    
    def show_error_dialog(self, message):
        """Show error message dialog"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Error")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present()
    
    def show_preferences(self, action, param):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self)
        dialog.present()
    
    def show_about(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Linux Armoury",
            application_icon="applications-system",
            developer_name="th3cavalry",
            version=getattr(Config, 'VERSION', '1.0.0'),
            developers=["th3cavalry"],
            copyright="© 2025 th3cavalry",
            website="https://github.com/th3cavalry/Linux-Armoury",
            issue_url="https://github.com/th3cavalry/Linux-Armoury/issues",
            license_type=Gtk.License.GPL_3_0
        )
        about.present()


class PreferencesDialog(Adw.PreferencesWindow):
    """Preferences dialog window"""
    
    def __init__(self, parent):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Preferences")
        
        # General preferences page
        page = Adw.PreferencesPage()
        page.set_title("General")
        page.set_icon_name("preferences-system")
        
        # Startup group
        startup_group = Adw.PreferencesGroup()
        startup_group.set_title("Startup")
        
        # Autostart switch
        autostart_row = Adw.ActionRow()
        autostart_row.set_title("Start on Boot")
        autostart_row.set_subtitle("Launch Linux Armoury when system starts")
        
        autostart_switch = Gtk.Switch()
        autostart_switch.set_valign(Gtk.Align.CENTER)
        autostart_switch.set_active(parent.settings.get("autostart", False))
        autostart_switch.connect("notify::active", self.on_autostart_toggled, parent)
        autostart_row.add_suffix(autostart_switch)
        
        startup_group.add(autostart_row)
        page.add(startup_group)
        
        # Behavior group
        behavior_group = Adw.PreferencesGroup()
        behavior_group.set_title("Behavior")
        
        # Minimize to tray switch
        minimize_row = Adw.ActionRow()
        minimize_row.set_title("Minimize to System Tray")
        minimize_row.set_subtitle("Keep running in background when window is closed")
        
        minimize_switch = Gtk.Switch()
        minimize_switch.set_valign(Gtk.Align.CENTER)
        minimize_switch.set_active(parent.settings.get("minimize_to_tray", True))
        minimize_switch.connect("notify::active", self.on_minimize_toggled, parent)
        minimize_row.add_suffix(minimize_switch)
        
        behavior_group.add(minimize_row)
        page.add(behavior_group)
        
        self.add(page)
    
    def on_autostart_toggled(self, switch, param, parent):
        """Handle autostart toggle"""
        enabled = switch.get_active()
        parent.settings["autostart"] = enabled
        parent.get_application().save_settings()
        self.update_autostart(enabled)
    
    def on_minimize_toggled(self, switch, param, parent):
        """Handle minimize to tray toggle"""
        enabled = switch.get_active()
        parent.settings["minimize_to_tray"] = enabled
        parent.get_application().save_settings()
    
    def update_autostart(self, enabled):
        """Update autostart desktop file"""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        autostart_file = os.path.join(autostart_dir, "linux-armoury.desktop")
        
        if enabled:
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Linux Armoury
Comment=ASUS GZ302EA Control Center
Exec={sys.argv[0]}
Icon=applications-system
Terminal=false
Categories=System;Settings;
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
            with open(autostart_file, 'w') as f:
                f.write(desktop_content)
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)


def main():
    """Main entry point"""
    app = LinuxArmouryApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
