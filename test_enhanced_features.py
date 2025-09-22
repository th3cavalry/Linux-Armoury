#!/usr/bin/env python3
"""
Enhanced test script for Linux Armoury - tests new advanced features
"""

import sys
import os
sys.path.insert(0, '.')

def test_enhanced_hardware_monitoring():
    """Test enhanced hardware monitoring features"""
    print("\nTesting enhanced hardware monitoring...")
    
    try:
        from linux_armoury.core.hardware_monitor import (
            TemperatureMonitor, FanController, PerformanceMonitor, BatteryHealthManager
        )
        
        # Test temperature monitoring
        temp_monitor = TemperatureMonitor()
        temps = temp_monitor.get_temperatures()
        cpu_temp = temp_monitor.get_cpu_temperature()
        
        print(f"✓ Temperature monitoring: {len(temps)} sources found")
        if cpu_temp:
            print(f"✓ CPU Temperature: {cpu_temp}°C")
        else:
            print("✗ CPU temperature not available")
        
        # Test fan control
        fan_controller = FanController()
        fan_speeds = fan_controller.get_fan_speeds()
        print(f"✓ Fan control: {len(fan_speeds)} fans detected")
        
        # Test performance monitoring
        perf_monitor = PerformanceMonitor()
        perf_monitor.update_metrics()
        current_stats = perf_monitor.get_current_stats()
        print("✓ Performance monitoring initialized")
        
        # Test battery health
        battery_manager = BatteryHealthManager()
        battery_info = battery_manager.get_battery_health_info()
        charge_limit = battery_info.get('charge_limit')
        if charge_limit:
            print(f"✓ Battery charge limit: {charge_limit}%")
        else:
            print("✗ Battery charge limit not available")
        
        return True
    except ImportError as e:
        print(f"✗ Enhanced hardware monitoring: {e}")
        return False

def test_rgb_lighting_control():
    """Test RGB lighting control features"""
    print("\nTesting RGB lighting control...")
    
    try:
        from linux_armoury.core.rgb_control import (
            AuraManager, KeyboardLightingManager, MatrixDisplayManager, RGBColor, ColorSchemes
        )
        
        # Test Aura manager
        aura_manager = AuraManager()
        available = aura_manager.is_available()
        zones = aura_manager.get_available_zones()
        
        print(f"✓ Aura management available: {available}")
        print(f"✓ Available zones: {len(zones)}")
        
        # Test keyboard lighting
        keyboard_manager = KeyboardLightingManager()
        kb_available = keyboard_manager.is_available()
        print(f"✓ Keyboard lighting available: {kb_available}")
        
        # Test matrix display
        matrix_manager = MatrixDisplayManager()
        matrix_available = matrix_manager.is_available()
        print(f"✓ Matrix display available: {matrix_available}")
        
        # Test color schemes
        gaming_red = ColorSchemes.GAMING_RED
        temp_color = ColorSchemes.get_temperature_color(65.0)
        print(f"✓ Color schemes: Gaming red {gaming_red.to_hex()}, Temp color {temp_color.to_hex()}")
        
        return True
    except ImportError as e:
        print(f"✗ RGB lighting control: {e}")
        return False

def test_gaming_mode():
    """Test gaming mode optimization features"""
    print("\nTesting gaming mode optimization...")
    
    try:
        from linux_armoury.core.gaming_mode import (
            GameModeManager, ProcessManager, NetworkOptimizer, GameProfile
        )
        
        # Test game mode manager
        game_manager = GameModeManager()
        running_games = game_manager.detect_running_games()
        profiles = game_manager.get_game_profiles()
        
        print(f"✓ Game detection: {len(running_games)} games running")
        print(f"✓ Game profiles: {len(profiles)} profiles available")
        
        # Test process manager
        process_manager = ProcessManager()
        gamemode_available = process_manager.is_gamemode_available()
        governors = process_manager.get_available_governors()
        
        print(f"✓ GameMode available: {gamemode_available}")
        print(f"✓ CPU governors: {', '.join(governors)}")
        
        # Test network optimizer
        network_optimizer = NetworkOptimizer()
        net_available = network_optimizer.is_available()
        print(f"✓ Network optimization available: {net_available}")
        
        # Test gaming statistics
        stats = game_manager.get_gaming_statistics()
        print(f"✓ Gaming statistics: {stats['active_games']} active games")
        
        return True
    except ImportError as e:
        print(f"✗ Gaming mode optimization: {e}")
        return False

