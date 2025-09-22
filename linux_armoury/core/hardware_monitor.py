"""
Hardware monitoring module for Linux Armoury
Enhanced system monitoring inspired by ROG Control Center and G-Helper
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess
import re

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from linux_armoury.core.utils import run_command, check_command_exists


class TemperatureMonitor:
    """Enhanced temperature monitoring with multiple sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_sources = self._discover_temperature_sources()
        
    def _discover_temperature_sources(self) -> Dict[str, str]:
        """Discover available temperature sources"""
        sources = {}
        
        # Check hwmon
        hwmon_path = Path("/sys/class/hwmon")
        if hwmon_path.exists():
            for hwmon in hwmon_path.iterdir():
                if hwmon.is_dir():
                    name_file = hwmon / "name"
                    if name_file.exists():
                        try:
                            name = name_file.read_text().strip()
                            sources[name] = str(hwmon)
                        except Exception:
                            continue
        
        # Check thermal zones
        thermal_path = Path("/sys/class/thermal")
        if thermal_path.exists():
            for zone in thermal_path.glob("thermal_zone*"):
                type_file = zone / "type"
                if type_file.exists():
                    try:
                        zone_type = type_file.read_text().strip()
                        sources[f"thermal_{zone_type}"] = str(zone)
                    except Exception:
                        continue
        
        return sources
    
    def get_temperatures(self) -> Dict[str, float]:
        """Get temperatures from all available sources"""
        temps = {}
        
        # Use psutil if available
        if PSUTIL_AVAILABLE:
            try:
                sensor_temps = psutil.sensors_temperatures()
                for name, sensors in sensor_temps.items():
                    for sensor in sensors:
                        key = f"{name}_{sensor.label}" if sensor.label else name
                        temps[key] = sensor.current
            except Exception as e:
                self.logger.debug(f"psutil temperature failed: {e}")
        
        # Manual hwmon reading for additional sources
        for name, path in self.temp_sources.items():
            try:
                hwmon_path = Path(path)
                for temp_file in hwmon_path.glob("temp*_input"):
                    temp_value = int(temp_file.read_text().strip()) / 1000.0
                    temps[f"{name}_{temp_file.stem}"] = temp_value
            except Exception:
                continue
        
        return temps
    
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature specifically"""
        temps = self.get_temperatures()
        
        # Priority order for CPU temperature sources
        cpu_keys = [
            "coretemp_Package id 0",
            "coretemp_Core 0",
            "k10temp_Tctl",
            "acpi_ACPI thermal zone",
            "thermal_x86_pkg_temp"
        ]
        
        for key in cpu_keys:
            if key in temps:
                return temps[key]
        
        # Fallback to any temperature that might be CPU
        for key, temp in temps.items():
            if any(term in key.lower() for term in ["cpu", "core", "pkg", "tctl"]):
                return temp
        
        return None


class FanController:
    """Fan control manager inspired by ROG Control Center"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fan_sources = self._discover_fan_sources()
        self.asus_control_available = check_command_exists("asusctl")
        
    def _discover_fan_sources(self) -> Dict[str, str]:
        """Discover available fan control sources"""
        sources = {}
        
        # Check hwmon for fan controls
        hwmon_path = Path("/sys/class/hwmon")
        if hwmon_path.exists():
            for hwmon in hwmon_path.iterdir():
                if hwmon.is_dir():
                    # Look for fan control files
                    if list(hwmon.glob("pwm*")):
                        name_file = hwmon / "name"
                        name = "unknown"
                        if name_file.exists():
                            try:
                                name = name_file.read_text().strip()
                            except Exception:
                                pass
                        sources[name] = str(hwmon)
        
        return sources
    
    def get_fan_speeds(self) -> Dict[str, int]:
        """Get current fan speeds (RPM)"""
        speeds = {}
        
        # Use psutil if available
        if PSUTIL_AVAILABLE:
            try:
                fans = psutil.sensors_fans()
                for name, fan_list in fans.items():
                    for i, fan in enumerate(fan_list):
                        key = f"{name}_fan{i}" if len(fan_list) > 1 else name
                        speeds[key] = fan.current
            except Exception as e:
                self.logger.debug(f"psutil fan reading failed: {e}")
        
        # Manual hwmon reading
        for name, path in self.fan_sources.items():
            try:
                hwmon_path = Path(path)
                for fan_file in hwmon_path.glob("fan*_input"):
                    fan_rpm = int(fan_file.read_text().strip())
                    speeds[f"{name}_{fan_file.stem}"] = fan_rpm
            except Exception:
                continue
        
        return speeds
    
    def get_fan_curves(self) -> Dict[str, List[Tuple[int, int]]]:
        """Get current fan curves (temp, speed) points"""
        if self.asus_control_available:
            success, output = run_command(["asusctl", "fan-curve", "-g"])
            if success:
                # Parse fan curve data from asusctl output
                return self._parse_fan_curve_output(output)
        
        return {}
    
    def set_fan_curve(self, profile: str, curve_data: List[Tuple[int, int]]) -> bool:
        """Set fan curve for a profile"""
        if not self.asus_control_available:
            return False
        
        try:
            # Convert curve data to asusctl format
            curve_str = ",".join([f"{temp}c:{speed}%" for temp, speed in curve_data])
            success, _ = run_command(["asusctl", "fan-curve", "-p", profile, "-s", curve_str])
            return success
        except Exception as e:
            self.logger.error(f"Failed to set fan curve: {e}")
            return False
    
    def set_manual_fan_speed(self, fan_id: str, speed_percent: int) -> bool:
        """Set manual fan speed (0-100%)"""
        if not self.asus_control_available:
            return False
        
        try:
            success, _ = run_command(["asusctl", "fan-curve", "-m", str(speed_percent)])
            return success
        except Exception as e:
            self.logger.error(f"Failed to set manual fan speed: {e}")
            return False
    
    def _parse_fan_curve_output(self, output: str) -> Dict[str, List[Tuple[int, int]]]:
        """Parse fan curve output from asusctl"""
        curves = {}
        current_profile = None
        
        for line in output.split('\n'):
            line = line.strip()
            if 'Profile:' in line:
                current_profile = line.split(':')[-1].strip()
                curves[current_profile] = []
            elif current_profile and re.match(r'\d+c:\d+%', line):
                # Parse temperature:speed pairs
                temp_speed = line.split(':')
                temp = int(temp_speed[0].replace('c', ''))
                speed = int(temp_speed[1].replace('%', ''))
                curves[current_profile].append((temp, speed))
        
        return curves


