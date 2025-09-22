"""
Update manager for laptop-specific packages and drivers
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from linux_armoury.core.utils import run_command, check_command_exists


class PackageInfo:
    """Information about a package"""
    
    def __init__(self, name: str, current_version: str = "", available_version: str = "", 
                 description: str = "", category: str = ""):
        self.name = name
        self.current_version = current_version
        self.available_version = available_version
        self.description = description
        self.category = category
        self.update_available = current_version != available_version and available_version != ""
    
    def __repr__(self):
        return f"PackageInfo({self.name}, {self.current_version} -> {self.available_version})"


class UpdateManager:
    """Manager for checking and installing updates for laptop-specific packages"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.distro = self._detect_distro()
        self.package_manager = self._get_package_manager()
        
        # Define ROG/laptop-specific packages by category
        self.rog_packages = {
            "ASUS Control": [
                "asusctl", "rog-control-center", "supergfxctl"
            ],
            "Kernel & Drivers": [
                "linux-g14", "linux-g14-headers", "linux-firmware",
                "mesa", "vulkan-radeon", "amdgpu-pro", "rocm-opencl-runtime"
            ],
            "Power Management": [
                "power-profiles-daemon", "ryzenadj", "switcheroo-control"
            ],
            "Gaming & Graphics": [
                "gamemode", "mangohud", "steam", "lutris", "wine"
            ],
            "System Tools": [
                "psutil", "lm-sensors", "acpi"
            ]
        }
    
    def _detect_distro(self) -> str:
        """Detect the Linux distribution"""
        try:
            success, output = run_command(["lsb_release", "-si"])
            if success:
                return output.lower()
        except:
            pass
        
        # Fallback to checking /etc/os-release
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=")[1].strip().strip('"').lower()
        except:
            pass
        
        return "unknown"
    
    def _get_package_manager(self) -> str:
        """Determine the package manager based on distribution"""
        if self.distro in ["arch", "manjaro", "endeavouros"]:
            return "pacman"
        elif self.distro in ["ubuntu", "debian", "pop", "mint"]:
            return "apt"
        elif self.distro in ["fedora", "rhel", "centos", "nobara"]:
            return "dnf"
        elif self.distro in ["opensuse", "sled", "sles"]:
            return "zypper"
        else:
            # Try to detect by available commands
            for pm in ["pacman", "apt", "dnf", "zypper"]:
                if check_command_exists(pm):
                    return pm
            return "unknown"
    
    def check_updates(self) -> Dict[str, List[PackageInfo]]:
        """Check for updates to ROG-specific packages"""
        self.logger.info("Checking for updates...")
        updates = {}
        
        for category, packages in self.rog_packages.items():
            category_updates = []
            
            for package in packages:
                package_info = self._get_package_info(package)
                if package_info and package_info.update_available:
                    package_info.category = category
                    category_updates.append(package_info)
            
            if category_updates:
                updates[category] = category_updates
        
        self.logger.info(f"Found {sum(len(pkgs) for pkgs in updates.values())} available updates")
        return updates
    
    def _get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get information about a specific package"""
        if self.package_manager == "pacman":
            return self._get_pacman_package_info(package_name)
        elif self.package_manager == "apt":
            return self._get_apt_package_info(package_name)
        elif self.package_manager == "dnf":
            return self._get_dnf_package_info(package_name)
        elif self.package_manager == "zypper":
            return self._get_zypper_package_info(package_name)
        
        return None
    
    def _get_pacman_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get package info from pacman"""
        # Check if package is installed
        success, output = run_command(["pacman", "-Q", package_name])
        if not success:
            return None
        
        current_version = output.split()[1] if output else ""
        
        # Check for updates
        success, output = run_command(["pacman", "-Qu", package_name])
        if success and output:
            available_version = output.split()[1] if output else current_version
        else:
            available_version = current_version
        
        # Get description
        success, desc_output = run_command(["pacman", "-Qi", package_name])
        description = ""
        if success:
            for line in desc_output.split('\n'):
                if line.startswith("Description"):
                    description = line.split(":", 1)[1].strip()
                    break
        
        return PackageInfo(package_name, current_version, available_version, description)
    
    def _get_apt_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get package info from apt"""
        # Check if package is installed
        success, output = run_command(["dpkg", "-l", package_name])
        if not success or "no packages found" in output.lower():
            return None
        
        current_version = ""
        for line in output.split('\n'):
            if package_name in line and line.startswith("ii"):
                parts = line.split()
                if len(parts) >= 3:
                    current_version = parts[2]
                break
        
        if not current_version:
            return None
        
        # Check for updates
        success, output = run_command(["apt", "list", "--upgradable", package_name])
        available_version = current_version
        if success and package_name in output:
            for line in output.split('\n'):
                if package_name in line and "[upgradable" in line:
                    match = re.search(r'(\S+)\s+\[upgradable from:', line)
                    if match:
                        available_version = match.group(1)
                    break
        
        # Get description
        success, desc_output = run_command(["apt", "show", package_name])
        description = ""
        if success:
            for line in desc_output.split('\n'):
                if line.startswith("Description"):
                    description = line.split(":", 1)[1].strip()
                    break
        
        return PackageInfo(package_name, current_version, available_version, description)
    
    def _get_dnf_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get package info from dnf"""
        # Check if package is installed
        success, output = run_command(["rpm", "-q", package_name])
        if not success:
            return None
        
        current_version = output.replace(package_name + "-", "").rsplit(".", 2)[0]
        
        # Check for updates
        success, output = run_command(["dnf", "list", "--updates", package_name])
        available_version = current_version
        if success and package_name in output:
            for line in output.split('\n'):
                if package_name in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        available_version = parts[1]
                    break
        
        # Get description
        success, desc_output = run_command(["dnf", "info", package_name])
        description = ""
        if success:
            for line in desc_output.split('\n'):
                if line.startswith("Summary"):
                    description = line.split(":", 1)[1].strip()
                    break
        
        return PackageInfo(package_name, current_version, available_version, description)
    
    def _get_zypper_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get package info from zypper"""
        # Check if package is installed
        success, output = run_command(["rpm", "-q", package_name])
        if not success:
            return None
        
        current_version = output.replace(package_name + "-", "").rsplit(".", 2)[0]
        
        # Check for updates
        success, output = run_command(["zypper", "list-updates", package_name])
        available_version = current_version
        if success and package_name in output:
            for line in output.split('\n'):
                if package_name in line and "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        available_version = parts[3].strip()
                    break
        
        return PackageInfo(package_name, current_version, available_version)
    
    def install_updates(self, packages: List[str]) -> bool:
        """Install updates for specified packages"""
        if not packages:
            return True
        
        self.logger.info(f"Installing updates for {len(packages)} packages")
        
        if self.package_manager == "pacman":
            success, _ = run_command(["sudo", "pacman", "-S", "--noconfirm"] + packages)
        elif self.package_manager == "apt":
            # Update package list first
            run_command(["sudo", "apt", "update"])
            success, _ = run_command(["sudo", "apt", "install", "-y"] + packages)
        elif self.package_manager == "dnf":
            success, _ = run_command(["sudo", "dnf", "update", "-y"] + packages)
        elif self.package_manager == "zypper":
            success, _ = run_command(["sudo", "zypper", "update", "-y"] + packages)
        else:
            self.logger.error(f"Unsupported package manager: {self.package_manager}")
            return False
        
        if success:
            self.logger.info("Updates installed successfully")
        else:
            self.logger.error("Failed to install some updates")
        
        return success
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information relevant to updates"""
        info = {
            "Distribution": self.distro,
            "Package Manager": self.package_manager
        }
        
        # Get kernel version
        success, output = run_command(["uname", "-r"])
        if success:
            info["Kernel"] = output
        
        # Get ASUS control status
        if check_command_exists("asusctl"):
            success, output = run_command(["asusctl", "--version"])
            if success:
                info["asusctl"] = output.split()[1] if len(output.split()) > 1 else "installed"
        
        if check_command_exists("supergfxctl"):
            info["supergfxctl"] = "installed"
        
        return info