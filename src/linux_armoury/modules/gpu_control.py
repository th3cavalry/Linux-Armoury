#!/usr/bin/env python3
"""
GPU Control Module for Linux Armoury
Provides GPU switching via supergfxctl and live GPU stats monitoring.
"""

import subprocess
import re
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum


class GpuMode(Enum):
    """GPU switching modes supported by supergfxctl"""
    HYBRID = "Hybrid"
    INTEGRATED = "Integrated"
    VFIO = "Vfio"
    ASUS_EGPU = "AsusEgpu"
    ASUS_MUX_DGPU = "AsusMuxDgpu"
    
    @classmethod
    def from_string(cls, s: str) -> Optional['GpuMode']:
        """Convert string to GpuMode"""
        s_lower = s.lower().strip()
        for mode in cls:
            if mode.value.lower() == s_lower:
                return mode
        return None


class GpuPowerStatus(Enum):
    """dGPU power status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    OFF = "off"
    UNKNOWN = "unknown"


@dataclass
class GpuLiveStats:
    """Live GPU statistics"""
    # GPU identification
    gpu_name: str = "Unknown"
    vendor: str = "Unknown"
    driver: str = "Unknown"
    
    # Clock speeds (MHz)
    gpu_clock_mhz: int = 0
    mem_clock_mhz: int = 0
    gpu_clock_max_mhz: int = 0
    mem_clock_max_mhz: int = 0
    
    # Usage percentages
    gpu_usage_percent: int = 0
    mem_usage_percent: int = 0
    encoder_usage_percent: int = 0
    decoder_usage_percent: int = 0
    
    # Memory (MB)
    vram_total_mb: int = 0
    vram_used_mb: int = 0
    vram_free_mb: int = 0
    
    # Temperature (Celsius)
    gpu_temp_c: int = 0
    junction_temp_c: int = 0
    mem_temp_c: int = 0
    
    # Power (Watts)
    power_draw_w: float = 0.0
    power_limit_w: float = 0.0
    
    # Fan
    fan_speed_rpm: int = 0
    fan_speed_percent: int = 0
    
    # Performance state
    performance_level: str = "auto"
    power_profile: str = "default"


@dataclass
class GpuSwitchingStatus:
    """GPU switching status from supergfxctl"""
    available: bool = False
    current_mode: Optional[GpuMode] = None
    supported_modes: List[GpuMode] = field(default_factory=list)
    dgpu_vendor: str = "Unknown"
    power_status: GpuPowerStatus = GpuPowerStatus.UNKNOWN
    pending_action: str = ""
    pending_mode: Optional[GpuMode] = None
    requires_logout: bool = False
    requires_reboot: bool = False


class GpuController:
    """Controls GPU switching and monitors GPU stats"""
    
    def __init__(self):
        self.supergfxctl_available = self._check_supergfxctl()
        self.nvidia_available = self._check_nvidia()
        self.amd_gpu_path = self._find_amd_gpu()
        self.intel_gpu_path = self._find_intel_gpu()
        
    def _check_supergfxctl(self) -> bool:
        """Check if supergfxctl is installed and running"""
        try:
            result = subprocess.run(
                ["supergfxctl", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_nvidia(self) -> bool:
        """Check if NVIDIA GPU and nvidia-smi are available"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _find_amd_gpu(self) -> Optional[str]:
        """Find AMD GPU sysfs path"""
        try:
            for card in os.listdir("/sys/class/drm"):
                if card.startswith("card") and not "-" in card:
                    device_path = f"/sys/class/drm/{card}/device"
                    if os.path.exists(device_path):
                        vendor_path = f"{device_path}/vendor"
                        if os.path.exists(vendor_path):
                            with open(vendor_path) as f:
                                vendor = f.read().strip()
                                if vendor == "0x1002":  # AMD vendor ID
                                    return device_path
        except Exception:
            pass
        return None
    
    def _find_intel_gpu(self) -> Optional[str]:
        """Find Intel GPU sysfs path"""
        try:
            for card in os.listdir("/sys/class/drm"):
                if card.startswith("card") and not "-" in card:
                    device_path = f"/sys/class/drm/{card}/device"
                    if os.path.exists(device_path):
                        vendor_path = f"{device_path}/vendor"
                        if os.path.exists(vendor_path):
                            with open(vendor_path) as f:
                                vendor = f.read().strip()
                                if vendor == "0x8086":  # Intel vendor ID
                                    return device_path
        except Exception:
            pass
        return None
    
    # ========== GPU Switching Methods ==========
    
    def get_switching_status(self) -> GpuSwitchingStatus:
        """Get current GPU switching status from supergfxctl"""
        status = GpuSwitchingStatus()
        
        if not self.supergfxctl_available:
            return status
        
        status.available = True
        
        # Get current mode
        try:
            result = subprocess.run(
                ["supergfxctl", "--get"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                mode_str = result.stdout.strip()
                status.current_mode = GpuMode.from_string(mode_str)
        except Exception:
            pass
        
        # Get supported modes
        try:
            result = subprocess.run(
                ["supergfxctl", "--supported"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                modes_str = result.stdout.strip()
                for mode_str in modes_str.replace("[", "").replace("]", "").split(","):
                    mode = GpuMode.from_string(mode_str.strip())
                    if mode:
                        status.supported_modes.append(mode)
        except Exception:
            pass
        
        # Get vendor
        try:
            result = subprocess.run(
                ["supergfxctl", "--vendor"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                status.dgpu_vendor = result.stdout.strip() or "Unknown"
        except Exception:
            pass
        
        # Get power status
        try:
            result = subprocess.run(
                ["supergfxctl", "--status"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                power_str = result.stdout.strip().lower()
                if "active" in power_str:
                    status.power_status = GpuPowerStatus.ACTIVE
                elif "suspend" in power_str:
                    status.power_status = GpuPowerStatus.SUSPENDED
                elif "off" in power_str:
                    status.power_status = GpuPowerStatus.OFF
        except Exception:
            pass
        
        # Get pending action
        try:
            result = subprocess.run(
                ["supergfxctl", "--pend-action"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                action = result.stdout.strip()
                if action and action.lower() not in ["none", ""]:
                    status.pending_action = action
                    if "logout" in action.lower():
                        status.requires_logout = True
                    if "reboot" in action.lower():
                        status.requires_reboot = True
        except Exception:
            pass
        
        # Get pending mode
        try:
            result = subprocess.run(
                ["supergfxctl", "--pend-mode"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                mode_str = result.stdout.strip()
                if mode_str and mode_str.lower() not in ["none", ""]:
                    status.pending_mode = GpuMode.from_string(mode_str)
        except Exception:
            pass
        
        return status
    
    def set_gpu_mode(self, mode: GpuMode) -> Tuple[bool, str]:
        """Set GPU mode via supergfxctl"""
        if not self.supergfxctl_available:
            return False, "supergfxctl is not installed"
        
        try:
            result = subprocess.run(
                ["supergfxctl", "--mode", mode.value],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if "logout" in output.lower():
                    return True, "Mode change queued. Please log out and back in."
                elif "reboot" in output.lower():
                    return True, "Mode change queued. Please reboot."
                return True, f"GPU mode set to {mode.value}"
            else:
                error = result.stderr.strip() or result.stdout.strip()
                return False, f"Failed to set mode: {error}"
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    # ========== Live GPU Stats Methods ==========
    
    def get_live_stats(self) -> GpuLiveStats:
        """Get live GPU statistics from the active GPU"""
        stats = GpuLiveStats()
        
        # Try NVIDIA first (if available and active)
        if self.nvidia_available:
            nvidia_stats = self._get_nvidia_stats()
            if nvidia_stats:
                return nvidia_stats
        
        # Try AMD GPU
        if self.amd_gpu_path:
            amd_stats = self._get_amd_stats()
            if amd_stats.gpu_name != "Unknown":
                return amd_stats
        
        # Try Intel GPU
        if self.intel_gpu_path:
            intel_stats = self._get_intel_stats()
            if intel_stats.gpu_name != "Unknown":
                return intel_stats
        
        return stats
    
    def _get_nvidia_stats(self) -> Optional[GpuLiveStats]:
        """Get stats from NVIDIA GPU using nvidia-smi"""
        try:
            query_fields = [
                "gpu_name", "driver_version",
                "clocks.current.graphics", "clocks.current.memory",
                "clocks.max.graphics", "clocks.max.memory",
                "utilization.gpu", "utilization.memory",
                "utilization.encoder", "utilization.decoder",
                "memory.total", "memory.used", "memory.free",
                "temperature.gpu", "power.draw", "power.limit", "fan.speed"
            ]
            
            result = subprocess.run(
                ["nvidia-smi", f"--query-gpu={','.join(query_fields)}", 
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            values = result.stdout.strip().split(", ")
            if len(values) < len(query_fields):
                return None
            
            stats = GpuLiveStats()
            stats.gpu_name = values[0]
            stats.vendor = "NVIDIA"
            stats.driver = values[1]
            
            def safe_int(s):
                try: return int(float(s))
                except: return 0
            
            def safe_float(s):
                try: return float(s)
                except: return 0.0
            
            stats.gpu_clock_mhz = safe_int(values[2])
            stats.mem_clock_mhz = safe_int(values[3])
            stats.gpu_clock_max_mhz = safe_int(values[4])
            stats.mem_clock_max_mhz = safe_int(values[5])
            stats.gpu_usage_percent = safe_int(values[6])
            stats.mem_usage_percent = safe_int(values[7])
            stats.encoder_usage_percent = safe_int(values[8])
            stats.decoder_usage_percent = safe_int(values[9])
            stats.vram_total_mb = safe_int(values[10])
            stats.vram_used_mb = safe_int(values[11])
            stats.vram_free_mb = safe_int(values[12])
            stats.gpu_temp_c = safe_int(values[13])
            stats.power_draw_w = safe_float(values[14])
            stats.power_limit_w = safe_float(values[15])
            stats.fan_speed_percent = safe_int(values[16])
            
            return stats
            
        except Exception as e:
            print(f"Error getting NVIDIA stats: {e}")
            return None
    
    def _get_amd_stats(self) -> GpuLiveStats:
        """Get stats from AMD GPU via sysfs"""
        stats = GpuLiveStats()
        stats.vendor = "AMD"
        
        if not self.amd_gpu_path:
            return stats
        
        def read_sysfs(filename):
            path = f"{self.amd_gpu_path}/{filename}"
            try:
                if os.path.exists(path):
                    with open(path) as f:
                        return f.read().strip()
            except Exception:
                pass
            return ""
        
        def read_hwmon(filename):
            hwmon_path = f"{self.amd_gpu_path}/hwmon"
            if os.path.exists(hwmon_path):
                for hwmon_dir in os.listdir(hwmon_path):
                    path = f"{hwmon_path}/{hwmon_dir}/{filename}"
                    try:
                        if os.path.exists(path):
                            with open(path) as f:
                                return f.read().strip()
                    except Exception:
                        pass
            return ""
        
        # Get GPU name
        try:
            result = subprocess.run(["lspci", "-v"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "VGA" in line and ("AMD" in line or "ATI" in line or "Radeon" in line):
                        match = re.search(r'\[(.+)\]', line)
                        if match:
                            stats.gpu_name = match.group(1)
                            break
        except Exception:
            pass
        
        if not stats.gpu_name or stats.gpu_name == "Unknown":
            stats.gpu_name = "AMD GPU"
        
        # GPU busy percent
        busy = read_sysfs("gpu_busy_percent")
        if busy:
            try: stats.gpu_usage_percent = int(busy)
            except: pass
        
        # Parse clock speeds
        sclk = read_sysfs("pp_dpm_sclk")
        if sclk:
            for line in sclk.split('\n'):
                match = re.search(r'(\d+)\s*[Mm][Hh]z', line)
                if match:
                    clock = int(match.group(1))
                    stats.gpu_clock_max_mhz = max(stats.gpu_clock_max_mhz, clock)
                    if '*' in line:
                        stats.gpu_clock_mhz = clock
        
        mclk = read_sysfs("pp_dpm_mclk")
        if mclk:
            for line in mclk.split('\n'):
                match = re.search(r'(\d+)\s*[Mm][Hh]z', line)
                if match:
                    clock = int(match.group(1))
                    stats.mem_clock_max_mhz = max(stats.mem_clock_max_mhz, clock)
                    if '*' in line:
                        stats.mem_clock_mhz = clock
        
        # Temperature
        temp = read_hwmon("temp1_input")
        if temp:
            try: stats.gpu_temp_c = int(temp) // 1000
            except: pass
        
        temp_edge = read_hwmon("temp2_input")
        if temp_edge:
            try: stats.junction_temp_c = int(temp_edge) // 1000
            except: pass
        
        temp_mem = read_hwmon("temp3_input")
        if temp_mem:
            try: stats.mem_temp_c = int(temp_mem) // 1000
            except: pass
        
        # Power
        power = read_hwmon("power1_average")
        if power:
            try: stats.power_draw_w = int(power) / 1_000_000
            except: pass
        
        power_cap = read_hwmon("power1_cap")
        if power_cap:
            try: stats.power_limit_w = int(power_cap) / 1_000_000
            except: pass
        
        # Fan
        fan_rpm = read_hwmon("fan1_input")
        if fan_rpm:
            try: stats.fan_speed_rpm = int(fan_rpm)
            except: pass
        
        fan_max = read_hwmon("fan1_max")
        if fan_max and stats.fan_speed_rpm:
            try:
                max_rpm = int(fan_max)
                if max_rpm > 0:
                    stats.fan_speed_percent = (stats.fan_speed_rpm * 100) // max_rpm
            except: pass
        
        # VRAM
        vram_total = read_sysfs("mem_info_vram_total")
        if vram_total:
            try: stats.vram_total_mb = int(vram_total) // (1024 * 1024)
            except: pass
        
        vram_used = read_sysfs("mem_info_vram_used")
        if vram_used:
            try:
                stats.vram_used_mb = int(vram_used) // (1024 * 1024)
                stats.vram_free_mb = stats.vram_total_mb - stats.vram_used_mb
                if stats.vram_total_mb > 0:
                    stats.mem_usage_percent = (stats.vram_used_mb * 100) // stats.vram_total_mb
            except: pass
        
        # Performance level
        perf_level = read_sysfs("power_dpm_force_performance_level")
        if perf_level:
            stats.performance_level = perf_level
        
        # Power profile
        profile = read_sysfs("pp_power_profile_mode")
        if profile:
            for line in profile.split('\n'):
                if '*' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        stats.power_profile = parts[1].replace('*', '').replace(':', '')
                        break
        
        # Driver info
        driver_path = f"{self.amd_gpu_path}/driver"
        if os.path.islink(driver_path):
            driver = os.path.basename(os.readlink(driver_path))
            stats.driver = driver
        
        return stats
    
    def _get_intel_stats(self) -> GpuLiveStats:
        """Get stats from Intel GPU"""
        stats = GpuLiveStats()
        stats.vendor = "Intel"
        
        if not self.intel_gpu_path:
            return stats
        
        try:
            result = subprocess.run(["lspci", "-v"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "VGA" in line and "Intel" in line:
                        match = re.search(r'\[(.+)\]', line)
                        if match:
                            stats.gpu_name = match.group(1)
                            break
        except Exception:
            pass
        
        if not stats.gpu_name or stats.gpu_name == "Unknown":
            stats.gpu_name = "Intel Integrated Graphics"
        
        def read_hwmon(filename):
            hwmon_path = f"{self.intel_gpu_path}/hwmon"
            if os.path.exists(hwmon_path):
                for hwmon_dir in os.listdir(hwmon_path):
                    path = f"{hwmon_path}/{hwmon_dir}/{filename}"
                    try:
                        if os.path.exists(path):
                            with open(path) as f:
                                return f.read().strip()
                    except Exception:
                        pass
            return ""
        
        temp = read_hwmon("temp1_input")
        if temp:
            try: stats.gpu_temp_c = int(temp) // 1000
            except: pass
        
        power = read_hwmon("power1_input")
        if power:
            try: stats.power_draw_w = int(power) / 1_000_000
            except: pass
        
        stats.driver = "i915"
        return stats
    
    def get_all_gpus(self) -> List[Dict]:
        """Get information about all detected GPUs"""
        gpus = []
        
        # Check for NVIDIA
        if self.nvidia_available:
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=index,name", "--format=csv,noheader"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split(', ')
                        if len(parts) >= 2:
                            gpus.append({
                                'index': int(parts[0]),
                                'name': parts[1],
                                'vendor': 'NVIDIA',
                                'type': 'discrete'
                            })
            except Exception:
                pass
        
        # Check for AMD GPUs
        try:
            for card in os.listdir("/sys/class/drm"):
                if card.startswith("card") and not "-" in card:
                    device_path = f"/sys/class/drm/{card}/device"
                    vendor_path = f"{device_path}/vendor"
                    if os.path.exists(vendor_path):
                        with open(vendor_path) as f:
                            vendor = f.read().strip()
                            if vendor == "0x1002":
                                name = "AMD GPU"
                                result = subprocess.run(["lspci", "-v"], capture_output=True, text=True, timeout=5)
                                if result.returncode == 0:
                                    for line in result.stdout.split("\n"):
                                        if "VGA" in line and ("AMD" in line or "Radeon" in line):
                                            match = re.search(r'\[(.+)\]', line)
                                            if match:
                                                name = match.group(1)
                                                break
                                
                                gpu_type = 'discrete'
                                if any(x in name for x in ['Vega', 'Renoir', 'Cezanne', 'Barcelo', 'Phoenix', 'Hawk']):
                                    gpu_type = 'integrated'
                                
                                gpus.append({
                                    'index': int(card.replace('card', '')),
                                    'name': name,
                                    'vendor': 'AMD',
                                    'type': gpu_type
                                })
        except Exception:
            pass
        
        # Check for Intel GPUs
        try:
            for card in os.listdir("/sys/class/drm"):
                if card.startswith("card") and not "-" in card:
                    device_path = f"/sys/class/drm/{card}/device"
                    vendor_path = f"{device_path}/vendor"
                    if os.path.exists(vendor_path):
                        with open(vendor_path) as f:
                            vendor = f.read().strip()
                            if vendor == "0x8086":
                                name = "Intel Graphics"
                                result = subprocess.run(["lspci", "-v"], capture_output=True, text=True, timeout=5)
                                if result.returncode == 0:
                                    for line in result.stdout.split("\n"):
                                        if "VGA" in line and "Intel" in line:
                                            match = re.search(r'\[(.+)\]', line)
                                            if match:
                                                name = match.group(1)
                                                break
                                
                                gpus.append({
                                    'index': int(card.replace('card', '')),
                                    'name': name,
                                    'vendor': 'Intel',
                                    'type': 'integrated'
                                })
        except Exception:
            pass
        
        return gpus


# Singleton instance
_controller: Optional[GpuController] = None

def get_controller() -> GpuController:
    """Get or create the GPU controller singleton"""
    global _controller
    if _controller is None:
        _controller = GpuController()
    return _controller


if __name__ == "__main__":
    ctrl = get_controller()
    
    print("=== GPU Detection ===")
    print(f"supergfxctl available: {ctrl.supergfxctl_available}")
    print(f"NVIDIA available: {ctrl.nvidia_available}")
    print(f"AMD GPU path: {ctrl.amd_gpu_path}")
    print(f"Intel GPU path: {ctrl.intel_gpu_path}")
    
    print("\n=== All GPUs ===")
    for gpu in ctrl.get_all_gpus():
        print(f"  {gpu}")
    
    print("\n=== GPU Switching Status ===")
    status = ctrl.get_switching_status()
    print(f"  Available: {status.available}")
    print(f"  Current mode: {status.current_mode}")
    print(f"  Supported modes: {status.supported_modes}")
    print(f"  dGPU vendor: {status.dgpu_vendor}")
    print(f"  Power status: {status.power_status}")
    
    print("\n=== Live GPU Stats ===")
    stats = ctrl.get_live_stats()
    print(f"  GPU: {stats.gpu_name} ({stats.vendor})")
    print(f"  Driver: {stats.driver}")
    print(f"  Clock: {stats.gpu_clock_mhz}/{stats.gpu_clock_max_mhz} MHz")
    print(f"  Memory Clock: {stats.mem_clock_mhz}/{stats.mem_clock_max_mhz} MHz")
    print(f"  Usage: {stats.gpu_usage_percent}%")
    print(f"  VRAM: {stats.vram_used_mb}/{stats.vram_total_mb} MB ({stats.mem_usage_percent}%)")
    print(f"  Temp: {stats.gpu_temp_c}°C")
    print(f"  Power: {stats.power_draw_w:.1f}/{stats.power_limit_w:.1f}W")
    print(f"  Fan: {stats.fan_speed_rpm} RPM ({stats.fan_speed_percent}%)")