class PerformanceMonitor:
    """Enhanced performance monitoring with historical data"""
    
    def __init__(self, history_size: int = 100):
        self.logger = logging.getLogger(__name__)
        self.history_size = history_size
        self.cpu_history = []
        self.memory_history = []
        self.gpu_history = []
        self.temp_history = []
        self.temp_monitor = TemperatureMonitor()
        
    def update_metrics(self):
        """Update all performance metrics"""
        if not PSUTIL_AVAILABLE:
            return
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()
        cpu_temp = self.temp_monitor.get_cpu_temperature()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # GPU metrics (if nvidia-smi available)
        gpu_data = self._get_gpu_metrics()
        
        # Store history
        timestamp = time.time()
        
        self.cpu_history.append({
            'timestamp': timestamp,
            'percent': cpu_percent,
            'frequency': cpu_freq.current if cpu_freq else 0,
            'temperature': cpu_temp or 0
        })
        
        self.memory_history.append({
            'timestamp': timestamp,
            'percent': memory.percent,
            'used': memory.used,
            'available': memory.available
        })
        
        if gpu_data:
            self.gpu_history.append({
                'timestamp': timestamp,
                **gpu_data
            })
        
        # Trim history
        if len(self.cpu_history) > self.history_size:
            self.cpu_history.pop(0)
        if len(self.memory_history) > self.history_size:
            self.memory_history.pop(0)
        if len(self.gpu_history) > self.history_size:
            self.gpu_history.pop(0)
    
    def _get_gpu_metrics(self) -> Optional[Dict]:
        """Get GPU metrics if available"""
        if check_command_exists("nvidia-smi"):
            success, output = run_command([
                "nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits"
            ])
            if success:
                try:
                    values = output.strip().split(',')
                    return {
                        'utilization': float(values[0]),
                        'memory_used': float(values[1]),
                        'memory_total': float(values[2]),
                        'temperature': float(values[3])
                    }
                except Exception:
                    pass
        
        return None
    
    def get_historical_data(self, metric: str, duration_minutes: int = 5) -> List[Dict]:
        """Get historical data for a specific metric"""
        cutoff_time = time.time() - (duration_minutes * 60)
        
        if metric == 'cpu':
            return [d for d in self.cpu_history if d['timestamp'] > cutoff_time]
        elif metric == 'memory':
            return [d for d in self.memory_history if d['timestamp'] > cutoff_time]
        elif metric == 'gpu':
            return [d for d in self.gpu_history if d['timestamp'] > cutoff_time]
        
        return []
    
    def get_current_stats(self) -> Dict:
        """Get current performance statistics"""
        stats = {
            'cpu': None,
            'memory': None,
            'gpu': None,
            'temperatures': self.temp_monitor.get_temperatures(),
            'fans': {}
        }
        
        if self.cpu_history:
            stats['cpu'] = self.cpu_history[-1]
        
        if self.memory_history:
            stats['memory'] = self.memory_history[-1]
        
        if self.gpu_history:
            stats['gpu'] = self.gpu_history[-1]
        
        # Get fan speeds
        fan_controller = FanController()
        stats['fans'] = fan_controller.get_fan_speeds()
        
        return stats


