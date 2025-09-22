"""
ASUS ROG integration module for asusctl and supergfxctl
Enhanced with advanced hardware monitoring and control features
"""

import logging
from typing import Dict, List, Optional, Tuple
from linux_armoury.core.utils import run_command, check_command_exists


class ASUSCtlManager:
    """Manager for asusctl integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available = check_command_exists("asusctl")
        
        if not self.available:
            self.logger.warning("asusctl not found - ASUS-specific features will be disabled")
    
    def is_available(self) -> bool:
        """Check if asusctl is available"""
        return self.available
    
    def get_profiles(self) -> List[str]:
        """Get available performance profiles"""
        if not self.available:
            return []
        
        success, output = run_command(["asusctl", "profile", "-l"])
        if success:
            # Parse profile list from output
            profiles = []
            for line in output.split('\n'):
                if 'Profile' in line:
                    # Extract profile name from output
                    profile = line.split(':')[-1].strip()
                    if profile:
                        profiles.append(profile)
            return profiles
        
        return ["Balanced", "Performance", "Quiet"]  # Default profiles
    
    def get_current_profile(self) -> Optional[str]:
        """Get current performance profile"""
        if not self.available:
            return None
        
        success, output = run_command(["asusctl", "profile", "-p"])
        if success:
            # Parse current profile from output
            for line in output.split('\n'):
                if 'Active profile' in line or 'Current profile' in line:
                    return line.split(':')[-1].strip()
        
        return None
    
    def set_profile(self, profile: str) -> bool:
        """Set performance profile"""
        if not self.available:
            return False
        
        profile_map = {
            "balanced": "Balanced",
            "performance": "Performance", 
            "quiet": "Quiet"
        }
        
        asus_profile = profile_map.get(profile.lower(), profile)
        success, _ = run_command(["asusctl", "profile", "-P", asus_profile])
        
        if success:
            self.logger.info(f"Set ASUS profile to {asus_profile}")
        else:
            self.logger.error(f"Failed to set ASUS profile to {asus_profile}")
        
        return success
    
    def get_fan_curves(self) -> Dict[str, any]:
        """Get fan curve information"""
        if not self.available:
            return {}
        
        success, output = run_command(["asusctl", "fan-curve", "-i"])
        if success:
            # Parse fan curve information
            return {"available": True, "output": output}
        
        return {"available": False}
    
    def get_rgb_info(self) -> Dict[str, any]:
        """Get RGB keyboard information"""
        if not self.available:
            return {}
        
        success, output = run_command(["asusctl", "led", "-s"])
        if success:
            return {"available": True, "status": output}
        
        return {"available": False}
    
    def set_rgb_mode(self, mode: str) -> bool:
        """Set RGB keyboard mode"""
        if not self.available:
            return False
        
        success, _ = run_command(["asusctl", "led", "-m", mode])
        
        if success:
            self.logger.info(f"Set RGB mode to {mode}")
        else:
            self.logger.error(f"Failed to set RGB mode to {mode}")
        
        return success


class SuperGfxCtlManager:
    """Manager for supergfxctl integration (GPU switching)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available = check_command_exists("supergfxctl")
        
        if not self.available:
            self.logger.warning("supergfxctl not found - GPU switching will be disabled")
    
    def is_available(self) -> bool:
        """Check if supergfxctl is available"""
        return self.available
    
    def get_gpu_modes(self) -> List[str]:
        """Get available GPU modes"""
        if not self.available:
            return []
        
        success, output = run_command(["supergfxctl", "-g"])
        if success:
            modes = []
            for line in output.split('\n'):
                if 'Available modes' in line:
                    # Parse modes from output
                    mode_line = line.split(':')[-1].strip()
                    modes = [m.strip() for m in mode_line.split(',')]
                    break
            return modes
        
        return ["Integrated", "Hybrid", "Dedicated"]  # Default modes
    
    def get_current_gpu_mode(self) -> Optional[str]:
        """Get current GPU mode"""
        if not self.available:
            return None
        
        success, output = run_command(["supergfxctl", "-g"])
        if success:
            for line in output.split('\n'):
                if 'Current mode' in line:
                    return line.split(':')[-1].strip()
        
        return None
    
    def set_gpu_mode(self, mode: str) -> bool:
        """Set GPU mode"""
        if not self.available:
            return False
        
        mode_map = {
            "integrated": "Integrated",
            "hybrid": "Hybrid",
            "dedicated": "Dedicated",
            "compute": "Compute"
        }
        
        gpu_mode = mode_map.get(mode.lower(), mode)
        success, _ = run_command(["supergfxctl", "-m", gpu_mode])
        
        if success:
            self.logger.info(f"Set GPU mode to {gpu_mode}")
        else:
            self.logger.error(f"Failed to set GPU mode to {gpu_mode}")
        
        return success
    
    def needs_reboot(self) -> bool:
        """Check if a reboot is needed for GPU mode change"""
        if not self.available:
            return False
        
        success, output = run_command(["supergfxctl", "-s"])
        if success:
            return "reboot required" in output.lower() or "pending" in output.lower()
        
        return False


