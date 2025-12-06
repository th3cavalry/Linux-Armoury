#!/usr/bin/env python3
"""
Unit tests for config.py
"""

import pytest
from linux_armoury.config import Config


class TestConfig:
    """Test cases for Config class"""
    
    def test_app_id_exists(self):
        """Test that APP_ID is defined"""
        assert hasattr(Config, "APP_ID")
        assert Config.APP_ID == "com.github.th3cavalry.linux-armoury"
    
    def test_version_format(self):
        """Test version is in semver format"""
        assert hasattr(Config, "VERSION")
        parts = Config.VERSION.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()
    
    def test_power_profiles_exist(self):
        """Test that all expected power profiles are defined"""
        expected_profiles = [
            "emergency", "battery", "efficient", 
            "balanced", "performance", "gaming", "maximum"
        ]
        for profile in expected_profiles:
            assert profile in Config.POWER_PROFILES
    
    def test_power_profile_structure(self):
        """Test that power profiles have required fields"""
        required_fields = ["name", "tdp", "refresh", "description"]
        for profile_id, profile in Config.POWER_PROFILES.items():
            for field in required_fields:
                assert field in profile, f"Profile {profile_id} missing {field}"
    
    def test_tdp_ranges(self):
        """Test that TDP values are within valid ranges"""
        for profile_id, profile in Config.POWER_PROFILES.items():
            tdp = profile["tdp"]
            assert Config.MIN_TDP <= tdp <= Config.MAX_TDP, \
                f"Profile {profile_id} TDP {tdp} out of range"
    
    def test_refresh_rates_valid(self):
        """Test that refresh rates are valid"""
        for profile_id, profile in Config.POWER_PROFILES.items():
            refresh = profile["refresh"]
            assert refresh in Config.SUPPORTED_REFRESH_RATES, \
                f"Profile {profile_id} has invalid refresh rate {refresh}"
    
    def test_supported_models_exist(self):
        """Test that supported models are defined"""
        assert hasattr(Config, "SUPPORTED_MODELS")
        assert len(Config.SUPPORTED_MODELS) > 0
    
    def test_shortcuts_defined(self):
        """Test that keyboard shortcuts are defined"""
        assert hasattr(Config, "SHORTCUTS")
        assert "quit" in Config.SHORTCUTS
    
    def test_temperature_thresholds(self):
        """Test temperature thresholds are sane"""
        assert Config.TEMP_WARNING < Config.TEMP_CRITICAL
        assert Config.TEMP_WARNING > 0
        assert Config.TEMP_CRITICAL < 150


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
