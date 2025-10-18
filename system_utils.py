#!/usr/bin/env python3
"""
System utilities for hardware detection and monitoring
"""

import subprocess
import os
import re
from typing import Optional, Dict, List, Tuple


class SystemUtils:
    """System utility functions for hardware detection and monitoring"""
    
    @staticmethod
    def get_primary_display() -> str:
        """
        Auto-detect the primary display output name.
        
        Returns:
            str: Display output name (e.g., 'eDP-1', 'eDP-2')
        """
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Look for connected displays
            for line in result.stdout.split('\n'):
                # First try to find primary display
                if ' connected primary' in line:
                    return line.split()[0]
            
            # If no primary, find first connected display
            for line in result.stdout.split('\n'):
                if ' connected' in line and 'disconnected' not in line:
                    return line.split()[0]
                    
        except Exception as e:
            print(f"Error detecting display: {e}")
        
        # Fallback to common default
        return "eDP-1"
    
    @staticmethod
    def get_display_resolution() -> Tuple[int, int]:
        """
        Get current display resolution.
        
        Returns:
            Tuple[int, int]: (width, height)
        """
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if '*' in line:  # Current resolution marked with *
                    match = re.search(r'(\d+)x(\d+)', line)
                    if match:
                        return (int(match.group(1)), int(match.group(2)))
                        
        except Exception as e:
            print(f"Error getting resolution: {e}")
        
        return (2560, 1600)  # Default for GZ302EA
    
    @staticmethod
    def get_current_refresh_rate() -> Optional[int]:
        """
        Get current display refresh rate.
        
        Returns:
            Optional[int]: Refresh rate in Hz
        """
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if '*' in line:  # Current mode
                    match = re.search(r'(\d+\.\d+)\*', line)
                    if match:
                        return int(float(match.group(1)))
                        
        except Exception as e:
            print(f"Error getting refresh rate: {e}")
        
        return None
    
    @staticmethod
    def get_cpu_temperature() -> Optional[float]:
        """
        Get CPU temperature from hwmon.
        
        Returns:
            Optional[float]: Temperature in Celsius
        """
        try:
            # Try different hwmon paths
            hwmon_paths = [
                "/sys/class/hwmon/hwmon0/temp1_input",
                "/sys/class/hwmon/hwmon1/temp1_input",
                "/sys/class/hwmon/hwmon2/temp1_input",
                "/sys/class/hwmon/hwmon3/temp1_input",
            ]
            
            for path in hwmon_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        # Temperature in millidegrees
                        temp = int(f.read().strip()) / 1000.0
                        if 0 < temp < 150:  # Sanity check
                            return temp
                            
            # Try sensors command if available
            result = subprocess.run(
                ["sensors", "-A"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Tctl' in line or 'CPU' in line:
                        match = re.search(r'(\d+\.\d+)°C', line)
                        if match:
                            return float(match.group(1))
                            
        except Exception as e:
            print(f"Error reading temperature: {e}")
        
        return None
    
    @staticmethod
    def get_gpu_temperature() -> Optional[float]:
        """
        Get GPU temperature.
        
        Returns:
            Optional[float]: Temperature in Celsius
        """
        try:
            # For AMD integrated graphics
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'edge' in line.lower() or 'gpu' in line.lower():
                        match = re.search(r'(\d+\.\d+)°C', line)
                        if match:
                            return float(match.group(1))
                            
        except Exception as e:
            print(f"Error reading GPU temperature: {e}")
        
        return None
    
    @staticmethod
    def is_on_ac_power() -> bool:
        """
        Check if system is running on AC power.
        
        Returns:
            bool: True if on AC power, False if on battery
        """
        try:
            # Check via /sys/class/power_supply
            ac_online_path = "/sys/class/power_supply/AC/online"
            if os.path.exists(ac_online_path):
                with open(ac_online_path, 'r') as f:
                    return f.read().strip() == '1'
            
            # Alternative paths
            for power_supply in os.listdir("/sys/class/power_supply"):
                path = f"/sys/class/power_supply/{power_supply}/online"
                if os.path.exists(path) and 'AC' in power_supply:
                    with open(path, 'r') as f:
                        return f.read().strip() == '1'
                        
        except Exception as e:
            print(f"Error checking AC power: {e}")
        
        return True  # Assume AC as safe default
    
    @staticmethod
    def get_battery_percentage() -> Optional[int]:
        """
        Get battery charge percentage.
        
        Returns:
            Optional[int]: Battery percentage (0-100)
        """
        try:
            for power_supply in os.listdir("/sys/class/power_supply"):
                if 'BAT' in power_supply:
                    capacity_path = f"/sys/class/power_supply/{power_supply}/capacity"
                    if os.path.exists(capacity_path):
                        with open(capacity_path, 'r') as f:
                            return int(f.read().strip())
                            
        except Exception as e:
            print(f"Error reading battery: {e}")
        
        return None
    
    @staticmethod
    def get_current_tdp() -> Optional[int]:
        """
        Get current TDP limit (requires ryzenadj or similar).
        
        Returns:
            Optional[int]: TDP in Watts
        """
        try:
            # Try ryzenadj if available
            result = subprocess.run(
                ["ryzenadj", "-i"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'STAPM LIMIT' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            return int(match.group(1))
                            
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def check_command_exists(command: str) -> bool:
        """
        Check if a command exists in PATH.
        
        Args:
            command: Command name to check
            
        Returns:
            bool: True if command exists
        """
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    
    @staticmethod
    def get_running_processes() -> List[str]:
        """
        Get list of running process names.
        
        Returns:
            List[str]: Process names
        """
        try:
            result = subprocess.run(
                ["ps", "-eo", "comm"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                processes = result.stdout.split('\n')[1:]  # Skip header
                return [p.strip() for p in processes if p.strip()]
                
        except Exception as e:
            print(f"Error getting processes: {e}")
        
        return []
    
    @staticmethod
    def detect_gaming_apps() -> bool:
        """
        Detect if any gaming applications are running.
        
        Returns:
            bool: True if gaming app detected
        """
        gaming_apps = [
            'steam', 'lutris', 'heroic', 'bottles',
            'wine', 'proton', 'gamemoded', 'gamemode',
            'minecraft', 'dotnet'
        ]
        
        processes = SystemUtils.get_running_processes()
        process_lower = [p.lower() for p in processes]
        
        for game_app in gaming_apps:
            if any(game_app in p for p in process_lower):
                return True
        
        return False
