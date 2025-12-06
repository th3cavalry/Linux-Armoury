#!/usr/bin/env python3
"""
Unit tests for plugin_system.py
"""

import tempfile
import shutil

import pytest
from linux_armoury.plugin_system import PluginBase, PluginManager


class TestPluginBase:
    """Test cases for PluginBase class"""
    
    def test_plugin_base_init(self):
        """Test PluginBase initialization"""
        plugin = PluginBase("TestPlugin")
        assert plugin.name == "TestPlugin"
        assert plugin.enabled == True
    
    def test_plugin_base_get_info(self):
        """Test PluginBase get_info method"""
        plugin = PluginBase("TestPlugin")
        info = plugin.get_info()
        assert isinstance(info, dict)
        assert "name" in info
        assert "version" in info
        assert "description" in info
    
    def test_plugin_base_on_load(self):
        """Test PluginBase on_load method (should not raise)"""
        plugin = PluginBase("TestPlugin")
        plugin.on_load()
    
    def test_plugin_base_on_status_update(self):
        """Test PluginBase on_status_update method"""
        plugin = PluginBase("TestPlugin")
        status_data = {"cpu_temp": 50.0, "battery": 80}
        plugin.on_status_update(status_data)
    
    def test_plugin_base_on_profile_change(self):
        """Test PluginBase on_profile_change method"""
        plugin = PluginBase("TestPlugin")
        plugin.on_profile_change("balanced", "performance")


class TestPluginManager:
    """Test cases for PluginManager class"""
    
    def setup_method(self):
        """Create a temporary plugin directory for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PluginManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_manager_init(self):
        """Test PluginManager initialization"""
        assert os.path.exists(self.temp_dir)
        assert self.manager.plugins == []
    
    def test_plugin_manager_creates_readme(self):
        """Test that PluginManager creates README.txt"""
        readme_path = os.path.join(self.temp_dir, "README.txt")
        assert os.path.exists(readme_path)
    
    def test_plugin_manager_load_plugins_empty(self):
        """Test loading plugins from empty directory"""
        self.manager.load_plugins()
        assert len(self.manager.plugins) == 0
    
    def test_plugin_manager_notify_status_update(self):
        """Test notifying plugins of status update"""
        status_data = {"cpu_temp": 50.0}
        self.manager.notify_status_update(status_data)
    
    def test_plugin_manager_notify_profile_change(self):
        """Test notifying plugins of profile change"""
        self.manager.notify_profile_change("balanced", "gaming")
    
    def test_plugin_manager_get_loaded_plugins(self):
        """Test getting list of loaded plugins"""
        result = self.manager.get_loaded_plugins()
        assert isinstance(result, list)
    
    def test_plugin_manager_enable_disable_nonexistent(self):
        """Test enabling/disabling nonexistent plugin"""
        assert self.manager.enable_plugin("nonexistent") == False
        assert self.manager.disable_plugin("nonexistent") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
