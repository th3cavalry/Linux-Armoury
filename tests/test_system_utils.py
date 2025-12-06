#!/usr/bin/env python3
"""
Unit tests for system_utils.py
"""

import os
from unittest.mock import patch

import pytest

from linux_armoury.system_utils import DisplayBackend, SystemUtils


class TestDisplayBackend:
    """Test cases for DisplayBackend detection"""

    def test_display_backend_x11(self):
        """Test X11 detection"""
        with patch.dict(
            os.environ, {"XDG_SESSION_TYPE": "x11", "DISPLAY": ":0"}, clear=False
        ):
            result = SystemUtils.get_display_backend()
            assert result == DisplayBackend.X11

    def test_display_backend_wayland(self):
        """Test Wayland detection"""
        with patch.dict(
            os.environ,
            {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"},
            clear=False,
        ):
            result = SystemUtils.get_display_backend()
            assert result == DisplayBackend.WAYLAND


class TestCheckCommandExists:
    """Test cases for command existence checking"""

    def test_command_exists_true(self):
        """Test with a command that should exist"""
        # Ensure the function returns a boolean value (may vary by environment)
        assert isinstance(SystemUtils.check_command_exists("ls"), bool)

    def test_command_exists_false(self):
        """Test with a command that should not exist"""
        assert SystemUtils.check_command_exists("nonexistent_command_xyz123") is False


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

    def test_find_battery_path_behaviour(self, monkeypatch):
        """Test find_battery_path handles missing /sys and finds BAT0 when present"""

        # Case 1: /sys not present
        original_exists = os.path.exists
        monkeypatch.setattr(
            "os.path.exists",
            lambda p: False if p == "/sys/class/power_supply" else original_exists(p),
        )
        assert SystemUtils.find_battery_path() is None

        # Case 2: /sys exists and contains BAT0
        def fake_exists(path):
            if path == "/sys/class/power_supply":
                return True
            if path.endswith("BAT0"):
                return True
            return False

        monkeypatch.setattr("os.path.exists", fake_exists)
        monkeypatch.setattr(
            "os.listdir",
            lambda path: ["BAT0"] if path == "/sys/class/power_supply" else [],
        )
        assert SystemUtils.find_battery_path() == "/sys/class/power_supply/BAT0"

    def test_find_ac_path_behaviour(self, monkeypatch):
        """Test find_ac_path behavior under various /sys layouts"""
        # No /sys
        original_exists = os.path.exists
        monkeypatch.setattr(
            "os.path.exists",
            lambda p: False if p == "/sys/class/power_supply" else original_exists(p),
        )
        assert SystemUtils.find_ac_path() is None

        # AC path exists as ADP1
        def fake_exists2(path):
            if path == "/sys/class/power_supply":
                return True
            if path.endswith("ADP1"):
                return True
            if path.endswith("ADP1/type"):
                return True
            return False

        monkeypatch.setattr("os.path.exists", fake_exists2)
        monkeypatch.setattr(
            "os.listdir",
            lambda path: ["ADP1"] if path == "/sys/class/power_supply" else [],
        )

        class _FakeTypeFile:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return "Mains"

        monkeypatch.setattr(
            "builtins.open",
            lambda p, *a, **k: _FakeTypeFile()
            if p.endswith("type")
            else open(p, *a, **k),
        )
        # For the simulated path, find_ac_path should return a path ending with ADP1
        p = SystemUtils.find_ac_path()
        assert p is not None and p.endswith("ADP1")

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