class TDPManager:
    """Manager for TDP control using gz302-tdp command"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available = check_command_exists("gz302-tdp")
        
        if not self.available:
            self.logger.warning("gz302-tdp not found - TDP management will be disabled")
    
    def is_available(self) -> bool:
        """Check if TDP management is available"""
        return self.available
    
    def get_profiles(self) -> List[str]:
        """Get available TDP profiles"""
        return ["gaming", "performance", "balanced", "efficient", "power_saver"]
    
    def get_status(self) -> Dict[str, any]:
        """Get TDP status"""
        if not self.available:
            return {}
        
        success, output = run_command(["gz302-tdp", "status"])
        if success:
            return {"available": True, "status": output}
        
        return {"available": False}
    
    def set_profile(self, profile: str) -> bool:
        """Set TDP profile"""
        if not self.available:
            return False
        
        success, _ = run_command(["gz302-tdp", profile])
        
        if success:
            self.logger.info(f"Set TDP profile to {profile}")
        else:
            self.logger.error(f"Failed to set TDP profile to {profile}")
        
        return success


class RefreshRateManager:
    """Manager for refresh rate control using gz302-refresh command"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available = check_command_exists("gz302-refresh")
        
        if not self.available:
            self.logger.warning("gz302-refresh not found - refresh rate management will be disabled")
    
    def is_available(self) -> bool:
        """Check if refresh rate management is available"""
        return self.available
    
    def get_profiles(self) -> List[str]:
        """Get available refresh rate profiles"""
        return ["gaming", "performance", "balanced", "efficient", "power_saver", "ultra_low"]
    
    def get_status(self) -> Dict[str, any]:
        """Get refresh rate status"""
        if not self.available:
            return {}
        
        success, output = run_command(["gz302-refresh", "status"])
        if success:
            return {"available": True, "status": output}
        
        return {"available": False}
    
    def set_profile(self, profile: str) -> bool:
        """Set refresh rate profile"""
        if not self.available:
            return False
        
        success, _ = run_command(["gz302-refresh", profile])
        
        if success:
            self.logger.info(f"Set refresh rate profile to {profile}")
        else:
            self.logger.error(f"Failed to set refresh rate profile to {profile}")
        
        return success
    
    def toggle_vrr(self, enable: bool) -> bool:
        """Toggle Variable Refresh Rate"""
        if not self.available:
            return False
        
        command = "on" if enable else "off"
        success, _ = run_command(["gz302-refresh", "vrr", command])
        
        if success:
            self.logger.info(f"VRR {'enabled' if enable else 'disabled'}")
        else:
            self.logger.error(f"Failed to {'enable' if enable else 'disable'} VRR")
        
        return success


