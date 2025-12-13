#!/usr/bin/env python3
"""
Linux Armoury CLI - Command-Line Interface
Provides terminal-based control for power profiles and system monitoring

Usage:
    linux-armoury-cli --profile gaming
    linux-armoury-cli --status
    linux-armoury-cli --monitor
    linux-armoury-cli --gui

Author: th3cavalry
License: GPL-3.0
"""

import argparse
import subprocess
import sys

from .config import Config
from .system_utils import SystemUtils

# typing imports not required here


# Optional new feature modules
try:
    from .modules.battery_control import get_battery_controller

    HAS_BATTERY_CONTROL = True
except ImportError:
    HAS_BATTERY_CONTROL = False

try:
    from .modules.fan_control import get_fan_controller

    HAS_FAN_CONTROL = True
except ImportError:
    HAS_FAN_CONTROL = False

try:
    from .modules.keyboard_control import get_keyboard_controller

    HAS_KEYBOARD_CONTROL = True
except ImportError:
    HAS_KEYBOARD_CONTROL = False

try:
    from .modules.hardware_detection import HardwareFeature, detect_hardware

    HAS_HARDWARE_DETECTION = True
except ImportError:
    HAS_HARDWARE_DETECTION = False

try:
    from .modules.overclocking_control import TDP_PRESETS, OverclockingController

    HAS_OVERCLOCKING = True
except ImportError:
    HAS_OVERCLOCKING = False