class BatteryHealthManager:
    """Battery health management inspired by Armoury Crate"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asus_control_available = check_command_exists("asusctl")
        
    def get_charge_limit(self) -> Optional[int]:
        """Get current battery charge limit"""
        if self.asus_control_available:
            success, output = run_command(["asusctl", "battery", "--get"])
            if success:
                # Parse charge limit from output
                for line in output.split('\n'):
                    if 'charge_control_end_threshold' in line:
                        try:
                            return int(line.split(':')[-1].strip())
                        except ValueError:
                            pass
        
        return None
    
    def set_charge_limit(self, limit: int) -> bool:
        """Set battery charge limit (20-100%)"""
        if not self.asus_control_available:
            return False
        
        if not 20 <= limit <= 100:
            self.logger.error(f"Invalid charge limit: {limit}%. Must be between 20-100%")
            return False
        
        try:
            success, _ = run_command(["asusctl", "battery", f"--set-limit", str(limit)])
            return success
        except Exception as e:
            self.logger.error(f"Failed to set charge limit: {e}")
            return False
    
    def get_battery_health_info(self) -> Dict:
        """Get comprehensive battery health information"""
        info = {
            'charge_limit': self.get_charge_limit(),
            'health_percentage': None,
            'cycle_count': None,
            'design_capacity': None,
            'current_capacity': None
        }
        
        if PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    info.update({
                        'current_percent': battery.percent,
                        'charging': battery.power_plugged,
                        'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                    })
            except Exception:
                pass
        
        # Try to get additional battery info from ACPI
        try:
            acpi_path = Path("/sys/class/power_supply/BAT0")
            if acpi_path.exists():
                cycle_count_file = acpi_path / "cycle_count"
                if cycle_count_file.exists():
                    info['cycle_count'] = int(cycle_count_file.read_text().strip())
                
                design_capacity_file = acpi_path / "energy_full_design"
                current_capacity_file = acpi_path / "energy_full"
                if design_capacity_file.exists() and current_capacity_file.exists():
                    design = int(design_capacity_file.read_text().strip())
                    current = int(current_capacity_file.read_text().strip())
                    info['design_capacity'] = design
                    info['current_capacity'] = current
                    if design > 0:
                        info['health_percentage'] = round((current / design) * 100, 1)
        except Exception:
            pass
        
        return info