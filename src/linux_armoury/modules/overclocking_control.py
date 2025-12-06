#!/usr/bin/env python3
"""
Overclocking Control Module for Linux Armoury
Provides CPU frequency scaling, TDP control via RyzenAdj, and AMD GPU overclocking
"""

import subprocess
import os
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class CPUInfo:
    """CPU information and current settings"""
    model: str = ""
    cores: int = 0
    threads: int = 0
    base_freq_mhz: float = 0.0
    max_freq_mhz: float = 0.0
    current_freq_mhz: float = 0.0
    governor: str = ""
    available_governors: List[str] = None
    turbo_enabled: bool = True
    energy_perf_preference: str = ""
    
    def __post_init__(self):
        if self.available_governors is None:
            self.available_governors = []


@dataclass
class GPUInfo:
    """AMD GPU information and current settings"""
    name: str = ""
    driver: str = ""
    vram_mb: int = 0
    current_gpu_clock_mhz: int = 0
    current_mem_clock_mhz: int = 0
    gpu_temp_c: float = 0.0
    power_level: str = ""
    power_profile: str = ""
    available_power_profiles: List[str] = None
    
    def __post_init__(self):
        if self.available_power_profiles is None:
            self.available_power_profiles = []


class OverclockingController:
    """Controller for CPU/GPU overclocking and power management"""
    
    SYSFS_CPU_BASE = "/sys/devices/system/cpu"
    SYSFS_DRM_BASE = "/sys/class/drm"
    
    def __init__(self):
        self.ryzenadj_available = self._check_ryzenadj()
        self.cpupower_available = self._check_cpupower()
        self.amd_gpu_path = self._find_amd_gpu()
    
    def _check_ryzenadj(self) -> bool:
        """Check if RyzenAdj is available"""
        try:
            result = subprocess.run(["which", "ryzenadj"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_cpupower(self) -> bool:
        """Check if cpupower is available"""
        try:
            result = subprocess.run(["which", "cpupower"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _find_amd_gpu(self) -> Optional[str]:
        """Find AMD GPU sysfs path"""
        drm_path = Path(self.SYSFS_DRM_BASE)
        if not drm_path.exists():
            return None
        
        for card in drm_path.iterdir():
            if card.name.startswith("card") and not card.name.endswith("-"):
                device_path = card / "device"
                vendor_path = device_path / "vendor"
                if vendor_path.exists():
                    try:
                        vendor = vendor_path.read_text().strip()
                        if vendor == "0x1002":  # AMD vendor ID
                            return str(device_path)
                    except Exception:
                        continue
        return None
    
    def _read_sysfs(self, path: str) -> Optional[str]:
        """Read a sysfs file"""
        try:
            return Path(path).read_text().strip()
        except Exception:
            return None
    
    def _write_sysfs(self, path: str, value: str) -> bool:
        """Write to a sysfs file (requires root)"""
        try:
            Path(path).write_text(value)
            return True
        except PermissionError:
            try:
                result = subprocess.run(
                    ["pkexec", "tee", path],
                    input=value,
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except Exception:
                return False
        except Exception:
            return False
    
    def _run_privileged(self, cmd: List[str]) -> tuple:
        """Run a command with pkexec for privilege escalation"""
        try:
            result = subprocess.run(
                ["pkexec"] + cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    # ==================== CPU CONTROLS ====================
    
    def get_cpu_info(self) -> CPUInfo:
        """Get current CPU information"""
        info = CPUInfo()
        
        # Get CPU model from /proc/cpuinfo
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text()
            model_match = re.search(r"model name\s*:\s*(.+)", cpuinfo)
            if model_match:
                info.model = model_match.group(1).strip()
            
            # Count cores and threads
            info.threads = cpuinfo.count("processor")
            cores_match = re.search(r"cpu cores\s*:\s*(\d+)", cpuinfo)
            if cores_match:
                info.cores = int(cores_match.group(1))
            else:
                info.cores = info.threads
        except Exception:
            pass
        
        # Get frequency info from scaling driver
        cpu0_path = f"{self.SYSFS_CPU_BASE}/cpu0/cpufreq"
        
        min_freq = self._read_sysfs(f"{cpu0_path}/cpuinfo_min_freq")
        if min_freq:
            info.base_freq_mhz = int(min_freq) / 1000
        
        max_freq = self._read_sysfs(f"{cpu0_path}/cpuinfo_max_freq")
        if max_freq:
            info.max_freq_mhz = int(max_freq) / 1000
        
        cur_freq = self._read_sysfs(f"{cpu0_path}/scaling_cur_freq")
        if cur_freq:
            info.current_freq_mhz = int(cur_freq) / 1000
        
        # Get governor
        governor = self._read_sysfs(f"{cpu0_path}/scaling_governor")
        if governor:
            info.governor = governor
        
        # Get available governors
        governors = self._read_sysfs(f"{cpu0_path}/scaling_available_governors")
        if governors:
            info.available_governors = governors.split()
        
        # Get turbo boost status
        info.turbo_enabled = self.get_turbo_boost_status()
        
        # Get energy performance preference
        epp = self._read_sysfs(f"{cpu0_path}/energy_performance_preference")
        if epp:
            info.energy_perf_preference = epp
        
        return info
    
    def get_turbo_boost_status(self) -> bool:
        """Check if turbo boost is enabled"""
        # Check Intel
        intel_turbo = self._read_sysfs("/sys/devices/system/cpu/intel_pstate/no_turbo")
        if intel_turbo:
            return intel_turbo == "0"
        
        # Check AMD
        amd_boost = self._read_sysfs(f"{self.SYSFS_CPU_BASE}/cpufreq/boost")
        if amd_boost:
            return amd_boost == "1"
        
        return True  # Default to enabled if we can't check
    
    def set_turbo_boost(self, enabled: bool) -> bool:
        """Enable or disable turbo boost"""
        # Try Intel first
        intel_path = "/sys/devices/system/cpu/intel_pstate/no_turbo"
        if Path(intel_path).exists():
            return self._write_sysfs(intel_path, "0" if enabled else "1")
        
        # Try AMD
        amd_path = f"{self.SYSFS_CPU_BASE}/cpufreq/boost"
        if Path(amd_path).exists():
            return self._write_sysfs(amd_path, "1" if enabled else "0")
        
        return False
    
    def get_available_governors(self) -> List[str]:
        """Get list of available CPU governors"""
        governors = self._read_sysfs(f"{self.SYSFS_CPU_BASE}/cpu0/cpufreq/scaling_available_governors")
        if governors:
            return governors.split()
        return []
    
    def set_cpu_governor(self, governor: str) -> bool:
        """Set CPU governor for all cores"""
        if self.cpupower_available:
            success, _, _ = self._run_privileged(["cpupower", "frequency-set", "-g", governor])
            return success
        
        # Fallback to direct sysfs
        cpu_path = Path(self.SYSFS_CPU_BASE)
        success = True
        for cpu in cpu_path.iterdir():
            if cpu.name.startswith("cpu") and cpu.name[3:].isdigit():
                gov_path = cpu / "cpufreq" / "scaling_governor"
                if gov_path.exists():
                    if not self._write_sysfs(str(gov_path), governor):
                        success = False
        return success
    
    def set_cpu_frequency_limits(self, min_mhz: Optional[int] = None, max_mhz: Optional[int] = None) -> bool:
        """Set CPU frequency limits"""
        if self.cpupower_available:
            cmd = ["cpupower", "frequency-set"]
            if min_mhz:
                cmd.extend(["-d", f"{min_mhz}MHz"])
            if max_mhz:
                cmd.extend(["-u", f"{max_mhz}MHz"])
            success, _, _ = self._run_privileged(cmd)
            return success
        return False
    
    # ==================== RYZENADJ CONTROLS ====================
    
    def get_ryzenadj_info(self) -> Optional[Dict[str, Any]]:
        """Get current RyzenAdj power limits"""
        if not self.ryzenadj_available:
            return None
        
        try:
            result = subprocess.run(
                ["pkexec", "ryzenadj", "-i"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return None
            
            info = {}
            for line in result.stdout.split("\n"):
                # Parse RyzenAdj output
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        name = parts[0]
                        value = parts[1]
                        if name and value:
                            try:
                                info[name] = float(value)
                            except ValueError:
                                info[name] = value
            return info
        except Exception:
            return None
    
    def set_ryzenadj_tdp(self, stapm_limit: Optional[int] = None,
                         fast_limit: Optional[int] = None,
                         slow_limit: Optional[int] = None) -> bool:
        """Set TDP limits using RyzenAdj (values in watts)"""
        if not self.ryzenadj_available:
            return False
        
        cmd = ["ryzenadj"]
        if stapm_limit is not None:
            cmd.extend(["--stapm-limit", str(stapm_limit * 1000)])  # Convert W to mW
        if fast_limit is not None:
            cmd.extend(["--fast-limit", str(fast_limit * 1000)])
        if slow_limit is not None:
            cmd.extend(["--slow-limit", str(slow_limit * 1000)])
        
        if len(cmd) == 1:
            return False
        
        success, _, _ = self._run_privileged(cmd)
        return success
    
    def set_ryzenadj_temp_limit(self, temp_c: int) -> bool:
        """Set temperature limit using RyzenAdj"""
        if not self.ryzenadj_available:
            return False
        
        success, _, _ = self._run_privileged(["ryzenadj", "--tctl-temp", str(temp_c)])
        return success
    
    # ==================== AMD GPU CONTROLS ====================
    
    def get_amd_gpu_info(self) -> Optional[GPUInfo]:
        """Get AMD GPU information"""
        if not self.amd_gpu_path:
            return None
        
        info = GPUInfo()
        info.driver = "amdgpu"
        
        # Get GPU name
        name_path = f"{self.amd_gpu_path}/product_name"
        name = self._read_sysfs(name_path)
        if name:
            info.name = name
        else:
            # Try hwmon name
            hwmon_path = Path(self.amd_gpu_path) / "hwmon"
            if hwmon_path.exists():
                for hwmon in hwmon_path.iterdir():
                    name_file = hwmon / "name"
                    if name_file.exists():
                        info.name = self._read_sysfs(str(name_file)) or "AMD GPU"
                        break
        
        # Get VRAM
        vram_path = f"{self.amd_gpu_path}/mem_info_vram_total"
        vram = self._read_sysfs(vram_path)
        if vram:
            info.vram_mb = int(vram) // (1024 * 1024)
        
        # Get current clocks from pp_dpm_sclk (GPU) and pp_dpm_mclk (memory)
        sclk_path = f"{self.amd_gpu_path}/pp_dpm_sclk"
        sclk = self._read_sysfs(sclk_path)
        if sclk:
            for line in sclk.split("\n"):
                if "*" in line:  # Active clock marked with *
                    match = re.search(r"(\d+)Mhz", line)
                    if match:
                        info.current_gpu_clock_mhz = int(match.group(1))
                    break
        
        mclk_path = f"{self.amd_gpu_path}/pp_dpm_mclk"
        mclk = self._read_sysfs(mclk_path)
        if mclk:
            for line in mclk.split("\n"):
                if "*" in line:
                    match = re.search(r"(\d+)Mhz", line)
                    if match:
                        info.current_mem_clock_mhz = int(match.group(1))
                    break
        
        # Get temperature from hwmon
        hwmon_path = Path(self.amd_gpu_path) / "hwmon"
        if hwmon_path.exists():
            for hwmon in hwmon_path.iterdir():
                temp_file = hwmon / "temp1_input"
                if temp_file.exists():
                    temp = self._read_sysfs(str(temp_file))
                    if temp:
                        info.gpu_temp_c = int(temp) / 1000
                    break
        
        # Get performance level
        perf_path = f"{self.amd_gpu_path}/power_dpm_force_performance_level"
        perf = self._read_sysfs(perf_path)
        if perf:
            info.power_level = perf
        
        # Get power profile mode
        profile_path = f"{self.amd_gpu_path}/pp_power_profile_mode"
        profiles = self._read_sysfs(profile_path)
        if profiles:
            for line in profiles.split("\n"):
                if "*" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        info.power_profile = parts[1] if parts[1] != "*" else parts[0]
                    break
            # Parse available profiles
            for line in profiles.split("\n"):
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    profile_name = parts[1].replace("*", "").strip()
                    if profile_name:
                        info.available_power_profiles.append(profile_name)
        
        return info
    
    def set_gpu_performance_level(self, level: str) -> bool:
        """Set GPU performance level (auto, low, high, manual, profile_standard, etc.)"""
        if not self.amd_gpu_path:
            return False
        
        perf_path = f"{self.amd_gpu_path}/power_dpm_force_performance_level"
        return self._write_sysfs(perf_path, level)
    
    def set_gpu_power_profile(self, profile_index: int) -> bool:
        """Set GPU power profile mode by index"""
        if not self.amd_gpu_path:
            return False
        
        profile_path = f"{self.amd_gpu_path}/pp_power_profile_mode"
        return self._write_sysfs(profile_path, str(profile_index))
    
    def get_gpu_power_profiles(self) -> List[tuple]:
        """Get available GPU power profiles as (index, name, is_active)"""
        if not self.amd_gpu_path:
            return []
        
        profiles = []
        profile_path = f"{self.amd_gpu_path}/pp_power_profile_mode"
        content = self._read_sysfs(profile_path)
        if content:
            for line in content.split("\n"):
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    idx = int(parts[0])
                    is_active = "*" in line
                    name = parts[1].replace("*", "").strip()
                    profiles.append((idx, name, is_active))
        return profiles
    
    def reset_gpu_clocks(self) -> bool:
        """Reset GPU clocks to default"""
        if not self.amd_gpu_path:
            return False
        
        od_path = f"{self.amd_gpu_path}/pp_od_clk_voltage"
        return self._write_sysfs(od_path, "r")
    
    # ==================== ENERGY PERFORMANCE PREFERENCE ====================
    
    def get_energy_performance_preference(self) -> Optional[str]:
        """Get current energy performance preference"""
        epp_path = f"{self.SYSFS_CPU_BASE}/cpu0/cpufreq/energy_performance_preference"
        return self._read_sysfs(epp_path)
    
    def get_available_energy_preferences(self) -> List[str]:
        """Get available energy performance preferences"""
        epp_path = f"{self.SYSFS_CPU_BASE}/cpu0/cpufreq/energy_performance_available_preferences"
        content = self._read_sysfs(epp_path)
        if content:
            return content.split()
        return []
    
    def set_energy_performance_preference(self, preference: str) -> bool:
        """Set energy performance preference for all cores"""
        cpu_path = Path(self.SYSFS_CPU_BASE)
        success = True
        for cpu in cpu_path.iterdir():
            if cpu.name.startswith("cpu") and cpu.name[3:].isdigit():
                epp_path = cpu / "cpufreq" / "energy_performance_preference"
                if epp_path.exists():
                    if not self._write_sysfs(str(epp_path), preference):
                        success = False
        return success


# TDP presets for common scenarios
TDP_PRESETS = {
    "silent": {"stapm": 10, "fast": 12, "slow": 10},
    "balanced": {"stapm": 25, "fast": 35, "slow": 25},
    "performance": {"stapm": 35, "fast": 45, "slow": 35},
    "turbo": {"stapm": 45, "fast": 65, "slow": 45},
}


if __name__ == "__main__":
    # Test the module
    controller = OverclockingController()
    
    print("=== CPU Info ===")
    cpu_info = controller.get_cpu_info()
    print(f"Model: {cpu_info.model}")
    print(f"Cores/Threads: {cpu_info.cores}/{cpu_info.threads}")
    print(f"Frequency: {cpu_info.current_freq_mhz:.0f} MHz (max: {cpu_info.max_freq_mhz:.0f} MHz)")
    print(f"Governor: {cpu_info.governor}")
    print(f"Turbo: {'Enabled' if cpu_info.turbo_enabled else 'Disabled'}")
    
    if controller.ryzenadj_available:
        print("\n=== RyzenAdj Available ===")
    
    if controller.amd_gpu_path:
        print("\n=== AMD GPU Info ===")
        gpu_info = controller.get_amd_gpu_info()
        if gpu_info:
            print(f"Name: {gpu_info.name}")
            print(f"VRAM: {gpu_info.vram_mb} MB")
            print(f"GPU Clock: {gpu_info.current_gpu_clock_mhz} MHz")
            print(f"Temp: {gpu_info.gpu_temp_c}°C")
            print(f"Performance Level: {gpu_info.power_level}")