class LinuxArmouryCLI:
    """Command-line interface for Linux Armoury"""

    def __init__(self):
        self.parser = self.create_parser()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description=(
                "Linux Armoury - Command-Line Control for "
                "ASUS ROG / ASUS gaming laptops"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --profile gaming       Apply gaming profile
  %(prog)s --refresh 180          Set refresh rate to 180Hz
  %(prog)s --status               Show current status
  %(prog)s --temperature          Show temperatures
  %(prog)s --monitor              Monitor system in real-time
  %(prog)s --gui                  Launch graphical interface

For more information, visit:
https://github.com/th3cavalry/Linux-Armoury
            """,
        )

        # Profile management
        parser.add_argument(
            "-p",
            "--profile",
            choices=list(Config.POWER_PROFILES.keys()),
            help="Apply power profile",
        )

        # Refresh rate
        parser.add_argument(
            "-r",
            "--refresh",
            type=int,
            choices=Config.SUPPORTED_REFRESH_RATES,
            help="Set refresh rate (Hz)",
        )

        # Status display
        parser.add_argument(
            "-s", "--status", action="store_true", help="Show current system status"
        )

        # Temperature
        parser.add_argument(
            "-t", "--temperature", action="store_true", help="Show temperature readings"
        )

        # Battery info
        parser.add_argument(
            "-b", "--battery", action="store_true", help="Show battery information"
        )

        # Monitor mode
        parser.add_argument(
            "-m",
            "--monitor",
            action="store_true",
            help="Monitor system in real-time (Ctrl+C to exit)",
        )

        # Launch GUI
        parser.add_argument(
            "-g", "--gui", action="store_true", help="Launch graphical interface"
        )

        # List profiles
        parser.add_argument(
            "-l", "--list", action="store_true", help="List available profiles"
        )

        # Hardware detection
        parser.add_argument(
            "--detect",
            action="store_true",
            help="Detect laptop model and supported features",
        )

        # Battery charge limit (new feature)
        parser.add_argument(
            "--charge-limit",
            type=int,
            choices=[60, 80, 100],
            metavar="PERCENT",
            help="Set battery charge limit (60, 80, or 100%%)",
        )

        # Fan control (new feature)
        parser.add_argument(
            "--fan", action="store_true", help="Show fan speed and temperatures"
        )

        # Keyboard backlight (new feature)
        parser.add_argument(
            "--kbd-brightness",
            type=int,
            metavar="LEVEL",
            help="Set keyboard backlight brightness (0-3)",
        )

        # Keyboard color (new feature)
        parser.add_argument(
            "--kbd-color",
            type=str,
            choices=[
                "red",
                "green",
                "blue",
                "white",
                "cyan",
                "magenta",
                "yellow",
                "orange",
                "purple",
                "pink",
            ],
            metavar="COLOR",
            help="Set keyboard RGB color",
        )

        # Display color settings (new feature)
        parser.add_argument(
            "--srgb-clamp",
            type=str,
            choices=["on", "off", "toggle"],
            metavar="STATE",
            help="Enable/disable sRGB gamut clamp (fixes over-saturated colors)",
        )

        parser.add_argument(
            "--color-profile",
            type=str,
            choices=["srgb", "adobe-rgb", "dci-p3"],
            metavar="PROFILE",
            help="Set color profile (sRGB, adobe-rgb, dci-p3)",
        )

        parser.add_argument(
            "--get-color-settings",
            action="store_true",
            help="Show current display color settings",
        )

        # Hardware capabilities
        parser.add_argument(
            "--capabilities",
            action="store_true",
            help="Show detected hardware capabilities",
        )

        # Overclocking - CPU Governor
        parser.add_argument(
            "--governor",
            type=str,
            metavar="GOV",
            help="Set CPU governor (e.g., performance, powersave, schedutil)",
        )

        # Overclocking - Turbo Boost
        parser.add_argument(
            "--turbo",
            type=str,
            choices=["on", "off"],
            metavar="STATE",
            help="Enable or disable CPU turbo boost",
        )

        # Overclocking - TDP preset
        parser.add_argument(
            "--tdp",
            type=str,
            choices=(
                list(TDP_PRESETS.keys())
                if HAS_OVERCLOCKING
                else [
                    "silent",
                    "balanced",
                    "performance",
                    "turbo",
                ]
            ),
            metavar="PRESET",
            help="Apply TDP preset (requires RyzenAdj)",
        )

        # Overclocking - Custom TDP
        parser.add_argument(
            "--tdp-custom",
            type=str,
            metavar="STAPM,FAST,SLOW",
            help="Set custom TDP values in watts (e.g., 25,35,25)",
        )

        # Overclocking - GPU performance level
        parser.add_argument(
            "--gpu-per",
            type=str,
            choices=["auto", "low", "high", "manual"],
            metavar="LEVEL",
            help="Set AMD GPU performance level",
        )

        # CPU/GPU info
        parser.add_argument(
            "--cpu-info",
            action="store_true",
            help="Show CPU frequency and governor information",
        )

        parser.add_argument(
            "--gpu-info", action="store_true", help="Show AMD GPU information"
        )

        # Verbose output
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Verbose output"
        )

        # Version
        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {Config.VERSION}"
        )

        return parser

    def apply_profile(self, profile: str) -> bool:
        """Apply a power profile"""
        # Try to get profile info if available in config, but don't fail if not
        profile_info = Config.POWER_PROFILES.get(profile)
        if profile_info:
            print(f"[*] Applying {profile_info['name']} profile...")
            if "tdp" in profile_info:
                print(f"[*]   Target TDP: {profile_info['tdp']}W")
        else:
            print(f"[*] Applying {profile} profile...")

        try:
            success, message = SystemUtils.set_power_profile(profile)

            if success:
                print(f"[+] {message}")

                # Optional: Set refresh rate if defined in profile
                # and we are not using pwrcfg
                if (
                    profile_info
                    and "refresh" in profile_info
                    and not SystemUtils.check_command_exists("pwrcfg")
                ):
                    rate = int(str(profile_info["refresh"]))
                    print(f"[*]   Setting refresh rate to {rate}Hz...")
                    r_success, r_msg = SystemUtils.set_refresh_rate(rate)
                    if r_success:
                        print("[+]   Refresh rate set")
                    else:
                        print(f"[-]   Could not set refresh rate: {r_msg}")

                return True
            else:
                print(f"[-] Failed to apply profile: {message}")
                return False

        except Exception as e:
            print(f"[-] Error: {e}")
            return False

    def set_refresh_rate(self, rate: int) -> bool:
        """Set display refresh rate"""
        print(f"[*] Setting refresh rate to {rate}Hz...")

        try:
            success, message = SystemUtils.set_refresh_rate(rate)

            if success:
                print(f"[+] {message}")
                return True
            else:
                print(f"[-] Failed to set refresh rate: {message}")
                return False

        except Exception as e:
            print(f"[-] Error: {e}")
            return False

    def show_status(self):
        """Show current system status"""
        print("=" * 60)
        print(f"  {Config.APP_NAME} v{Config.VERSION} - System Status")
        print("=" * 60)

        # Display info
        display = SystemUtils.get_primary_display()
        resolution = SystemUtils.get_display_resolution()
        refresh = SystemUtils.get_current_refresh_rate()

        print("\n📺 Display Information:")
        print(f"  Output: {display}")
        print(f"  Resolution: {resolution[0]}x{resolution[1]}")
        print(f"  Refresh Rate: {refresh}Hz" if refresh else "  Refresh Rate: Unknown")

        # Power info
        on_ac = SystemUtils.is_on_ac_power()
        battery = SystemUtils.get_battery_percentage()

        print("\n🔋 Power Information:")
        print(f"  Power Source: {'AC Adapter' if on_ac else 'Battery'}")
        if battery is not None:
            print(f"  Battery Level: {battery}%")

        # Temperature info
        cpu_temp = SystemUtils.get_cpu_temperature()
        gpu_temp = SystemUtils.get_gpu_temperature()

        print("\n🌡️  Temperature:")
        if cpu_temp:
            print(f"  CPU: {cpu_temp:.1f}°C")
        else:
            print("  CPU: N/A")

        if gpu_temp:
            print(f"  GPU: {gpu_temp:.1f}°C")
        else:
            print("  GPU: N/A")

        # TDP info
        tdp = SystemUtils.get_current_tdp()
        if tdp:
            print("\n⚡ Power Limits:")
            print(f"  Current TDP: {tdp}W")

        print()

    def show_temperature(self):
        """Show temperature readings"""
        cpu_temp = SystemUtils.get_cpu_temperature()
        gpu_temp = SystemUtils.get_gpu_temperature()

        print("\n🌡️  Temperature Readings:")
        print("-" * 40)

        if cpu_temp:
            status = (
                "❄️  Cool" if cpu_temp < 60 else "🔥 Warm" if cpu_temp < 80 else "🚨 Hot"
            )
            print(f"  CPU: {cpu_temp:.1f}°C  {status}")
        else:
            print("  CPU: Unable to read temperature")

        if gpu_temp:
            status = (
                "❄️  Cool" if gpu_temp < 60 else "🔥 Warm" if gpu_temp < 80 else "🚨 Hot"
            )
            print(f"  GPU: {gpu_temp:.1f}°C  {status}")
        else:
            print("  GPU: Unable to read temperature")

        print()

    def show_battery(self):
        """Show battery information"""
        battery = SystemUtils.get_battery_percentage()
        on_ac = SystemUtils.is_on_ac_power()

        print("\n🔋 Battery Information:")
        print("-" * 40)

        if battery is not None:
            # Battery level indicator
            if battery >= 80:
                icon = "████████"
            elif battery >= 60:
                icon = "██████  "
            elif battery >= 40:
                icon = "████    "
            elif battery >= 20:
                icon = "██      "
            else:
                icon = "▌       "

            print(f"  Level: {battery}% [{icon}]")
            print(f"  Status: {'Charging/Full' if on_ac else 'Discharging'}")

            # Battery health estimation
            if battery < 20 and not on_ac:
                print("  ⚠️  Warning: Low battery!")
        else:
            print("  Unable to read battery information")

        print()

    def list_profiles(self):
        """List available profiles"""
        print("\n⚡ Available Power Profiles:")
        print("=" * 70)

        for profile_id, info in Config.POWER_PROFILES.items():
            print(f"\n  {profile_id:12s} - {info['name']}")
            print(f"                 {info['description']}")

        print("\n" + "=" * 70)
        print(f"Apply a profile with: {sys.argv[0]} --profile <name>")
        print()

    def monitor_system(self):
        """Monitor system in real-time"""
        import time

        print("\n🔍 Real-time System Monitoring")
        print("   Press Ctrl+C to exit\n")
        print("-" * 60)

        try:
            iteration = 0
            while True:
                # Clear previous lines (simple version)
                print("\r" + " " * 80, end="")

                # Get current stats
                cpu_temp = SystemUtils.get_cpu_temperature()
                gpu_temp = SystemUtils.get_gpu_temperature()
                battery = SystemUtils.get_battery_percentage()
                on_ac = SystemUtils.is_on_ac_power()
                refresh = SystemUtils.get_current_refresh_rate()
                gaming = SystemUtils.detect_gaming_apps()

                # Display stats
                stats = []
                if cpu_temp:
                    temp_status = (
                        "🔥" if cpu_temp > 80 else "❄️" if cpu_temp < 60 else "🌡️"
                    )
                    stats.append(f"{temp_status} CPU: {cpu_temp:.1f}°C")
                if gpu_temp:
                    stats.append(f"GPU: {gpu_temp:.1f}°C")
                if battery is not None:
                    bat_icon = "🔋" if battery > 20 else "⚠️"
                    stats.append(f"{bat_icon} {battery}%")
                pwr_icon = "⚡" if on_ac else "🔋"
                stats.append(f"{pwr_icon} {'AC' if on_ac else 'BAT'}")
                if refresh:
                    stats.append(f"📺 {refresh}Hz")
                if gaming:
                    stats.append("🎮 GAMING")

                # Print with timestamp every 10 iterations
                if iteration % 10 == 0:
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{timestamp}] " + " | ".join(stats), flush=True)
                else:
                    print("\r" + " | ".join(stats), end="", flush=True)

                iteration += 1
                time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped")

    def launch_gui(self):
        """Launch the graphical interface"""
        print("Launching Linux Armoury GUI...")
        try:
            subprocess.run(["linux-armoury"])
        except FileNotFoundError:
            print("Error: GUI not found. Please install Linux Armoury first.")
            print("  ./install.sh")

    def detect_hardware(self):
        """Detect and display laptop hardware information"""
        print("\n🔍 Hardware Detection")
        print("=" * 70)

        # Laptop model detection
        model_info = SystemUtils.detect_laptop_model()
        if model_info:
            print("\n📱 Laptop Information:")
            print(f"  Vendor: {model_info.get('vendor', 'Unknown')}")
            print(f"  Model: {model_info.get('product', 'Unknown')}")
            print(f"  Version: {model_info.get('version', 'Unknown')}")
            if "board" in model_info:
                print(f"  Board: {model_info.get('board', 'Unknown')}")

        # ASUS detection
        is_asus = SystemUtils.is_asus_laptop()
        print(f"\n💻 ASUS Laptop: {'Yes ✓' if is_asus else 'No ✗'}")

        # Supported models
        print("\n📋 Supported Models:")
        supported = SystemUtils.get_supported_models()
        for i, model in enumerate(supported, 1):
            model_config = Config.SUPPORTED_MODELS.get(model, {})
            model_name = model_config.get("name", model)
            print(f"  {i}. {model} - {model_name}")

        # Current model match
        if model_info and "product" in model_info:
            product = model_info["product"]
            matched = False
            for model_id in supported:
                if model_id in product:
                    print(f"\n✓ Model Match: {model_id}")
                    config = Config.SUPPORTED_MODELS.get(model_id, {})
                    min_tdp = config.get("min_tdp", 10)
                    max_tdp = config.get("max_tdp", 90)
                    print(f"  TDP Range: {min_tdp}W - {max_tdp}W")
                    print(
                        f"  Resolution: {config.get('default_resolution', '2560x1600')}"
                    )
                    print(
                        f"  Refresh Rates: {config.get('supported_refresh_rates', [])}"
                    )
                    matched = True
                    break
            if not matched:
                print("\n⚠️  Model not in supported list (may still work)")

        # Feature availability
        print("\n🔧 Feature Availability:")
        pwrcfg_status = (
            "✓ Available"
            if SystemUtils.check_command_exists("pwrcfg")
            else "✗ Not found"
        )
        xrandr_status = (
            "✓ Available"
            if SystemUtils.check_command_exists("xrandr")
            else "✗ Not found"
        )
        sensors_status = (
            "✓ Available"
            if SystemUtils.check_command_exists("sensors")
            else "✗ Not found"
        )

        print(f"  pwrcfg: {pwrcfg_status}")
        print(f"  xrandr: {xrandr_status}")
        print(f"  sensors: {sensors_status}")

        # Display detection
        display = SystemUtils.get_primary_display()
        resolution = SystemUtils.get_display_resolution()
        refresh = SystemUtils.get_current_refresh_rate()
        print("\n📺 Display:")
        print(f"  Output: {display}")
        print(f"  Resolution: {resolution[0]}x{resolution[1]}")
        if refresh:
            print(f"  Refresh Rate: {refresh}Hz")

        print()

    def set_charge_limit(self, limit: int):
        """Set battery charge limit"""
        if not HAS_BATTERY_CONTROL:
            print("✗ Battery control module not available")
            return False

        battery = get_battery_controller()
        if not battery.is_supported():
            print("✗ Battery charge limit control not supported on this system")
            return False

        print(f"Setting battery charge limit to {limit}%...")
        success, message = battery.set_charge_limit(limit)

        if success:
            print(f"✓ {message}")
            return True
        else:
            print(f"✗ {message}")
            return False

    def show_fan_info(self):
        """Show fan speeds and temperatures"""
        if not HAS_FAN_CONTROL:
            print("✗ Fan control module not available")
            return

        fan = get_fan_controller()

        print("\n🌡️  Cooling Information")
        print("=" * 50)

        # Temperatures
        temps = fan.get_temperatures()
        cpu_temp = temps.get("cpu")
        gpu_temp = temps.get("gpu")

        print("\n  Temperatures:")
        if cpu_temp:
            status = (
                "❄️  Cool" if cpu_temp < 60 else "🔥 Warm" if cpu_temp < 80 else "🚨 Hot"
            )
            print(f"    CPU: {cpu_temp:.1f}°C  {status}")
        else:
            print("    CPU: N/A")

        if gpu_temp:
            status = (
                "❄️  Cool" if gpu_temp < 60 else "🔥 Warm" if gpu_temp < 80 else "🚨 Hot"
            )
            print(f"    GPU: {gpu_temp:.1f}°C  {status}")
        else:
            print("    GPU: N/A")

        # Fan speeds
        if fan.is_supported():
            fans = fan.get_all_fan_speeds()
            if fans:
                print("\n  Fan Speeds:")
                for fan_status in fans:
                    print(f"    {fan_status.name}: {fan_status.rpm} RPM")
        else:
            print("\n  Fan speed monitoring not available")

        print()

    def set_keyboard_brightness(self, level: int):
        """Set keyboard backlight brightness"""
        if not HAS_KEYBOARD_CONTROL:
            print("✗ Keyboard control module not available")
            return False

        kbd = get_keyboard_controller()
        if not kbd.is_supported():
            print("✗ Keyboard backlight not supported on this system")
            return False

        max_level = kbd.get_max_brightness()
        if level < 0 or level > max_level:
            print(f"✗ Invalid brightness level. Must be between 0 and {max_level}")
            return False

        print(f"Setting keyboard brightness to level {level}...")
        success, message = kbd.set_brightness(level)

        if success:
            print(f"✓ {message}")
            return True
        else:
            print(f"✗ {message}")
            return False

    def set_keyboard_color(self, color: str):
        """Set keyboard RGB color"""
        if not HAS_KEYBOARD_CONTROL:
            print("✗ Keyboard control module not available")
            return False

        kbd = get_keyboard_controller()
        if not kbd.has_rgb():
            print("✗ RGB keyboard control not supported on this system")
            return False

        print(f"Setting keyboard color to {color}...")
        success, message = kbd.set_preset_color(color)

        if success:
            print(f"✓ {message}")
            return True
        else:
            print(f"✗ {message}")
            return False

    def set_srgb_clamp(self, state: str):
        """Enable, disable, or toggle sRGB gamut clamp"""
        if state == "toggle":
            success, message = SystemUtils.toggle_srgb_clamp()
        else:
            enabled = state == "on"
            success, message = SystemUtils.set_srgb_clamp(enabled)

        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")

    def set_color_profile(self, profile: str):
        """Set color profile"""
        print(f"Setting color profile to {profile}...")
        success, message = SystemUtils.set_color_profile(profile)

        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")

    def show_color_settings(self):
        """Show current display color settings"""
        print("\n🎨 Display Color Settings")
        print("=" * 50)

        settings = SystemUtils.get_display_color_settings()
        print(f"  sRGB Gamut Clamp: {settings['srgb_clamp']}")
        print(f"  Color Profile: {settings['color_profile']}")
        print(f"  Available Profiles: {settings['available_profiles']}")

        print()

    # === Overclocking Methods ===

    def set_cpu_governor(self, governor: str):
        """Set CPU governor"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        available = oc.get_available_governors()

        if governor not in available:
            print(f"✗ Invalid governor '{governor}'")
            print(f"  Available: {', '.join(available)}")
            return

        if oc.set_cpu_governor(governor):
            print(f"✓ CPU governor set to {governor}")
        else:
            print("✗ Failed to set CPU governor")

    def set_turbo_boost(self, enabled: bool):
        """Enable or disable turbo boost"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        if oc.set_turbo_boost(enabled):
            print(f"✓ Turbo Boost {'enabled' if enabled else 'disabled'}")
        else:
            print("✗ Failed to change Turbo Boost setting")

    def apply_tdp_preset(self, preset_name: str):
        """Apply a TDP preset"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        if not oc.ryzenadj_available:
            print("✗ RyzenAdj not available")
            return

        if preset_name not in TDP_PRESETS:
            print(f"✗ Unknown preset '{preset_name}'")
            print(f"  Available: {', '.join(TDP_PRESETS.keys())}")
            return

        preset = TDP_PRESETS[preset_name]
        if oc.set_ryzenadj_tdp(
            stapm_limit=preset["stapm"],
            fast_limit=preset["fast"],
            slow_limit=preset["slow"],
        ):
            print(f"✓ Applied {preset_name} TDP preset:")
            print(f"    STAPM: {preset['stapm']}W")
            print(f"    Fast:  {preset['fast']}W")
            print(f"    Slow:  {preset['slow']}W")
        else:
            print("✗ Failed to apply TDP preset")

    def apply_custom_tdp(self, tdp_string: str):
        """Apply custom TDP values (STAPM,FAST,SLOW)"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        if not oc.ryzenadj_available:
            print("✗ RyzenAdj not available")
            return

        try:
            parts = tdp_string.split(",")
            if len(parts) != 3:
                raise ValueError("Need 3 values")
            stapm, fast, slow = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            print("✗ Invalid TDP format. Use: STAPM,FAST,SLOW (e.g., 25,35,25)")
            return

        if oc.set_ryzenadj_tdp(stapm_limit=stapm, fast_limit=fast, slow_limit=slow):
            print("✓ Applied custom TDP:")
            print(f"    STAPM: {stapm}W")
            print(f"    Fast:  {fast}W")
            print(f"    Slow:  {slow}W")
        else:
            print("✗ Failed to apply TDP settings")

    def set_gpu_perf_level(self, level: str):
        """Set AMD GPU performance level"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        if not oc.amd_gpu_path:
            print("✗ AMD GPU not detected")
            return

        if oc.set_gpu_performance_level(level):
            print(f"✓ GPU performance level set to {level}")
        else:
            print("✗ Failed to set GPU performance level")

    def show_cpu_info(self):
        """Display CPU information"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        info = oc.get_cpu_info()

        print("\n🔧 CPU Information")
        print("=" * 50)
        print(f"  Model:      {info.model}")
        print(f"  Cores:      {info.cores}")
        print(f"  Threads:    {info.threads}")
        print(f"  Frequency:  {info.current_freq_mhz:.0f} MHz")
        print(f"  Max Freq:   {info.max_freq_mhz:.0f} MHz")
        print(f"  Governor:   {info.governor}")
        print(f"  Turbo:      {'Enabled' if info.turbo_enabled else 'Disabled'}")

        if info.energy_perf_preference:
            print(f"  EPP:        {info.energy_perf_preference}")

        available_govs = oc.get_available_governors()
        if available_govs:
            print(f"\n  Available Governors: {', '.join(available_govs)}")

        epp_prefs = oc.get_available_energy_preferences()
        if epp_prefs:
            print(f"  Available EPP: {', '.join(epp_prefs)}")

        print("\n  Tools Available:")
        print(f"    cpupower:  {'Yes ✓' if oc.cpupower_available else 'No ✗'}")
        print(f"    RyzenAdj:  {'Yes ✓' if oc.ryzenadj_available else 'No ✗'}")
        print()

    def show_gpu_info(self):
        """Display AMD GPU information"""
        if not HAS_OVERCLOCKING:
            print("✗ Overclocking module not available")
            return

        oc = OverclockingController()
        if not oc.amd_gpu_path:
            print("✗ AMD GPU not detected")
            return

        info = oc.get_amd_gpu_info()
        if not info:
            print("✗ Could not read GPU information")
            return

        print("\n🎮 AMD GPU Information")
        print("=" * 50)
        print(f"  Name:         {info.name}")
        print(f"  Driver:       {info.driver}")
        print(f"  VRAM:         {info.vram_mb} MB")
        print(f"  GPU Clock:    {info.current_gpu_clock_mhz} MHz")
        print(f"  Memory Clock: {info.current_mem_clock_mhz} MHz")
        print(f"  Temperature:  {info.gpu_temp_c}°C")
        print(f"  Perf Level:   {info.power_level}")
        print(f"  Power Profile: {info.power_profile}")

        profiles = oc.get_gpu_power_profiles()
        if profiles:
            print("\n  Available Power Profiles:")
            for idx, name, is_active in profiles:
                active_mark = " *" if is_active else ""
                print(f"    {idx}: {name}{active_mark}")
        print()

    def show_capabilities(self):
        """Show detected hardware capabilities"""
        print("\n🔧 Hardware Capabilities")
        print("=" * 50)

        if HAS_HARDWARE_DETECTION:
            caps = detect_hardware()
            print("\n  System Information:")
            print(f"    ASUS Laptop: {'Yes ✓' if caps.is_asus_laptop else 'No'}")
            print(f"    Model: {caps.laptop_model or 'Unknown'}")
            print(f"    Kernel: {caps.kernel_version or 'Unknown'}")

            print("\n  Available Features:")
            features = {
                HardwareFeature.PLATFORM_PROFILE: "Platform Profile",
                HardwareFeature.CHARGE_CONTROL: "Battery Charge Control",
                HardwareFeature.KEYBOARD_BACKLIGHT: "Keyboard Backlight",
                HardwareFeature.KEYBOARD_RGB: "Keyboard RGB",
                HardwareFeature.FAN_CURVES: "Custom Fan Curves",
                HardwareFeature.GPU_MUX: "GPU MUX Switching",
                HardwareFeature.DGPU: "Discrete GPU",
                HardwareFeature.ANIME_MATRIX: "Anime Matrix",
                HardwareFeature.PANEL_OVERDRIVE: "Panel Overdrive",
            }

            for feature, name in features.items():
                available = feature in caps.features
                print(f"    {name}: {'✓ Yes' if available else '✗ No'}")

            print("\n  Daemon Status:")
            asusd_status = "✓ Running" if caps.asusd_available else "✗ Not running"
            supergfx_status = (
                "✓ Running" if caps.supergfxctl_available else "✗ Not running"
            )
            print(f"    asusd: {asusd_status}")
            print(f"    supergfxctl: {supergfx_status}")
        else:
            print("\n  Hardware detection module not available")

        # Check available control modules
        print("\n  Control Modules:")
        bat_status = "✓ Available" if HAS_BATTERY_CONTROL else "✗ Not installed"
        fan_status = "✓ Available" if HAS_FAN_CONTROL else "✗ Not installed"
        kbd_status = "✓ Available" if HAS_KEYBOARD_CONTROL else "✗ Not installed"
        oc_status = "✓ Available" if HAS_OVERCLOCKING else "✗ Not installed"
        print(f"    Battery Control: {bat_status}")
        print(f"    Fan Control: {fan_status}")
        print(f"    Keyboard Control: {kbd_status}")
        print(f"    Overclocking: {oc_status}")

        # Show overclocking tools if module available
        if HAS_OVERCLOCKING:
            oc = OverclockingController()
            print("\n  Overclocking Tools:")
            cpupower_status = (
                "✓ Available" if oc.cpupower_available else "✗ Not installed"
            )
            ryzenadj_status = (
                "✓ Available" if oc.ryzenadj_available else "✗ Not installed"
            )
            amd_status = "✓ Detected" if oc.amd_gpu_path else "✗ Not detected"
            print(f"    cpupower:  {cpupower_status}")
            print(f"    RyzenAdj:  {ryzenadj_status}")
            print(f"    AMD GPU:   {amd_status}")

        print()

    def run(self, args):
        """Run the CLI with given arguments"""
        # If no arguments, show help
        if len(sys.argv) == 1:
            self.parser.print_help()
            return

        args = self.parser.parse_args(args)

        # Handle commands
        if args.profile:
            self.apply_profile(args.profile)

        if args.refresh:
            self.set_refresh_rate(args.refresh)

        if args.status:
            self.show_status()

        if args.detect:
            self.detect_hardware()

        if args.temperature:
            self.show_temperature()

        if args.battery:
            self.show_battery()

        if args.list:
            self.list_profiles()

        if args.monitor:
            self.monitor_system()

        if args.gui:
            self.launch_gui()

        # New feature commands
        if args.charge_limit is not None:
            self.set_charge_limit(args.charge_limit)

        if args.fan:
            self.show_fan_info()

        if args.kbd_brightness is not None:
            self.set_keyboard_brightness(args.kbd_brightness)

        if args.kbd_color:
            self.set_keyboard_color(args.kbd_color)

        if args.srgb_clamp:
            self.set_srgb_clamp(args.srgb_clamp)

        if args.color_profile:
            self.set_color_profile(args.color_profile)

        if args.get_color_settings:
            self.show_color_settings()

        if args.capabilities:
            self.show_capabilities()

        # Overclocking commands
        if args.governor:
            self.set_cpu_governor(args.governor)

        if args.turbo:
            self.set_turbo_boost(args.turbo == "on")

        if args.tdp:
            self.apply_tdp_preset(args.tdp)

        if args.tdp_custom:
            self.apply_custom_tdp(args.tdp_custom)

        if args.gpu_per:
            self.set_gpu_perf_level(args.gpu_per)

        if args.cpu_info:
            self.show_cpu_info()

        if args.gpu_info:
            self.show_gpu_info()


def main():
    """Main entry point"""
    cli = LinuxArmouryCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
