# Plugin System Documentation

## Overview

Linux Armoury includes a simple plugin system that allows you to extend its functionality without modifying the core application code.

## Plugin Directory

Plugins are stored in: `~/.config/linux-armoury/plugins/`

The directory is automatically created when Linux Armoury starts. A README.txt file in that directory provides basic instructions.

## Creating a Plugin

### Basic Structure

Create a Python file in the plugins directory with a `Plugin` class:

```python
from plugin_system import PluginBase

class Plugin(PluginBase):
    def __init__(self):
        super().__init__("My Plugin Name")
    
    def on_load(self):
        """Called when plugin is loaded"""
        print(f"{self.name} loaded!")
    
    def on_status_update(self, status_data):
        """Called every 2 seconds with current system status"""
        cpu_temp = status_data.get('cpu_temp')
        if cpu_temp and cpu_temp > 80:
            print(f"Warning: CPU is hot! {cpu_temp}°C")
    
    def on_profile_change(self, old_profile, new_profile):
        """Called when power profile changes"""
        print(f"Profile changed: {old_profile} → {new_profile}")
    
    def get_info(self):
        """Return plugin metadata"""
        return {
            'name': self.name,
            'version': '1.0.0',
            'description': 'My custom plugin',
            'author': 'Your Name'
        }
```

### Available Callbacks

#### `on_load()`
Called when the plugin is first loaded. Use this for initialization.

#### `on_status_update(status_data)`
Called periodically (every 2 seconds) with current system status.

**status_data dictionary contains:**
- `cpu_temp`: float - CPU temperature in Celsius
- `gpu_temp`: float - GPU temperature in Celsius  
- `battery`: int - Battery percentage (0-100)
- `on_ac`: bool - True if on AC power
- `refresh_rate`: int - Current refresh rate in Hz
- `profile`: str - Current power profile name

#### `on_profile_change(old_profile, new_profile)`
Called when the power profile changes.

**Parameters:**
- `old_profile`: str - Previous profile name
- `new_profile`: str - New profile name

#### `get_info()`
Returns a dictionary with plugin metadata.

## Example Plugins

### Temperature Monitor

See `examples/plugins/temperature_alert.py` for a complete example that:
- Monitors CPU temperature
- Alerts when temperature exceeds thresholds
- Logs profile changes

### Custom Profile Switcher

```python
from plugin_system import PluginBase

class Plugin(PluginBase):
    def __init__(self):
        super().__init__("Smart Switcher")
        self.last_gaming = False
    
    def on_status_update(self, status_data):
        from system_utils import SystemUtils
        
        gaming_active = SystemUtils.detect_gaming_apps()
        
        # Switch to gaming profile when game detected
        if gaming_active and not self.last_gaming:
            print("🎮 Game detected! Consider switching to gaming profile")
        
        self.last_gaming = gaming_active
```

## Plugin Management

### Loading Plugins

Plugins are automatically loaded from `~/.config/linux-armoury/plugins/` when the application starts.

### Enabling/Disabling Plugins

Currently, plugins can be disabled by:
1. Renaming the file (add `.disabled` extension)
2. Removing the file from the plugins directory
3. Setting `self.enabled = False` in the plugin code

Future versions will include GUI management.

## Best Practices

1. **Keep it Simple**: Plugins should be lightweight and focused
2. **Handle Errors**: Wrap your code in try/except to avoid crashes
3. **Be Efficient**: Avoid heavy computations in `on_status_update()`
4. **Test Standalone**: Use `if __name__ == "__main__":` for testing
5. **Document**: Add docstrings and comments

## Debugging

To test a plugin:

```bash
python3 your_plugin.py
```

Check application logs for plugin loading messages and errors.

## Limitations

Current limitations (may be improved in future versions):
- No GUI for plugin management
- Limited API surface
- No plugin dependencies
- No sandboxing (plugins run with full application permissions)

## Future Enhancements

Planned features:
- GUI plugin manager
- Plugin marketplace/repository
- Extended API (custom UI elements, notifications, etc.)
- Plugin settings storage
- Inter-plugin communication

## Support

For questions or issues:
- GitHub Issues: https://github.com/th3cavalry/Linux-Armoury/issues
- Discussions: https://github.com/th3cavalry/Linux-Armoury/discussions

## License

Plugins you create are your own code. The plugin system itself is GPL-3.0 licensed as part of Linux Armoury.
