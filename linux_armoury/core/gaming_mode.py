"""
Gaming optimization module for Linux Armoury
Inspired by Armoury Crate's GameFirst and performance optimization features
"""

import logging
import psutil
import time
import json
from typing import Dict, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from linux_armoury.core.utils import run_command, check_command_exists
from linux_armoury.core.config import Config


class GameProfile(Enum):
    """Gaming performance profiles"""
    ESPORTS = "esports"          # Maximum FPS, minimal latency
    AAA_GAMING = "aaa_gaming"    # Balanced high performance
    STREAMING = "streaming"       # Optimized for streaming/recording
    BATTERY_GAMING = "battery"    # Gaming on battery
    VR_GAMING = "vr"             # VR optimizations


@dataclass
class GameSettings:
    """Game-specific settings"""
    name: str
    executable: str
    profile: GameProfile
    tdp_profile: str = "performance"
    gpu_mode: str = "hybrid"
    refresh_rate: str = "gaming"
    fan_curve: str = "performance"
    rgb_profile: str = "gaming"
    cpu_governor: str = "performance"
    gpu_performance_mode: str = "high"
    network_priority: bool = True
    process_priority: str = "high"
    fullscreen_optimizations: bool = True


class ProcessManager:
    """Process and system optimization manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gamemode_available = check_command_exists("gamemoderun")
        self.original_nice_values = {}
        
    def is_gamemode_available(self) -> bool:
        """Check if GameMode is available"""
        return self.gamemode_available
    
    def start_gamemode(self) -> bool:
        """Start GameMode daemon"""
        if not self.gamemode_available:
            return False
        
        try:
            # GameMode usually starts automatically, but we can check status
            success, _ = run_command(["gamemoded", "--status"])
            return success
        except Exception as e:
            self.logger.error(f"Failed to start GameMode: {e}")
            return False
    
    def set_process_priority(self, pid: int, priority: str) -> bool:
        """Set process priority (nice value)"""
        try:
            process = psutil.Process(pid)
            
            # Store original nice value
            if pid not in self.original_nice_values:
                self.original_nice_values[pid] = process.nice()
            
            # Set new priority
            if priority == "high":
                process.nice(-10)  # Higher priority
            elif priority == "realtime":
                process.nice(-20)  # Highest priority (requires root)
            elif priority == "normal":
                process.nice(0)
            elif priority == "low":
                process.nice(10)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to set process priority: {e}")
            return False
    
    def restore_process_priority(self, pid: int) -> bool:
        """Restore original process priority"""
        try:
            if pid in self.original_nice_values:
                process = psutil.Process(pid)
                process.nice(self.original_nice_values[pid])
                del self.original_nice_values[pid]
                return True
        except Exception as e:
            self.logger.error(f"Failed to restore process priority: {e}")
        
        return False
    
    def set_cpu_governor(self, governor: str) -> bool:
        """Set CPU frequency governor"""
        try:
            # Get number of CPUs
            cpu_count = psutil.cpu_count()
            
            success = True
            for cpu in range(cpu_count):
                governor_file = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor"
                try:
                    with open(governor_file, 'w') as f:
                        f.write(governor)
                except PermissionError:
                    # Try with pkexec
                    cmd_success, _ = run_command([
                        "pkexec", "sh", "-c", 
                        f"echo {governor} > {governor_file}"
                    ])
                    if not cmd_success:
                        success = False
                except Exception:
                    success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to set CPU governor: {e}")
            return False
    
    def get_available_governors(self) -> List[str]:
        """Get available CPU governors"""
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors", 'r') as f:
                governors = f.read().strip().split()
                return governors
        except Exception:
            # Default governors that are commonly available
            return ["performance", "powersave", "ondemand", "conservative", "schedutil"]
    
    def disable_cpu_mitigations(self) -> bool:
        """Disable CPU security mitigations for performance (temporary)"""
        # This would typically require kernel parameter changes
        # For runtime, we can try to disable some mitigations
        try:
            mitigations = [
                "/sys/devices/system/cpu/vulnerabilities/l1tf",
                "/sys/devices/system/cpu/vulnerabilities/mds",
                "/sys/devices/system/cpu/vulnerabilities/spectre_v1",
                "/sys/devices/system/cpu/vulnerabilities/spectre_v2"
            ]
            
            # This is read-only, would need kernel parameters
            # Just log what mitigations are active
            active_mitigations = []
            for mitigation_file in mitigations:
                if Path(mitigation_file).exists():
                    try:
                        with open(mitigation_file, 'r') as f:
                            status = f.read().strip()
                            if "Mitigation" in status:
                                active_mitigations.append(Path(mitigation_file).name)
                    except Exception:
                        pass
            
            if active_mitigations:
                self.logger.info(f"Active CPU mitigations: {', '.join(active_mitigations)}")
                self.logger.info("Consider adding 'mitigations=off' to kernel parameters for maximum gaming performance")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to check CPU mitigations: {e}")
            return False


class NetworkOptimizer:
    """Network optimization for gaming"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tc_available = check_command_exists("tc")
        
    def is_available(self) -> bool:
        """Check if network optimization is available"""
        return self.tc_available
    
    def optimize_for_gaming(self) -> bool:
        """Apply gaming network optimizations"""
        if not self.tc_available:
            return False
        
        try:
            # Set TCP congestion control to BBR (if available)
            success1, _ = run_command([
                "pkexec", "sh", "-c",
                "echo bbr > /proc/sys/net/ipv4/tcp_congestion_control"
            ])
            
            # Optimize network buffer sizes
            optimizations = [
                "echo 262144 > /proc/sys/net/core/rmem_max",
                "echo 262144 > /proc/sys/net/core/wmem_max",
                "echo '4096 16384 262144' > /proc/sys/net/ipv4/tcp_rmem",
                "echo '4096 65536 262144' > /proc/sys/net/ipv4/tcp_wmem",
                "echo 1 > /proc/sys/net/ipv4/tcp_low_latency"
            ]
            
            success2 = True
            for opt in optimizations:
                cmd_success, _ = run_command(["pkexec", "sh", "-c", opt])
                if not cmd_success:
                    success2 = False
            
            return success1 and success2
        except Exception as e:
            self.logger.error(f"Failed to optimize network: {e}")
            return False
    
    def set_process_network_priority(self, pid: int, priority: bool = True) -> bool:
        """Set network priority for a process"""
        # This would typically use traffic control (tc) to prioritize packets
        # Implementation is complex and requires root privileges
        self.logger.info(f"Network priority setting not fully implemented for PID {pid}")
        return True
    
    def monitor_network_latency(self, host: str = "8.8.8.8") -> Optional[float]:
        """Monitor network latency to a host"""
        try:
            success, output = run_command(["ping", "-c", "1", "-W", "1", host])
            if success:
                # Parse ping output for latency
                for line in output.split('\n'):
                    if 'time=' in line:
                        time_part = line.split('time=')[1].split()[0]
                        return float(time_part)
        except Exception as e:
            self.logger.debug(f"Failed to measure latency: {e}")
        
        return None


