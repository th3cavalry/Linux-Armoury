import json
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "linux-armoury"
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_settings(self):
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return self.get_defaults()

    def save_settings(self, settings):
        self.config_file.write_text(json.dumps(settings, indent=2))

    def get_defaults(self):
        return {
            "auto_profile_switching": False,
            "last_tdp_profile": "Balanced",
            "rgb_brightness": 50,
            "rgb_color": "#ff0066",
            "battery_charge_limit": 80,
            "fan_curve": "Balanced",
            "window_size": [1000, 650],
            "startup_section": "Dashboard",
        }
