#!/usr/bin/env python3
"""
Quick start script for Linux Armoury
"""

import sys
import subprocess
from pathlib import Path

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
        print("Installing PySide6...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "PySide6", "psutil"], check=True)
            print("✓ Dependencies installed")
        except subprocess.CalledProcessError:
            print("✗ Failed to install dependencies")
            print("Please install manually: pip install PySide6 psutil")
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