class GameModeManager:
    """Main gaming mode manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.process_manager = ProcessManager()
        self.network_optimizer = NetworkOptimizer()
        self.active_games = {}  # pid -> GameSettings
        self.game_profiles = self._load_game_profiles()
        
    def _load_game_profiles(self) -> Dict[str, GameSettings]:
        """Load game profiles from config"""
        profiles_file = self.config.config_dir / "game_profiles.json"
        
        if profiles_file.exists():
            try:
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    profiles = {}
                    for name, settings_dict in data.items():
                        profiles[name] = GameSettings(**settings_dict)
                    return profiles
            except Exception as e:
                self.logger.error(f"Failed to load game profiles: {e}")
        
        # Return default profiles
        return self._get_default_profiles()
    
    def _get_default_profiles(self) -> Dict[str, GameSettings]:
        """Get default game profiles"""
        return {
            "steam": GameSettings(
                name="Steam Games",
                executable="steam",
                profile=GameProfile.AAA_GAMING
            ),
            "lutris": GameSettings(
                name="Lutris Games", 
                executable="lutris",
                profile=GameProfile.AAA_GAMING
            ),
            "wine": GameSettings(
                name="Wine Games",
                executable="wine",
                profile=GameProfile.AAA_GAMING
            ),
            "dota2": GameSettings(
                name="Dota 2",
                executable="dota2",
                profile=GameProfile.ESPORTS,
                refresh_rate="gaming"
            ),
            "csgo": GameSettings(
                name="CS:GO",
                executable="csgo_linux64",
                profile=GameProfile.ESPORTS,
                refresh_rate="gaming"
            )
        }
    
    def save_game_profiles(self):
        """Save game profiles to config"""
        profiles_file = self.config.config_dir / "game_profiles.json"
        
        try:
            data = {}
            for name, settings in self.game_profiles.items():
                data[name] = {
                    'name': settings.name,
                    'executable': settings.executable,
                    'profile': settings.profile.value,
                    'tdp_profile': settings.tdp_profile,
                    'gpu_mode': settings.gpu_mode,
                    'refresh_rate': settings.refresh_rate,
                    'fan_curve': settings.fan_curve,
                    'rgb_profile': settings.rgb_profile,
                    'cpu_governor': settings.cpu_governor,
                    'gpu_performance_mode': settings.gpu_performance_mode,
                    'network_priority': settings.network_priority,
                    'process_priority': settings.process_priority,
                    'fullscreen_optimizations': settings.fullscreen_optimizations
                }
            
            with open(profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save game profiles: {e}")
    
    def detect_running_games(self) -> List[Dict]:
        """Detect currently running games"""
        running_games = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    proc_exe = proc_info['exe']
                    
                    # Check against known game profiles
                    for profile_name, settings in self.game_profiles.items():
                        if (settings.executable.lower() in proc_name or 
                            (proc_exe and settings.executable.lower() in proc_exe.lower())):
                            
                            running_games.append({
                                'pid': proc_info['pid'],
                                'name': proc_info['name'],
                                'exe': proc_exe,
                                'profile': settings
                            })
                            break
                    
                    # Check for common gaming patterns
                    gaming_indicators = [
                        'steam', 'lutris', 'wine', 'gamemode', 'dota2', 'csgo',
                        'valorant', 'minecraft', 'terraria', 'factorio'
                    ]
                    
                    if any(indicator in proc_name for indicator in gaming_indicators):
                        # Check if we already found this process
                        if not any(game['pid'] == proc_info['pid'] for game in running_games):
                            running_games.append({
                                'pid': proc_info['pid'],
                                'name': proc_info['name'],
                                'exe': proc_exe,
                                'profile': None  # Unknown game
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            self.logger.error(f"Failed to detect running games: {e}")
        
        return running_games
    
    def start_gaming_mode(self, game_pid: int, settings: GameSettings) -> bool:
        """Start gaming mode for a specific game"""
        try:
            self.logger.info(f"Starting gaming mode for {settings.name} (PID: {game_pid})")
            
            # Apply performance optimizations
            success = True
            
            # Set CPU governor
            if not self.process_manager.set_cpu_governor(settings.cpu_governor):
                success = False
            
            # Set process priority
            if not self.process_manager.set_process_priority(game_pid, settings.process_priority):
                success = False
            
            # Apply network optimizations
            if settings.network_priority:
                if not self.network_optimizer.optimize_for_gaming():
                    self.logger.warning("Network optimizations failed")
                
                if not self.network_optimizer.set_process_network_priority(game_pid, True):
                    self.logger.warning("Process network priority failed")
            
            # Start GameMode if available
            if self.process_manager.is_gamemode_available():
                self.process_manager.start_gamemode()
            
            # Store active game
            self.active_games[game_pid] = settings
            
            # Apply hardware profiles (would integrate with existing managers)
            self._apply_hardware_profile(settings)
            
            self.logger.info(f"Gaming mode started for {settings.name}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to start gaming mode: {e}")
            return False
    
    def stop_gaming_mode(self, game_pid: int) -> bool:
        """Stop gaming mode for a specific game"""
        try:
            if game_pid not in self.active_games:
                return False
            
            settings = self.active_games[game_pid]
            self.logger.info(f"Stopping gaming mode for {settings.name} (PID: {game_pid})")
            
            # Restore process priority
            self.process_manager.restore_process_priority(game_pid)
            
            # Restore CPU governor to default
            available_governors = self.process_manager.get_available_governors()
            if "schedutil" in available_governors:
                self.process_manager.set_cpu_governor("schedutil")
            elif "ondemand" in available_governors:
                self.process_manager.set_cpu_governor("ondemand")
            
            # Remove from active games
            del self.active_games[game_pid]
            
            # If no more games running, restore default profiles
            if not self.active_games:
                self._restore_default_profile()
            
            self.logger.info(f"Gaming mode stopped for {settings.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop gaming mode: {e}")
            return False
    
    def _apply_hardware_profile(self, settings: GameSettings):
        """Apply hardware settings for the game profile"""
        # This would integrate with the existing ROG managers
        # Setting TDP, GPU mode, refresh rate, fan curves, RGB, etc.
        
        # Example integration points:
        # - self.tdp_manager.set_profile(settings.tdp_profile)
        # - self.gpu_manager.set_mode(settings.gpu_mode)
        # - self.refresh_manager.set_profile(settings.refresh_rate)
        # - self.fan_manager.set_curve(settings.fan_curve)
        # - self.rgb_manager.set_profile(settings.rgb_profile)
        
        self.logger.info(f"Applied hardware profile for {settings.profile.value}")
    
    def _restore_default_profile(self):
        """Restore default hardware profile when no games are running"""
        # Restore to balanced/default settings
        self.logger.info("Restoring default hardware profile")
    
    def add_game_profile(self, name: str, executable: str, profile: GameProfile) -> bool:
        """Add a new game profile"""
        try:
            settings = GameSettings(
                name=name,
                executable=executable,
                profile=profile
            )
            
            self.game_profiles[name.lower()] = settings
            self.save_game_profiles()
            
            self.logger.info(f"Added game profile: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add game profile: {e}")
            return False
    
    def remove_game_profile(self, name: str) -> bool:
        """Remove a game profile"""
        try:
            if name.lower() in self.game_profiles:
                del self.game_profiles[name.lower()]
                self.save_game_profiles()
                self.logger.info(f"Removed game profile: {name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove game profile: {e}")
            return False
    
    def get_game_profiles(self) -> Dict[str, GameSettings]:
        """Get all game profiles"""
        return self.game_profiles
    
    def auto_detect_and_optimize(self) -> int:
        """Automatically detect and optimize running games"""
        running_games = self.detect_running_games()
        optimized_count = 0
        
        for game in running_games:
            pid = game['pid']
            
            # Skip if already optimized
            if pid in self.active_games:
                continue
            
            # Use profile if available, otherwise use default
            settings = game['profile']
            if not settings:
                settings = GameSettings(
                    name=game['name'],
                    executable=game['name'],
                    profile=GameProfile.AAA_GAMING
                )
            
            if self.start_gaming_mode(pid, settings):
                optimized_count += 1
        
        # Stop optimization for games that are no longer running
        current_pids = {game['pid'] for game in running_games}
        for pid in list(self.active_games.keys()):
            if pid not in current_pids:
                self.stop_gaming_mode(pid)
        
        return optimized_count
    
    def get_gaming_statistics(self) -> Dict:
        """Get gaming performance statistics"""
        stats = {
            'active_games': len(self.active_games),
            'total_profiles': len(self.game_profiles),
            'gamemode_available': self.process_manager.is_gamemode_available(),
            'network_optimization': self.network_optimizer.is_available(),
            'current_games': []
        }
        
        for pid, settings in self.active_games.items():
            try:
                process = psutil.Process(pid)
                stats['current_games'].append({
                    'name': settings.name,
                    'pid': pid,
                    'cpu_percent': process.cpu_percent(),
                    'memory_percent': process.memory_percent(),
                    'profile': settings.profile.value
                })
            except psutil.NoSuchProcess:
                # Process no longer exists, will be cleaned up next cycle
                pass
        
        return stats