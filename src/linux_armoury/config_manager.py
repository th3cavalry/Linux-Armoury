"""
Configuration Manager for Linux Armoury
Handles saving and loading user preferences
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("LinuxArmoury")


class ConfigManager:
    """Manages application configuration and user preferences"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "linux-armoury"
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self.load()

    def get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "version": "1.0.0",
            "auto_profile_switching": False,
            "last_tdp_profile": "Balanced",
            "rgb_brightness": 50,
            "rgb_color": "#ff0066",
            "rgb_effect": "Static",
            "battery_charge_limit": 80,
            "fan_curve": "Balanced",
            "gpu_mode": "Hybrid",
            "window_size": [1000, 650],
            "window_position": None,
            "startup_section": "Dashboard",
            "minimize_to_tray": True,
            "start_minimized": False,
            "show_notifications": True,
            "notification_duration": 5000,
            "monitoring_interval": 2000,
            "graph_history_seconds": 60,
            "theme": "dark",
        }

    def load(self) -> Dict[str, Any]:
        """Load settings from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")

                # Merge with defaults to add any new settings
                defaults = self.get_defaults()
                for key, value in defaults.items():
                    if key not in self._config:
                        self._config[key] = value

                return self._config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._config = self.get_defaults()
        else:
            logger.info("No config file found, using defaults")
            self._config = self.get_defaults()
            self.save()

        return self._config

    def save(self) -> bool:
        """Save current settings to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value and optionally save"""
        self._config[key] = value
        if save:
            self.save()

    def update(self, values: Dict[str, Any], save: bool = True) -> None:
        """Update multiple configuration values"""
        self._config.update(values)
        if save:
            self.save()

    def reset(self) -> None:
        """Reset to default configuration"""
        self._config = self.get_defaults()
        self.save()
        logger.info("Configuration reset to defaults")

    def export_config(self, filepath: Path) -> bool:
        """Export configuration to a file"""
        try:
            with open(filepath, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export config: {e}")
            return False

    def import_config(self, filepath: Path) -> bool:
        """Import configuration from a file"""
        try:
            with open(filepath, "r") as f:
                imported = json.load(f)

            # Validate imported config has reasonable values
            self._config.update(imported)
            self.save()
            logger.info(f"Configuration imported from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
