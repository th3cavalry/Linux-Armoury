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
import sys
import subprocess
from typing import Optional
from config import Config
from system_utils import SystemUtils


class LinuxArmouryCLI:
    """Command-line interface for Linux Armoury"""
    
    def __init__(self):
        self.parser = self.create_parser()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='Linux Armoury - Command-Line Control for ASUS GZ302EA',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  %(prog)s --profile gaming       Apply gaming profile
  %(prog)s --refresh 180          Set refresh rate to 180Hz
  %(prog)s --status               Show current status
  %(prog)s --temperature          Show temperatures
  %(prog)s --monitor              Monitor system in real-time
  %(prog)s --gui                  Launch graphical interface

For more information, visit:
https://github.com/th3cavalry/Linux-Armoury
            '''
        )
        
        # Profile management
        parser.add_argument(
            '-p', '--profile',
            choices=list(Config.POWER_PROFILES.keys()),
            help='Apply power profile'
        )
        
        # Refresh rate
        parser.add_argument(
            '-r', '--refresh',
            type=int,
            choices=Config.SUPPORTED_REFRESH_RATES,
            help='Set refresh rate (Hz)'
        )
        
        # Status display
        parser.add_argument(
            '-s', '--status',
            action='store_true',
            help='Show current system status'
        )
        
        # Temperature
        parser.add_argument(
            '-t', '--temperature',
            action='store_true',
            help='Show temperature readings'
        )
        
        # Battery info
        parser.add_argument(
            '-b', '--battery',
            action='store_true',
            help='Show battery information'
        )
        
        # Monitor mode
        parser.add_argument(
            '-m', '--monitor',
            action='store_true',
            help='Monitor system in real-time (Ctrl+C to exit)'
        )
        
        # Launch GUI
        parser.add_argument(
            '-g', '--gui',
            action='store_true',
            help='Launch graphical interface'
        )
        
        # List profiles
        parser.add_argument(
            '-l', '--list',
            action='store_true',
            help='List available profiles'
        )
        
        # Hardware detection
        parser.add_argument(
            '--detect',
            action='store_true',
            help='Detect laptop model and supported features'
        )
        
        # Verbose output
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output'
        )
        
        # Version
        parser.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {Config.VERSION}'
        )
        
        return parser
    
    def apply_profile(self, profile: str) -> bool:
        """Apply a power profile"""
        profile_info = Config.POWER_PROFILES.get(profile)
        if not profile_info:
            print(f"Error: Unknown profile '{profile}'")
            return False
        
        print(f"Applying {profile_info['name']} profile...")
        print(f"  TDP: {profile_info['tdp']}W")
        print(f"  Refresh Rate: {profile_info['refresh']}Hz")
        
        # Apply profile using pwrcfg
        if not SystemUtils.check_command_exists('pwrcfg'):
            print("\nError: pwrcfg command not found!")
            print("Please install GZ302-Linux-Setup tools:")
            print("  https://github.com/th3cavalry/GZ302-Linux-Setup")
            return False
        
        try:
            result = subprocess.run(
                ['pkexec', 'pwrcfg', profile],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ Profile applied successfully!")
                return True
            else:
                print(f"✗ Failed to apply profile: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Command timed out")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def set_refresh_rate(self, rate: int) -> bool:
        """Set display refresh rate"""
        print(f"Setting refresh rate to {rate}Hz...")
        
        display = SystemUtils.get_primary_display()
        resolution = SystemUtils.get_display_resolution()
        
        try:
            result = subprocess.run(
                [
                    'pkexec', 'xrandr',
                    '--output', display,
                    '--mode', f"{resolution[0]}x{resolution[1]}",
                    '--rate', str(rate)
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ Refresh rate set to {rate}Hz")
                return True
            else:
                print(f"✗ Failed to set refresh rate: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
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
        
        print(f"\n📺 Display Information:")
        print(f"  Output: {display}")
        print(f"  Resolution: {resolution[0]}x{resolution[1]}")
        print(f"  Refresh Rate: {refresh}Hz" if refresh else "  Refresh Rate: Unknown")
        
        # Power info
        on_ac = SystemUtils.is_on_ac_power()
        battery = SystemUtils.get_battery_percentage()
        
        print(f"\n🔋 Power Information:")
        print(f"  Power Source: {'AC Adapter' if on_ac else 'Battery'}")
        if battery is not None:
            print(f"  Battery Level: {battery}%")
        
        # Temperature info
        cpu_temp = SystemUtils.get_cpu_temperature()
        gpu_temp = SystemUtils.get_gpu_temperature()
        
        print(f"\n🌡️  Temperature:")
        if cpu_temp:
            print(f"  CPU: {cpu_temp:.1f}°C")
        else:
            print(f"  CPU: N/A")
            
        if gpu_temp:
            print(f"  GPU: {gpu_temp:.1f}°C")
        else:
            print(f"  GPU: N/A")
        
        # TDP info
        tdp = SystemUtils.get_current_tdp()
        if tdp:
            print(f"\n⚡ Power Limits:")
            print(f"  Current TDP: {tdp}W")
        
        print()
    
    def show_temperature(self):
        """Show temperature readings"""
        cpu_temp = SystemUtils.get_cpu_temperature()
        gpu_temp = SystemUtils.get_gpu_temperature()
        
        print("\n🌡️  Temperature Readings:")
        print("-" * 40)
        
        if cpu_temp:
            status = "❄️  Cool" if cpu_temp < 60 else "🔥 Warm" if cpu_temp < 80 else "🚨 Hot"
            print(f"  CPU: {cpu_temp:.1f}°C  {status}")
        else:
            print(f"  CPU: Unable to read temperature")
            
        if gpu_temp:
            status = "❄️  Cool" if gpu_temp < 60 else "🔥 Warm" if gpu_temp < 80 else "🚨 Hot"
            print(f"  GPU: {gpu_temp:.1f}°C  {status}")
        else:
            print(f"  GPU: Unable to read temperature")
        
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
                print(f"  ⚠️  Warning: Low battery!")
        else:
            print(f"  Unable to read battery information")
        
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
                    temp_status = "🔥" if cpu_temp > 80 else "❄️" if cpu_temp < 60 else "🌡️"
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
                    stats.append(f"🎮 GAMING")
                
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
            subprocess.run(['linux-armoury'])
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
            print(f"\n📱 Laptop Information:")
            print(f"  Vendor: {model_info.get('vendor', 'Unknown')}")
            print(f"  Model: {model_info.get('product', 'Unknown')}")
            print(f"  Version: {model_info.get('version', 'Unknown')}")
            if 'board' in model_info:
                print(f"  Board: {model_info.get('board', 'Unknown')}")
        
        # ASUS detection
        is_asus = SystemUtils.is_asus_laptop()
        print(f"\n💻 ASUS Laptop: {'Yes ✓' if is_asus else 'No ✗'}")
        
        # Supported models
        print(f"\n📋 Supported Models:")
        supported = SystemUtils.get_supported_models()
        for i, model in enumerate(supported, 1):
            model_config = Config.SUPPORTED_MODELS.get(model, {})
            model_name = model_config.get('name', model)
            print(f"  {i}. {model} - {model_name}")
        
        # Current model match
        if model_info and 'product' in model_info:
            product = model_info['product']
            matched = False
            for model_id in supported:
                if model_id in product:
                    print(f"\n✓ Model Match: {model_id}")
                    config = Config.SUPPORTED_MODELS.get(model_id, {})
                    print(f"  TDP Range: {config.get('min_tdp', 10)}W - {config.get('max_tdp', 90)}W")
                    print(f"  Resolution: {config.get('default_resolution', '2560x1600')}")
                    print(f"  Refresh Rates: {config.get('supported_refresh_rates', [])}")
                    matched = True
                    break
            if not matched:
                print(f"\n⚠️  Model not in supported list (may still work)")
        
        # Feature availability
        print(f"\n🔧 Feature Availability:")
        print(f"  pwrcfg: {'✓ Available' if SystemUtils.check_command_exists('pwrcfg') else '✗ Not found'}")
        print(f"  xrandr: {'✓ Available' if SystemUtils.check_command_exists('xrandr') else '✗ Not found'}")
        print(f"  sensors: {'✓ Available' if SystemUtils.check_command_exists('sensors') else '✗ Not found'}")
        
        # Display detection
        display = SystemUtils.get_primary_display()
        resolution = SystemUtils.get_display_resolution()
        refresh = SystemUtils.get_current_refresh_rate()
        print(f"\n📺 Display:")
        print(f"  Output: {display}")
        print(f"  Resolution: {resolution[0]}x{resolution[1]}")
        if refresh:
            print(f"  Refresh Rate: {refresh}Hz")
        
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


def main():
    """Main entry point"""
    cli = LinuxArmouryCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
