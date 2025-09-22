#!/usr/bin/env python3
"""
Installation script for Linux Armoury
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    
    # Check for Qt
    try:
        import PySide6
        print("✓ PySide6 found")
    except ImportError:
        print("✗ PySide6 not found - will install")
    
    # Check for psutil
    try:
        import psutil
        print("✓ psutil found")
    except ImportError:
        print("✗ psutil not found - will install")
    
    return True


def check_pip_available():
    """Check if pip is available and return the best pip command"""
    # Try python -m pip first (preferred method)
    success, _, _ = run_command(f"{sys.executable} -m pip --version")
    if success:
        return f"{sys.executable} -m pip"
    
    # Try pip3 command
    success, _, _ = run_command("pip3 --version")
    if success:
        return "pip3"
    
    # Try pip command
    success, _, _ = run_command("pip --version")
    if success:
        return "pip"
    
    # Try to install pip using ensurepip
    print("Pip not found, attempting to install using ensurepip...")
    success, _, stderr = run_command(f"{sys.executable} -m ensurepip --user")
    if success:
        return f"{sys.executable} -m pip"
    
    return None


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    
    # Check for pip availability
    pip_command = check_pip_available()
    
    if not pip_command:
        print("✗ Could not find or install pip")
        print("Please install pip manually:")
        print("  Ubuntu/Debian: sudo apt install python3-pip")
        print("  Fedora: sudo dnf install python3-pip")
        print("  Arch: sudo pacman -S python-pip")
        print("  Or follow: https://pip.pypa.io/en/stable/installation/")
        return False
    
    # Install with pip
    success, stdout, stderr = run_command(f"{pip_command} install --user -r requirements.txt")
    
    if success:
        print("✓ Dependencies installed successfully")
        return True
    else:
        print(f"✗ Failed to install dependencies: {stderr}")
        print("You may need to install dependencies manually:")
        print("pip install PySide6 psutil")
        return False


def install_application():
    """Install the application"""
    print("Installing Linux Armoury...")
    
    # Check for pip availability
    pip_command = check_pip_available()
    
    if not pip_command:
        print("✗ Could not find pip for application installation")
        return False
    
    # Install in development mode
    success, stdout, stderr = run_command(f"{pip_command} install --user -e .")
    
    if success:
        print("✓ Application installed successfully")
        return True
    else:
        print(f"✗ Failed to install application: {stderr}")
        return False


def create_desktop_entry():
    """Create desktop entry"""
    print("Creating desktop entry...")
    
    # Get the installation path
    try:
        import linux_armoury
        app_path = Path(linux_armoury.__file__).parent
    except ImportError:
        app_path = Path(__file__).parent / "linux_armoury"
    
    icon_path = app_path / "assets" / "icon.svg"
    
    desktop_content = f"""[Desktop Entry]
Name=Linux Armoury
Comment=ASUS ROG Laptop Control GUI
Exec=linux-armoury
Icon={icon_path}
Terminal=false
Type=Application
Categories=System;Settings;HardwareSettings;
StartupNotify=true
Keywords=ASUS;ROG;TDP;GPU;refresh;rate;
"""
    
    # Create desktop entry
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = desktop_dir / "linux-armoury.desktop"
    with open(desktop_file, 'w') as f:
        f.write(desktop_content)
    
    # Make executable
    os.chmod(desktop_file, 0o755)
    
    print("✓ Desktop entry created")


def check_rog_tools():
    """Check for ROG-specific tools"""
    print("Checking for ROG tools...")
    
    tools = {
        "asusctl": "ASUS control utility",
        "supergfxctl": "GPU switching control",
        "gz302-tdp": "TDP management script",
        "gz302-refresh": "Refresh rate management script"
    }
    
    available_tools = []
    missing_tools = []
    
    for tool, description in tools.items():
        if shutil.which(tool):
            print(f"✓ {tool} - {description}")
            available_tools.append(tool)
        else:
            print(f"✗ {tool} - {description} (not found)")
            missing_tools.append(tool)
    
    if missing_tools:
        print("\nMissing tools:")
        if "asusctl" in missing_tools:
            print("  - Install asusctl from your package manager or AUR")
        if "supergfxctl" in missing_tools:
            print("  - Install supergfxctl from your package manager or AUR")
        if "gz302-tdp" in missing_tools:
            print("  - Install from: https://github.com/th3cavalry/GZ302-Linux-Setup")
        if "gz302-refresh" in missing_tools:
            print("  - Install from: https://github.com/th3cavalry/GZ302-Linux-Setup")
    
    return len(available_tools) > 0


def main():
    """Main installation function"""
    print("Linux Armoury Installation Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("Error: Please run this script from the Linux Armoury directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. You may need to install them manually:")
        print("pip install PySide6 psutil")
        sys.exit(1)
    
    # Install application
    if not install_application():
        sys.exit(1)
    
    # Create desktop entry
    create_desktop_entry()
    
    # Check ROG tools
    rog_tools_available = check_rog_tools()
    
    print("\n" + "=" * 40)
    print("Installation completed!")
    print("\nTo start Linux Armoury:")
    print("  - Run 'linux-armoury' from terminal")
    print("  - Or find 'Linux Armoury' in your application menu")
    
    if not rog_tools_available:
        print("\nNote: Some ROG-specific features may not work without the")
        print("required tools. See the installation instructions above.")
    
    print("\nFor ASUS ROG Flow Z13 (GZ302) users:")
    print("Consider installing the GZ302 setup script for full functionality:")
    print("https://github.com/th3cavalry/GZ302-Linux-Setup")


if __name__ == "__main__":
    main()