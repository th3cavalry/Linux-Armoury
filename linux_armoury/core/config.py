"""
Configuration management for Linux Armoury
"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for Linux Armoury"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "linux-armoury"
        self.config_file = self.config_dir / "config.json"
        self.logger = logging.getLogger(__name__)
        self._config = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self._config = self._get_default_config()
                self.save()  # Save default config
                self.logger.info("Created default configuration")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._config = self._get_default_config()
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "start_minimized": False,
            "auto_start": False,
            "check_updates": True,
            "update_interval": 3600,  # seconds
            "window_geometry": None,
            "theme": "auto",  # auto, light, dark
            "show_notifications": True,
            "tdp_profile": "balanced",
            "refresh_rate_profile": "balanced",
            "auto_switch_power": True,
            "logging_level": "INFO"
        }