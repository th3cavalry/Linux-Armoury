#!/usr/bin/env python3
"""
Linux Armoury - Demo/Test Mode
Runs the GUI without requiring system integration for testing purposes
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import sys
import os
import importlib.util

# Add current directory to path to import the main application
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# We'll need to handle the import differently since the filename has a dash
import importlib.util
spec = importlib.util.spec_from_file_location(
    "linux_armoury_gui",
    os.path.join(os.path.dirname(__file__), "linux-armoury-gui.py")
)
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

# Monkey patch the command execution methods to use demo mode
original_power_clicked = main_app.MainWindow.on_power_profile_clicked
original_refresh_clicked = main_app.MainWindow.on_refresh_rate_clicked

def demo_power_clicked(self, button, profile):
    """Demo version that doesn't execute system commands"""
    print(f"[DEMO MODE] Would set power profile to: {profile}")
    self.settings["current_power_profile"] = profile
    self.get_application().save_settings()
    self.show_success_dialog(f"[DEMO] Power profile set to {profile}")
    self.refresh_status()

def demo_refresh_clicked(self, button, rate):
    """Demo version that doesn't execute system commands"""
    print(f"[DEMO MODE] Would set refresh rate to: {rate} Hz")
    self.settings["current_refresh_rate"] = rate
    self.get_application().save_settings()
    self.show_success_dialog(f"[DEMO] Refresh rate set to {rate} Hz")
    self.refresh_status()

# Apply the demo mode patches
main_app.MainWindow.on_power_profile_clicked = demo_power_clicked
main_app.MainWindow.on_refresh_rate_clicked = demo_refresh_clicked

def main():
    """Run the application in demo mode"""
    print("="*60)
    print("  Linux Armoury - DEMO MODE")
    print("="*60)
    print()
    print("Running in demonstration mode - no system changes will be made")
    print("This is useful for:")
    print("  - Testing the UI without root privileges")
    print("  - Development and debugging")
    print("  - Previewing the interface")
    print()
    print("Note: Power profile and refresh rate changes will be simulated")
    print("      but not actually applied to the system.")
    print()
    print("="*60)
    print()
    
    # Create and run the application
    app = main_app.LinuxArmouryApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
