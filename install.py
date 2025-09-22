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
    
    # Try installing with --user first
    success, stdout, stderr = run_command(f"{pip_command} install --user -r requirements.txt")
    
    if success:
        print("✓ Dependencies installed successfully")
        return True
    
    # Check if this is an externally managed environment error
    if "externally-managed-environment" in stderr:
        print("✗ Detected externally managed Python environment (PEP 668)")
        print("Trying alternative installation methods...")
        
        # Try creating a virtual environment
        venv_success = try_virtual_environment_install()
        if venv_success:
            return True
        
        # Provide distribution-specific guidance
        provide_distro_specific_guidance()
        return False
    else:
        print(f"✗ Failed to install dependencies: {stderr}")
        print("You may need to install dependencies manually:")
        print("pip install --user PySide6 psutil")
        return False


def install_application():
    """Install the application"""
    print("Installing Linux Armoury...")
    
    # Check for pip availability
    pip_command = check_pip_available()
    
    if not pip_command:
        print("✗ Could not find pip for application installation")
        return False
    
    # Try installing in development mode with --user
    success, stdout, stderr = run_command(f"{pip_command} install --user -e .")
    
    if success:
        print("✓ Application installed successfully")
        return True
    
    # Check if this is an externally managed environment error
    if "externally-managed-environment" in stderr:
        print("✗ Cannot install application in externally managed environment")
        print("Please use one of these methods:")
        print("\n1. Virtual environment (recommended):")
        print("   python3 -m venv ~/.local/share/linux-armoury-venv")
        print("   source ~/.local/share/linux-armoury-venv/bin/activate")
        print("   pip install -e .")
        print("\n2. Run directly without installation:")
        print("   python3 -m linux_armoury.main")
        print("\n3. Force install (NOT RECOMMENDED):")
        print("   pip install --break-system-packages --user -e .")
        return False
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


def try_virtual_environment_install():
    """Try to install dependencies in a virtual environment"""
    print("Attempting to create a virtual environment for installation...")
    
    venv_path = Path.home() / ".local" / "share" / "linux-armoury-venv"
    
    # Create virtual environment
    success, stdout, stderr = run_command(f"{sys.executable} -m venv {venv_path}")
    if not success:
        print(f"✗ Failed to create virtual environment: {stderr}")
        return False
    
    # Install dependencies in virtual environment
    venv_pip = venv_path / "bin" / "pip"
    if not venv_pip.exists():
        print("✗ Virtual environment pip not found")
        return False
    
    # Use the virtual environment's pip which should bypass externally managed restrictions
    success, stdout, stderr = run_command(f"{venv_pip} install PySide6 psutil")
    if not success:
        print(f"✗ Failed to install dependencies in virtual environment: {stderr}")
        return False
    
    print("✓ Dependencies installed in virtual environment")
    print(f"Virtual environment created at: {venv_path}")
    print("Note: You'll need to activate this environment to use the application:")
    print(f"  source {venv_path}/bin/activate")
    print(f"  python3 -m linux_armoury.main")
    return True


def provide_distro_specific_guidance():
    """Provide distribution-specific guidance for installing dependencies"""
    print("\nAlternative installation methods:")
    print("\n1. Use system package manager:")
    print("   Arch/Manjaro/EndeavourOS:")
    print("     sudo pacman -S python-pyside6 python-psutil")
    print("   Ubuntu/Debian/Pop!_OS:")
    print("     sudo apt install python3-pyside6 python3-psutil")
    print("   Fedora/Nobara:")
    print("     sudo dnf install python3-pyside6 python3-psutil")
    print("   OpenSUSE:")
    print("     sudo zypper install python3-pyside6 python3-psutil")
    
    print("\n2. Use pipx (recommended for applications):")
    print("   pipx install linux-armoury")
    print("   (Note: You may need to install pipx first)")
    
    print("\n3. Create a virtual environment manually:")
    print("   python3 -m venv ~/.local/share/linux-armoury-venv")
    print("   source ~/.local/share/linux-armoury-venv/bin/activate")
    print("   pip install PySide6 psutil")
    print("   pip install -e .")
    
    print("\n4. Force install (NOT RECOMMENDED - may break system):")
    print("   pip install --break-system-packages --user PySide6 psutil")


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
    deps_installed = install_dependencies()
    if not deps_installed:
        print("\nFailed to install dependencies automatically.")
        print("Please install them manually using one of the methods above,")
        print("then run this script again or run the application directly:")
        print("  python3 -m linux_armoury.main")
        sys.exit(1)
    
    # Install application
    app_installed = install_application()
    if not app_installed:
        print("\nApplication installation failed, but dependencies are available.")
        print("You can still run the application directly:")
        print("  python3 -m linux_armoury.main")
        # Don't exit here - continue with desktop entry creation
    
    # Create desktop entry (only if application was installed successfully)
    if app_installed:
        create_desktop_entry()
    else:
        print("Skipping desktop entry creation due to installation issues.")
    
    # Check ROG tools
    rog_tools_available = check_rog_tools()
    
    print("\n" + "=" * 40)
    if app_installed:
        print("Installation completed!")
        print("\nTo start Linux Armoury:")
        print("  - Run 'linux-armoury' from terminal")
        print("  - Or find 'Linux Armoury' in your application menu")
    else:
        print("Setup completed with limited functionality!")
        print("\nTo start Linux Armoury:")
        print("  - Run 'python3 -m linux_armoury.main' from this directory")
    
    if not rog_tools_available:
        print("\nNote: Some ROG-specific features may not work without the")
        print("required tools. See the installation instructions above.")
    
    print("\nFor ASUS ROG Flow Z13 (GZ302) users:")
    print("Consider installing the GZ302 setup script for full functionality:")
    print("https://github.com/th3cavalry/GZ302-Linux-Setup")


if __name__ == "__main__":
    main()