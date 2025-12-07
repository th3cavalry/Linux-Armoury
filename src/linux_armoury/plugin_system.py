#!/usr/bin/env python3
"""
Plugin System for Linux Armoury
Provides a foundation for extending functionality through plugins

Plugin API:
- Plugins should be placed in ~/.config/linux-armoury/plugins/
- Each plugin is a Python file with a Plugin class
- Plugin class should implement: on_load(), on_status_update(status_data)
"""

import importlib.util
import os
from typing import Any, Dict, List, Optional


class PluginBase:
    """Base class for plugins"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    def on_load(self):
        """Called when plugin is loaded"""

    def on_status_update(self, status_data: Dict[str, Any]):
        """Called when system status is updated

        Args:
            status_data: Dictionary containing current system status
                - cpu_temp: float (CPU temperature in C)
                - gpu_temp: float (GPU temperature in C)
                - battery: int (battery percentage)
                - on_ac: bool (True if on AC power)
                - refresh_rate: int (current refresh rate in Hz)
                - profile: str (current power profile)
        """

    def on_profile_change(self, old_profile: str, new_profile: str):
        """Called when power profile changes"""

    def get_info(self) -> Dict[str, str]:
        """Return plugin information"""
        return {"name": self.name, "version": "1.0.0", "description": "Base plugin"}


class PluginManager:
    """Manages plugin loading and execution"""

    def __init__(self, plugin_dir: Optional[str] = None):
        if plugin_dir is None:
            config_dir = os.path.expanduser("~/.config/linux-armoury")
            plugin_dir = os.path.join(config_dir, "plugins")

        self.plugin_dir = plugin_dir
        self.plugins: List[PluginBase] = []

        # Create plugin directory if it doesn't exist
        os.makedirs(plugin_dir, exist_ok=True)

        # Create README for plugins
        readme_path = os.path.join(plugin_dir, "README.txt")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write(
                    """Linux Armoury Plugin Directory

Place your plugin files here. Each plugin should be a Python file
with a Plugin class that inherits from PluginBase.

Example plugin (my_plugin.py):

    from plugin_system import PluginBase

    class Plugin(PluginBase):
        def __init__(self):
            super().__init__("My Plugin")

        def on_load(self):
            print("My plugin loaded!")

        def on_status_update(self, status_data):
            # React to status updates
            if status_data.get('cpu_temp', 0) > 80:
                print("Warning: CPU temperature high!")

For more information, visit:
https://github.com/th3cavalry/Linux-Armoury
"""
                )

    def load_plugins(self):
        """Load all plugins from the plugin directory"""
        if not os.path.exists(self.plugin_dir):
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                plugin_path = os.path.join(self.plugin_dir, filename)
                self.load_plugin(plugin_path)

    def load_plugin(self, plugin_path: str) -> Optional[PluginBase]:
        """Load a single plugin from file"""
        try:
            # Load module
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for Plugin class
                if hasattr(module, "Plugin"):
                    plugin = module.Plugin()
                    plugin.on_load()
                    self.plugins.append(plugin)
                    print(f"Loaded plugin: {plugin.name}")
                    return plugin
        except Exception as e:
            print(f"Failed to load plugin {plugin_path}: {e}")

        return None

    def notify_status_update(self, status_data: Dict[str, Any]):
        """Notify all plugins of status update"""
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.on_status_update(status_data)
                except Exception as e:
                    print(f"Plugin {plugin.name} error in on_status_update: {e}")

    def notify_profile_change(self, old_profile: str, new_profile: str):
        """Notify all plugins of profile change"""
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.on_profile_change(old_profile, new_profile)
                except Exception as e:
                    print(f"Plugin {plugin.name} error in on_profile_change: {e}")

    def get_loaded_plugins(self) -> List[Dict[str, str]]:
        """Get information about loaded plugins"""
        return [plugin.get_info() for plugin in self.plugins]

    def enable_plugin(self, name: str):
        """Enable a plugin by name"""
        for plugin in self.plugins:
            if plugin.name == name:
                plugin.enabled = True
                return True
        return False

    def disable_plugin(self, name: str):
        """Disable a plugin by name"""
        for plugin in self.plugins:
            if plugin.name == name:
                plugin.enabled = False
                return True
        return False
