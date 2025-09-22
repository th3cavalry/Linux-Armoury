"""
Utility functions for Linux Armoury
"""

import logging
import subprocess
import shutil
import os
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
from pathlib import Path
from typing import List, Optional, Tuple, Dict


def setup_logging():
    """Setup logging configuration"""
    log_dir = Path.home() / ".config" / "linux-armoury" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "linux-armoury.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def run_command(command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
    """Run a shell command and return success status and output"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(command, timeout=30)
            return result.returncode == 0, ""
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, f"Command not found: {command[0]}"
    except Exception as e:
        return False, str(e)


def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system"""
    return shutil.which(command) is not None


def is_asus_rog_device() -> bool:
    """Check if the current device is an ASUS ROG laptop"""
    try:
        # Check DMI information
        dmi_files = [
            "/sys/class/dmi/id/product_name",
            "/sys/class/dmi/id/board_name",
            "/sys/class/dmi/id/sys_vendor"
        ]
        
        for dmi_file in dmi_files:
            if Path(dmi_file).exists():
                with open(dmi_file, 'r') as f:
                    content = f.read().lower()
                    if 'asus' in content and any(keyword in content for keyword in ['rog', 'republic', 'gz302']):
                        return True
        
        return False
    except Exception:
        return False


def get_battery_info() -> Dict[str, any]:
    """Get battery information"""
    if not PSUTIL_AVAILABLE:
        # Fallback to manual battery reading
        try:
            # Try to read battery info from /sys/class/power_supply/
            battery_path = Path("/sys/class/power_supply/BAT0")
            if battery_path.exists():
                capacity = 100
                plugged = True
                
                capacity_file = battery_path / "capacity"
                if capacity_file.exists():
                    with open(capacity_file, 'r') as f:
                        capacity = int(f.read().strip())
                
                # Check AC adapter status
                for ac_path in Path("/sys/class/power_supply/").glob("A*"):
                    online_file = ac_path / "online"
                    if online_file.exists():
                        with open(online_file, 'r') as f:
                            plugged = f.read().strip() == "1"
                        break
                
                return {"percent": capacity, "plugged": plugged, "time_left": None}
        except Exception:
            pass
        
        return {"percent": 100, "plugged": True, "time_left": None}
    
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
            }
    except Exception:
        pass
    
    return {"percent": 0, "plugged": True, "time_left": None}


def get_cpu_info() -> Dict[str, any]:
    """Get CPU information"""
    if not PSUTIL_AVAILABLE:
        # Fallback CPU info reading
        usage = 0
        frequency = 0
        
        try:
            # Try to read CPU frequency
            freq_file = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
            if freq_file.exists():
                with open(freq_file, 'r') as f:
                    frequency = int(f.read().strip()) / 1000  # Convert to MHz
        except Exception:
            pass
        
        try:
            # Try to get CPU usage from /proc/stat (simplified)
            with open("/proc/stat", 'r') as f:
                line = f.readline()
                if line.startswith('cpu '):
                    values = line.split()[1:5]
                    idle = int(values[3])
                    total = sum(int(v) for v in values)
                    usage = 100 * (total - idle) / total if total > 0 else 0
        except Exception:
            pass
        
        return {
            "usage": usage,
            "frequency": frequency,
            "temperature": get_cpu_temperature()
        }
    
    try:
        return {
            "usage": psutil.cpu_percent(interval=1),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "temperature": get_cpu_temperature()
        }
    except Exception:
        return {"usage": 0, "frequency": 0, "temperature": 0}


def get_cpu_temperature() -> float:
    """Get CPU temperature"""
    try:
        # Try different temperature sources
        temp_files = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/hwmon/hwmon0/temp1_input",
            "/sys/class/hwmon/hwmon1/temp1_input"
        ]
        
        for temp_file in temp_files:
            if Path(temp_file).exists():
                with open(temp_file, 'r') as f:
                    temp = int(f.read().strip())
                    # Convert from millidegrees if necessary
                    if temp > 1000:
                        temp = temp / 1000
                    return temp
    except Exception:
        pass
    
    return 0.0


def get_memory_info() -> Dict[str, any]:
    """Get memory information"""
    if not PSUTIL_AVAILABLE:
        # Fallback memory info reading
        try:
            with open("/proc/meminfo", 'r') as f:
                meminfo = {}
                for line in f:
                    key, value = line.split(':')
                    meminfo[key.strip()] = int(value.split()[0]) * 1024  # Convert to bytes
                
                total = meminfo.get('MemTotal', 0)
                available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
                used = total - available
                percent = (used / total * 100) if total > 0 else 0
                
                return {
                    "total": total,
                    "used": used,
                    "available": available,
                    "percent": percent
                }
        except Exception:
            pass
        
        return {"total": 8589934592, "used": 4294967296, "available": 4294967296, "percent": 50}
    
    try:
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "used": memory.used,
            "available": memory.available,
            "percent": memory.percent
        }
    except Exception:
        return {"total": 0, "used": 0, "available": 0, "percent": 0}


def create_desktop_entry(autostart: bool = False):
    """Create desktop entry for the application"""
    desktop_content = f"""[Desktop Entry]
Name=Linux Armoury
Comment=ASUS ROG Laptop Control GUI
Exec=linux-armoury
Icon=linux-armoury
Terminal=false
Type=Application
Categories=System;Settings;HardwareSettings;
StartupNotify=true
X-GNOME-Autostart-enabled={"true" if autostart else "false"}
"""
    
    # Create desktop entry
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = desktop_dir / "linux-armoury.desktop"
    with open(desktop_file, 'w') as f:
        f.write(desktop_content)
    
    # Make executable
    os.chmod(desktop_file, 0o755)
    
    # Create autostart entry if requested
    if autostart:
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        autostart_file = autostart_dir / "linux-armoury.desktop"
        with open(autostart_file, 'w') as f:
            f.write(desktop_content)
        
        os.chmod(autostart_file, 0o755)


def remove_autostart():
    """Remove autostart desktop entry"""
    autostart_file = Path.home() / ".config" / "autostart" / "linux-armoury.desktop"
    if autostart_file.exists():
        autostart_file.unlink()


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds is None:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"