def test_audio_enhancement():
    """Test audio enhancement features"""
    print("\nTesting audio enhancement...")
    
    try:
        from linux_armoury.core.audio_manager import (
            AudioProfileManager, PulseAudioManager, EqualizerManager, MicrophoneEnhancer
        )
        
        # Test audio profile manager
        audio_manager = AudioProfileManager()
        profiles = audio_manager.get_available_profiles()
        audio_devices = audio_manager.get_audio_devices()
        
        print(f"✓ Audio profiles: {', '.join(profiles)}")
        print(f"✓ Audio devices: {len(audio_devices.get('sinks', []))} sinks, {len(audio_devices.get('sources', []))} sources")
        
        # Test PulseAudio manager
        pulse_manager = PulseAudioManager()
        pulse_available = pulse_manager.is_available()
        print(f"✓ PulseAudio available: {pulse_available}")
        
        # Test equalizer
        equalizer = EqualizerManager()
        eq_available = equalizer.is_available()
        gaming_preset = equalizer.get_preset_bands('gaming')
        print(f"✓ Equalizer available: {eq_available}")
        print(f"✓ Gaming EQ preset: {len(gaming_preset)} bands")
        
        # Test microphone enhancer
        mic_enhancer = MicrophoneEnhancer()
        mic_available = mic_enhancer.is_available()
        print(f"✓ Microphone enhancement available: {mic_available}")
        
        # Test audio status
        status = audio_manager.get_audio_status()
        features = status['features']
        print(f"✓ Audio features: EQ={features['equalizer']}, Mic={features['microphone_enhancement']}")
        
        return True
    except ImportError as e:
        print(f"✗ Audio enhancement: {e}")
        return False

def test_enhanced_rog_integration():
    """Test enhanced ROG integration features"""
    print("\nTesting enhanced ROG integration...")
    
    try:
        from linux_armoury.core.rog_integration import (
            DisplayManager, PowerManagementManager
        )
        
        # Test display manager
        display_manager = DisplayManager()
        display_available = display_manager.is_available()
        brightness = display_manager.get_brightness()
        panel_od_status = display_manager.get_panel_overdrive_status()
        
        print(f"✓ Display management available: {display_available}")
        if brightness is not None:
            print(f"✓ Current brightness: {brightness}%")
        else:
            print("✗ Brightness control not available")
        
        print(f"✓ Panel overdrive: {panel_od_status.get('available', False)}")
        
        # Test power management
        power_manager = PowerManagementManager()
        power_available = power_manager.is_available()
        platform_profile = power_manager.get_platform_profile()
        available_profiles = power_manager.get_available_platform_profiles()
        cpu_boost = power_manager.get_cpu_boost_status()
        
        print(f"✓ Power management available: {power_available}")
        if platform_profile:
            print(f"✓ Platform profile: {platform_profile}")
        print(f"✓ Available profiles: {', '.join(available_profiles)}")
        
        if cpu_boost is not None:
            print(f"✓ CPU boost: {'enabled' if cpu_boost else 'disabled'}")
        else:
            print("✗ CPU boost status not available")
        
        return True
    except ImportError as e:
        print(f"✗ Enhanced ROG integration: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Linux Armoury - Enhanced Features Test")
    print("=" * 60)
    
    # Test all enhanced features
    test_results = {
        "Enhanced Hardware Monitoring": test_enhanced_hardware_monitoring(),
        "RGB Lighting Control": test_rgb_lighting_control(),
        "Gaming Mode Optimization": test_gaming_mode(),
        "Audio Enhancement": test_audio_enhancement(),
        "Enhanced ROG Integration": test_enhanced_rog_integration()
    }
    
    print("\n" + "=" * 60)
    print("Enhanced Features Test Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for feature, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{feature}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} enhanced features working")
    
    if passed == total:
        print("\n🎉 All enhanced features are working!")
        print("Linux Armoury now has advanced capabilities inspired by:")
        print("  • ROG Control Center (fan curves, RGB, hardware monitoring)")
        print("  • G-Helper (auto optimization, performance monitoring)")
        print("  • Armoury Crate (gaming profiles, audio enhancement)")
    elif passed > 0:
        print(f"\n✓ {passed} enhanced features are working")
        print("Some features may not be available in this environment")
    else:
        print("\n⚠️ Enhanced features need dependencies or hardware support")
    
    return 0 if passed > 0 else 1

if __name__ == "__main__":
    sys.exit(main())