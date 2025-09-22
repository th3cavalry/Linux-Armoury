#!/usr/bin/env python3
"""
Test script for Linux Armoury - tests core functionality without GUI
"""

import sys
import os
sys.path.insert(0, '.')

def test_core_modules():
    """Test core modules"""
    print("Testing core modules...")
    
    try:
        from linux_armoury.core.config import Config
        config = Config()
        print("✓ Configuration system")
        
        from linux_armoury.core.utils import get_battery_info, get_cpu_info, get_memory_info, format_bytes
        battery = get_battery_info()
        cpu = get_cpu_info()
        memory = get_memory_info()
        
        print(f"✓ Battery: {battery['percent']}% ({'AC' if battery['plugged'] else 'Battery'})")
        print(f"✓ CPU: {cpu['usage']:.1f}% @ {cpu['frequency']:.0f}MHz, {cpu['temperature']:.1f}°C")
        print(f"✓ Memory: {format_bytes(memory['used'])}/{format_bytes(memory['total'])} ({memory['percent']:.1f}%)")
        
        from linux_armoury.core.rog_integration import TDPManager, RefreshRateManager, ASUSCtlManager
        tdp = TDPManager()
        refresh = RefreshRateManager()
        asus = ASUSCtlManager()
        
        print(f"✓ TDP Manager available: {tdp.is_available()}")
        print(f"✓ Refresh Rate Manager available: {refresh.is_available()}")
        print(f"✓ ASUS Control available: {asus.is_available()}")
        
        from linux_armoury.core.update_manager import UpdateManager
        update_mgr = UpdateManager()
        sys_info = update_mgr.get_system_info()
        
        print(f"✓ Update Manager: {update_mgr.package_manager}")
        print(f"✓ Distribution: {sys_info.get('Distribution', 'unknown')}")
        print(f"✓ Kernel: {sys_info.get('Kernel', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Core module error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rog_tools():
    """Test ROG-specific tools availability"""
    print("\nTesting ROG tools availability...")
    
    from linux_armoury.core.utils import check_command_exists
    
    tools = {
        "asusctl": "ASUS laptop control utility",
        "supergfxctl": "GPU switching control", 
        "gz302-tdp": "TDP management script",
        "gz302-refresh": "Refresh rate management script",
        "ryzenadj": "AMD TDP control utility"
    }
    
    available_count = 0
    for tool, description in tools.items():
        if check_command_exists(tool):
            print(f"✓ {tool} - {description}")
            available_count += 1
        else:
            print(f"✗ {tool} - {description} (not found)")
    
    print(f"\nROG tools available: {available_count}/{len(tools)}")
    return available_count > 0

def test_ui_imports():
    """Test UI module imports (without creating widgets)"""
    print("\nTesting UI module imports...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        print("✓ PySide6 available")
        
        # Test UI module imports without creating widgets
        import linux_armoury.ui.main_window
        import linux_armoury.ui.tray_icon  
        import linux_armoury.ui.update_tab
        print("✓ All UI modules import successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ PySide6 not available: {e}")
        print("  Install with: pip install PySide6")
        return False
    except Exception as e:
        print(f"✗ UI module error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("Linux Armoury - Core Functionality Test")
    print("=" * 50)
    
    # Test core modules
    core_ok = test_core_modules()
    
    # Test ROG tools
    rog_tools_ok = test_rog_tools()
    
    # Test UI imports
    ui_ok = test_ui_imports()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Core modules: {'✓ PASS' if core_ok else '✗ FAIL'}")
    print(f"ROG tools: {'✓ PASS' if rog_tools_ok else '✗ FAIL (some missing)'}")
    print(f"UI modules: {'✓ PASS' if ui_ok else '✗ FAIL (PySide6 missing)'}")
    
    if core_ok:
        print("\n✓ Linux Armoury core functionality is working!")
        if not ui_ok:
            print("  Install PySide6 to run the GUI: pip install PySide6")
        if not rog_tools_ok:
            print("  Install ROG tools for full functionality")
    else:
        print("\n✗ Core functionality test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())