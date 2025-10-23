#!/usr/bin/env python3
"""
Example Plugin: Temperature Alert
Demonstrates the Linux Armoury plugin system

This plugin monitors CPU temperature and logs alerts when it exceeds thresholds.
"""

import sys
import os

# Add parent directory to path to import PluginBase
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from plugin_system import PluginBase
except ImportError:
    # Fallback if plugin_system not in path
    class PluginBase:
        def __init__(self, name):
            self.name = name
            self.enabled = True


class Plugin(PluginBase):
    """Temperature monitoring plugin"""
    
    def __init__(self):
        super().__init__("Temperature Alert")
        self.high_temp_threshold = 80
        self.critical_temp_threshold = 90
        self.last_alert_level = None
    
    def on_load(self):
        """Called when plugin is loaded"""
        print(f"[{self.name}] Plugin loaded")
        print(f"[{self.name}] Monitoring temperature (High: {self.high_temp_threshold}°C, Critical: {self.critical_temp_threshold}°C)")
    
    def on_status_update(self, status_data):
        """Monitor temperature and alert on high values"""
        cpu_temp = status_data.get('cpu_temp')
        
        if cpu_temp is None:
            return
        
        # Check thresholds
        if cpu_temp >= self.critical_temp_threshold:
            if self.last_alert_level != 'critical':
                print(f"\n[{self.name}] 🚨 CRITICAL: CPU temperature is {cpu_temp:.1f}°C!")
                self.last_alert_level = 'critical'
        elif cpu_temp >= self.high_temp_threshold:
            if self.last_alert_level != 'high':
                print(f"\n[{self.name}] ⚠️  WARNING: CPU temperature is {cpu_temp:.1f}°C")
                self.last_alert_level = 'high'
        else:
            # Temperature is normal
            if self.last_alert_level is not None:
                print(f"\n[{self.name}] ✓ Temperature normalized: {cpu_temp:.1f}°C")
                self.last_alert_level = None
    
    def on_profile_change(self, old_profile, new_profile):
        """Log profile changes"""
        print(f"\n[{self.name}] Profile changed: {old_profile} → {new_profile}")
    
    def get_info(self):
        """Return plugin information"""
        return {
            'name': self.name,
            'version': '1.0.0',
            'description': 'Monitors CPU temperature and alerts on high values',
            'author': 'Linux Armoury',
        }


# Allow running standalone for testing
if __name__ == "__main__":
    print("Temperature Alert Plugin - Standalone Test")
    plugin = Plugin()
    plugin.on_load()
    
    # Test status update
    test_status = {
        'cpu_temp': 85.5,
        'gpu_temp': 70.0,
        'battery': 50,
        'on_ac': True,
        'refresh_rate': 120,
        'profile': 'performance'
    }
    
    plugin.on_status_update(test_status)
    
    # Test profile change
    plugin.on_profile_change('performance', 'gaming')
    
    print("\nPlugin info:")
    for key, value in plugin.get_info().items():
        print(f"  {key}: {value}")
