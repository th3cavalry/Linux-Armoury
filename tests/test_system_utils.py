#!/usr/bin/env python3
"""
Unit tests for system_utils.py
"""

import pytest
from unittest.mock import patch, MagicMock
from linux_armoury.system_utils import SystemUtils, DisplayBackend


class TestDisplayBackend:
    """Test cases for DisplayBackend detection"""
    
    def test_display_backend_x11(self):
        """Test X11 detection"""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11", "DISPLAY": ":0"}, clear=False):
            result = SystemUtils.get_display_backend()
            assert result == DisplayBackend.X11
    
    def test_display_backend_wayland(self):
        """Test Wayland detection"""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"}, clear=False):
            result = SystemUtils.get_display_backend()
            assert result == DisplayBackend.WAYLAND


class TestCheckCommandExists:
    """Test cases for command existence checking"""
    
    def test_command_exists_true(self):
        """Test with a command that should exist"""
        assert SystemUtils.check_command_exists("ls") == True
    
    def test_command_exists_false(self):
        """Test with a command that should not exist"""
        assert SystemUtils.check_command_exists("nonexistent_command_xyz123") == False


class TestTemperature:
    """Test cases for temperature reading"""
    
    def test_cpu_temperature_returns_float_or_none(self):
        """Test CPU temperature returns correct type"""
        temp = SystemUtils.get_cpu_temperature()
        assert temp is None or isinstance(temp, float)
    
    def test_cpu_temperature_reasonable_range(self):
        """Test CPU temperature is in reasonable range if available"""
        temp = SystemUtils.get_cpu_temperature()
        if temp is not None:
            assert 0 < temp < 150


class TestBattery:
    """Test cases for battery detection"""
    
    def test_is_on_ac_power_returns_bool(self):
        """Test AC power detection returns boolean"""
        result = SystemUtils.is_on_ac_power()
        assert isinstance(result, bool)
    
    def test_battery_percentage_returns_int_or_none(self):
        """Test battery percentage returns correct type"""
        result = SystemUtils.get_battery_percentage()
        assert result is None or isinstance(result, int)
    
    def test_battery_percentage_valid_range(self):
        """Test battery percentage is in valid range if available"""
        result = SystemUtils.get_battery_percentage()
        if result is not None:
            assert 0 <= result <= 100


class TestLaptopDetection:
    """Test cases for laptop detection"""
    
    def test_detect_laptop_model_returns_dict_or_none(self):
        """Test laptop model detection returns correct type"""
        result = SystemUtils.detect_laptop_model()
        assert result is None or isinstance(result, dict)
    
    def test_is_asus_laptop_returns_bool(self):
        """Test ASUS detection returns boolean"""
        result = SystemUtils.is_asus_laptop()
        assert isinstance(result, bool)
    
    def test_get_supported_models_returns_list(self):
        """Test supported models returns list"""
        result = SystemUtils.get_supported_models()
        assert isinstance(result, list)
        assert len(result) > 0


class TestDisplay:
    """Test cases for display functions"""
    
    def test_get_primary_display_returns_string(self):
        """Test primary display returns string"""
        result = SystemUtils.get_primary_display()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_display_resolution_returns_tuple(self):
        """Test display resolution returns tuple"""
        result = SystemUtils.get_display_resolution()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)
    
    def test_get_current_refresh_rate_returns_int_or_none(self):
        """Test refresh rate returns correct type"""
        result = SystemUtils.get_current_refresh_rate()
        assert result is None or isinstance(result, int)


class TestProcessDetection:
    """Test cases for process detection"""
    
    def test_get_running_processes_returns_list(self):
        """Test running processes returns list"""
        result = SystemUtils.get_running_processes()
        assert isinstance(result, list)
    
    def test_detect_gaming_apps_returns_bool(self):
        """Test gaming app detection returns boolean"""
        result = SystemUtils.detect_gaming_apps()
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
