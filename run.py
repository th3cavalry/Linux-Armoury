#!/usr/bin/env python3
"""
Quick start script for Linux Armoury
"""

import sys
import subprocess
from pathlib import Path

def get_pip_command():
    """Get the best available pip command"""
    # Try python -m pip first
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        return [sys.executable, "-m", "pip"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try pip3
    try:
        subprocess.run(["pip3", "--version"], check=True, capture_output=True)
        return ["pip3"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try pip
    try:
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
        return ["pip"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None


def check_venv_dependencies():
    """Check if dependencies are available in a virtual environment"""
    venv_path = Path.home() / ".local" / "share" / "linux-armoury-venv"
    if not venv_path.exists():
        return False
    
    # Try to activate the venv and check for dependencies
    venv_python = venv_path / "bin" / "python"
    if not venv_python.exists():
        return False
    
    try:
        # Check if PySide6 is available in the venv
        result = subprocess.run([
            str(venv_python), "-c", "import PySide6; import psutil; print('OK')"
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and "OK" in result.stdout
    except Exception:
        return False


def main():
    """Quick start the application"""
    
    # Check if we're in the right directory
    if not (Path("linux_armoury").exists() and Path("setup.py").exists()):
        print("Error: Please run this script from the Linux-Armoury directory")
        sys.exit(1)
    
    print("Linux Armoury Quick Start")
    print("=" * 30)
    
    # Check if PySide6 is available
    try:
        import PySide6
        print("✓ PySide6 found")
    except ImportError:
        print("PySide6 not found in system environment...")
        
        # Check if dependencies are available in virtual environment
        if check_venv_dependencies():
            print("✓ Dependencies found in virtual environment")
            launcher_file = Path.home() / ".local" / "bin" / "linux-armoury"
            if launcher_file.exists():
                print(f"Using virtual environment launcher: {launcher_file}")
                try:
                    subprocess.run([str(launcher_file)], check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"✗ Launcher failed: {e}")
                    print("Falling back to manual virtual environment activation...")
            
            # Manual virtual environment activation
            venv_path = Path.home() / ".local" / "share" / "linux-armoury-venv"
            print("Please activate the virtual environment manually:")
            print(f"  source {venv_path}/bin/activate")
            print(f"  python3 -m linux_armoury.main")
            sys.exit(1)
        
        print("Installing PySide6...")
        
        pip_cmd = get_pip_command()
        if not pip_cmd:
            print("✗ Could not find pip")
            print("Please install pip and dependencies manually:")
            print("  Ubuntu/Debian: sudo apt install python3-pip")
            print("  Then: pip install PySide6 psutil")
            sys.exit(1)
        
        try:
            subprocess.run(pip_cmd + ["install", "--user", "PySide6", "psutil"], check=True)
            print("✓ Dependencies installed")
        except subprocess.CalledProcessError as e:
            # Check if this is an externally managed environment error
            if hasattr(e, 'stderr') and e.stderr and "externally-managed-environment" in str(e.stderr):
                print("✗ Externally managed Python environment detected")
                print("Please install dependencies using one of these methods:")
                print("\n1. System package manager:")
                print("   Arch: sudo pacman -S python-pyside6 python-psutil")
                print("   Ubuntu: sudo apt install python3-pyside6 python3-psutil")
                print("   Fedora: sudo dnf install python3-pyside6 python3-psutil")
                print("\n2. Run the full installation script:")
                print("   python3 install.py")
            else:
                print("✗ Failed to install dependencies")
                print("Please install manually: pip install --user PySide6 psutil")
            sys.exit(1)
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path.cwd()))
    
    # Import and run the application
    try:
        from linux_armoury.main import main as app_main
        print("Starting Linux Armoury...")
        app_main()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Try running: python3 install.py first")
        sys.exit(1)

if __name__ == "__main__":
    main()