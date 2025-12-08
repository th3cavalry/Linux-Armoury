"""
Profile Manager for Linux Armoury
Handles system profiles and presets
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("LinuxArmoury")


@dataclass
class SystemProfile:
    """
    Represents a complete system configuration profile
    """

    name: str
    tdp_watts: int
    gpu_mode: str
    fan_curve: str
    rgb_brightness: int
    rgb_effect: str
    battery_limit: int
    refresh_rate: Optional[int] = None
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SystemProfile":
        """Create from dictionary"""
        return cls(**data)


class ProfileManager:
    """
    Manages system profiles and presets
    """

    # Built-in profiles
    BUILTIN_PROFILES = {
        "Gaming": SystemProfile(
            name="Gaming",
            tdp_watts=70,
            gpu_mode="Ultimate",
            fan_curve="Performance",
            rgb_brightness=100,
            rgb_effect="Rainbow",
            battery_limit=100,
            refresh_rate=165,
            description="Maximum performance for gaming sessions",
        ),
        "Balanced": SystemProfile(
            name="Balanced",
            tdp_watts=40,
            gpu_mode="Hybrid",
            fan_curve="Balanced",
            rgb_brightness=50,
            rgb_effect="Static",
            battery_limit=80,
            refresh_rate=None,
            description="Balanced performance and efficiency",
        ),
        "Work": SystemProfile(
            name="Work",
            tdp_watts=35,
            gpu_mode="Hybrid",
            fan_curve="Quiet",
            rgb_brightness=30,
            rgb_effect="Static",
            battery_limit=80,
            refresh_rate=60,
            description="Optimized for productivity",
        ),
        "Battery Saver": SystemProfile(
            name="Battery Saver",
            tdp_watts=18,
            gpu_mode="Eco",
            fan_curve="Silent",
            rgb_brightness=0,
            rgb_effect="Off",
            battery_limit=80,
            refresh_rate=60,
            description="Maximum battery life",
        ),
        "Silent": SystemProfile(
            name="Silent",
            tdp_watts=30,
            gpu_mode="Hybrid",
            fan_curve="Silent",
            rgb_brightness=20,
            rgb_effect="Breathe",
            battery_limit=80,
            refresh_rate=60,
            description="Quiet operation for noise-sensitive environments",
        ),
        "Turbo": SystemProfile(
            name="Turbo",
            tdp_watts=90,
            gpu_mode="Ultimate",
            fan_curve="Performance",
            rgb_brightness=100,
            rgb_effect="Rainbow",
            battery_limit=100,
            refresh_rate=165,
            description="Maximum performance, no limits",
        ),
    }

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "linux-armoury" / "profiles"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.custom_profiles: Dict[str, SystemProfile] = {}
        self._load_custom_profiles()

    def _load_custom_profiles(self):
        """Load custom profiles from disk"""
        try:
            for file_path in self.config_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    profile = SystemProfile.from_dict(data)
                    self.custom_profiles[profile.name] = profile
                    logger.debug(f"Loaded custom profile: {profile.name}")
                except Exception as e:
                    logger.error(f"Failed to load profile {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load custom profiles: {e}")

    def get_profile(self, name: str) -> Optional[SystemProfile]:
        """Get a profile by name (checks both builtin and custom)"""
        if name in self.BUILTIN_PROFILES:
            return self.BUILTIN_PROFILES[name]
        return self.custom_profiles.get(name)

    def list_profiles(self) -> Dict[str, List[str]]:
        """List all available profiles"""
        return {
            "builtin": list(self.BUILTIN_PROFILES.keys()),
            "custom": list(self.custom_profiles.keys()),
        }

    def save_custom_profile(self, profile: SystemProfile) -> bool:
        """Save a custom profile to disk"""
        try:
            file_path = self.config_dir / f"{profile.name}.json"
            with open(file_path, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)

            self.custom_profiles[profile.name] = profile
            logger.info(f"Saved custom profile: {profile.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profile {profile.name}: {e}")
            return False

    def delete_custom_profile(self, name: str) -> bool:
        """Delete a custom profile"""
        if name in self.BUILTIN_PROFILES:
            logger.warning(f"Cannot delete builtin profile: {name}")
            return False

        try:
            file_path = self.config_dir / f"{name}.json"
            if file_path.exists():
                file_path.unlink()

            if name in self.custom_profiles:
                del self.custom_profiles[name]

            logger.info(f"Deleted custom profile: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete profile {name}: {e}")
            return False

    def apply_profile(self, profile: SystemProfile, app) -> bool:
        """
        Apply all settings from a profile to the application

        Args:
            profile: Profile to apply
            app: Application instance

        Returns:
            Success status
        """
        try:
            logger.info(f"Applying profile: {profile.name}")
            success = True

            # TDP
            if hasattr(app, "set_tdp"):
                try:
                    app.set_tdp(profile.tdp_watts)
                except Exception as e:
                    logger.error(f"Failed to set TDP: {e}")
                    success = False

            # GPU mode
            if hasattr(app, "gpu_controller") and app.gpu_controller:
                try:
                    app.gpu_controller.set_mode(profile.gpu_mode)
                except Exception as e:
                    logger.error(f"Failed to set GPU mode: {e}")
                    success = False

            # Fan curve
            if hasattr(app, "fan_controller") and app.fan_controller:
                try:
                    app.fan_controller.set_curve(profile.fan_curve)
                except Exception as e:
                    logger.error(f"Failed to set fan curve: {e}")
                    success = False

            # RGB
            if hasattr(app, "keyboard_controller") and app.keyboard_controller:
                try:
                    app.keyboard_controller.set_brightness(profile.rgb_brightness)
                    if profile.rgb_effect != "Off":
                        app.keyboard_controller.set_effect(profile.rgb_effect)
                except Exception as e:
                    logger.error(f"Failed to set RGB: {e}")
                    success = False

            # Battery
            if hasattr(app, "battery_controller") and app.battery_controller:
                try:
                    app.battery_controller.set_charge_limit(profile.battery_limit)
                except Exception as e:
                    logger.error(f"Failed to set battery limit: {e}")
                    success = False

            # Show notification
            if hasattr(app, "show_toast"):
                status = "applied successfully" if success else "applied with errors"
                app.show_toast(
                    f"Profile '{profile.name}' {status}",
                    "success" if success else "warning",
                )

            # Save current profile to config
            if hasattr(app, "config"):
                app.config.set("last_tdp_profile", profile.name)

            logger.info(f"Profile {profile.name} applied - success: {success}")
            return success

        except Exception as e:
            logger.error(f"Failed to apply profile {profile.name}: {e}")
            if hasattr(app, "show_toast"):
                app.show_toast(f"Failed to apply profile: {e}", "error")
            return False

    def export_profile(self, profile: SystemProfile, filepath: Path) -> bool:
        """Export a profile to a file"""
        try:
            with open(filepath, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)
            logger.info(f"Profile exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export profile: {e}")
            return False

    def import_profile(self, filepath: Path) -> Optional[SystemProfile]:
        """Import a profile from a file"""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            profile = SystemProfile.from_dict(data)

            # Save as custom profile
            self.save_custom_profile(profile)

            logger.info(f"Profile imported from {filepath}")
            return profile
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return None