class DisplayManager:
    """Manager for display controls including panel overdrive and color profiles"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asusctl_available = check_command_exists("asusctl")
        self.xrandr_available = check_command_exists("xrandr")
        
    def is_available(self) -> bool:
        """Check if display management is available"""
        return self.asusctl_available or self.xrandr_available
    
    def get_panel_overdrive_status(self) -> Dict[str, any]:
        """Get panel overdrive status"""
        if not self.asusctl_available:
            return {"available": False}
        
        success, output = run_command(["asusctl", "panel-od", "-g"])
        if success:
            return {"available": True, "status": output}
        
        return {"available": False}
    
    def set_panel_overdrive(self, enabled: bool) -> bool:
        """Enable/disable panel overdrive"""
        if not self.asusctl_available:
            return False
        
        try:
            cmd = ["asusctl", "panel-od", "-s", "1" if enabled else "0"]
            success, _ = run_command(cmd)
            return success
        except Exception as e:
            self.logger.error(f"Failed to set panel overdrive: {e}")
            return False
    
    def get_brightness(self) -> Optional[int]:
        """Get current screen brightness (0-100)"""
        try:
            with open("/sys/class/backlight/intel_backlight/brightness", "r") as f:
                current = int(f.read().strip())
            
            with open("/sys/class/backlight/intel_backlight/max_brightness", "r") as f:
                max_brightness = int(f.read().strip())
            
            return int((current / max_brightness) * 100)
        except Exception:
            return None
    
    def set_brightness(self, brightness: int) -> bool:
        """Set screen brightness (0-100)"""
        try:
            brightness = max(0, min(100, brightness))
            
            with open("/sys/class/backlight/intel_backlight/max_brightness", "r") as f:
                max_brightness = int(f.read().strip())
            
            target_brightness = int((brightness / 100) * max_brightness)
            
            # Try direct write first
            try:
                with open("/sys/class/backlight/intel_backlight/brightness", "w") as f:
                    f.write(str(target_brightness))
                return True
            except PermissionError:
                # Try with pkexec
                success, _ = run_command([
                    "pkexec", "sh", "-c",
                    f"echo {target_brightness} > /sys/class/backlight/intel_backlight/brightness"
                ])
                return success
        except Exception as e:
            self.logger.error(f"Failed to set brightness: {e}")
            return False


class PowerManagementManager:
    """Enhanced power management beyond basic TDP control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asusctl_available = check_command_exists("asusctl")
        
    def is_available(self) -> bool:
        """Check if power management is available"""
        return self.asusctl_available
    
    def get_platform_profile(self) -> Optional[str]:
        """Get current platform power profile"""
        try:
            with open("/sys/firmware/acpi/platform_profile", "r") as f:
                return f.read().strip()
        except Exception:
            return None
    
    def set_platform_profile(self, profile: str) -> bool:
        """Set platform power profile"""
        try:
            # Try direct write first
            try:
                with open("/sys/firmware/acpi/platform_profile", "w") as f:
                    f.write(profile)
                return True
            except PermissionError:
                # Try with pkexec
                success, _ = run_command([
                    "pkexec", "sh", "-c",
                    f"echo {profile} > /sys/firmware/acpi/platform_profile"
                ])
                return success
        except Exception as e:
            self.logger.error(f"Failed to set platform profile: {e}")
            return False
    
    def get_available_platform_profiles(self) -> List[str]:
        """Get available platform profiles"""
        try:
            with open("/sys/firmware/acpi/platform_profile_choices", "r") as f:
                return f.read().strip().split()
        except Exception:
            return ["balanced", "performance", "power-saver"]  # Common defaults
    
    def get_cpu_boost_status(self) -> Optional[bool]:
        """Get CPU boost status"""
        try:
            with open("/sys/devices/system/cpu/cpufreq/boost", "r") as f:
                return f.read().strip() == "1"
        except Exception:
            return None
    
    def set_cpu_boost(self, enabled: bool) -> bool:
        """Enable/disable CPU boost"""
        try:
            value = "1" if enabled else "0"
            # Try direct write first
            try:
                with open("/sys/devices/system/cpu/cpufreq/boost", "w") as f:
                    f.write(value)
                return True
            except PermissionError:
                # Try with pkexec
                success, _ = run_command([
                    "pkexec", "sh", "-c",
                    f"echo {value} > /sys/devices/system/cpu/cpufreq/boost"
                ])
                return success
        except Exception as e:
            self.logger.error(f"Failed to set CPU boost: {e}")
            return False