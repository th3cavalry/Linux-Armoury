"""
RGB Lighting control module for Linux Armoury
Aura Sync integration inspired by ROG Control Center
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path

from linux_armoury.core.utils import run_command, check_command_exists


class AuraEffect(Enum):
    """Available Aura lighting effects"""
    STATIC = "static"
    BREATHING = "breathing"
    RAINBOW = "rainbow"
    PULSE = "pulse"
    COMET = "comet"
    STROBE = "strobe"
    DISCO = "disco"
    WAVE = "wave"


class AuraZone(Enum):
    """Available Aura lighting zones"""
    KEYBOARD = "keyboard"
    LOGO = "logo"
    LIGHTBAR = "lightbar"
    LID = "lid"
    UNDERGLOW = "underglow"


class RGBColor:
    """RGB color representation"""
    
    def __init__(self, r: int, g: int, b: int):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
    
    def to_hex(self) -> str:
        """Convert to hex string"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple"""
        return (self.r, self.g, self.b)
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'RGBColor':
        """Create from hex string"""
        hex_color = hex_color.lstrip('#')
        return cls(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> 'RGBColor':
        """Create from HSV values (0-1 range)"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return cls(int(r * 255), int(g * 255), int(b * 255))


class AuraManager:
    """ASUS Aura lighting manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asusctl_available = check_command_exists("asusctl")
        self.openrgb_available = check_command_exists("openrgb")
        self.available_zones = self._discover_zones()
        
    def is_available(self) -> bool:
        """Check if Aura control is available"""
        return self.asusctl_available or self.openrgb_available
    
    def _discover_zones(self) -> List[AuraZone]:
        """Discover available lighting zones"""
        zones = []
        
        if self.asusctl_available:
            success, output = run_command(["asusctl", "led-mode", "-l"])
            if success:
                # Parse available zones from asusctl output
                for line in output.split('\n'):
                    line = line.lower().strip()
                    if 'keyboard' in line:
                        zones.append(AuraZone.KEYBOARD)
                    if 'logo' in line:
                        zones.append(AuraZone.LOGO)
                    if 'lightbar' in line or 'light_bar' in line:
                        zones.append(AuraZone.LIGHTBAR)
                    if 'lid' in line:
                        zones.append(AuraZone.LID)
        
        # Remove duplicates
        return list(set(zones))
    
    def get_available_zones(self) -> List[AuraZone]:
        """Get list of available lighting zones"""
        return self.available_zones
    
    def get_available_effects(self, zone: AuraZone) -> List[AuraEffect]:
        """Get available effects for a zone"""
        if not self.is_available():
            return []
        
        effects = []
        
        if self.asusctl_available:
            success, output = run_command(["asusctl", "led-mode", "-l"])
            if success:
                # Parse available effects from output
                available_effects = [
                    AuraEffect.STATIC,
                    AuraEffect.BREATHING,
                    AuraEffect.RAINBOW,
                    AuraEffect.PULSE,
                    AuraEffect.COMET,
                    AuraEffect.STROBE
                ]
                effects.extend(available_effects)
        
        return list(set(effects))
    
    def set_zone_effect(self, zone: AuraZone, effect: AuraEffect, 
                       color: Optional[RGBColor] = None, 
                       speed: int = 2, brightness: int = 3) -> bool:
        """Set lighting effect for a zone"""
        if not self.is_available():
            return False
        
        try:
            if self.asusctl_available:
                return self._set_asusctl_effect(zone, effect, color, speed, brightness)
            elif self.openrgb_available:
                return self._set_openrgb_effect(zone, effect, color, speed, brightness)
        except Exception as e:
            self.logger.error(f"Failed to set zone effect: {e}")
        
        return False
    
    def _set_asusctl_effect(self, zone: AuraZone, effect: AuraEffect,
                           color: Optional[RGBColor], speed: int, brightness: int) -> bool:
        """Set effect using asusctl"""
        cmd = ["asusctl", "led-mode"]
        
        # Add zone parameter
        if zone == AuraZone.KEYBOARD:
            cmd.extend(["-k"])
        elif zone == AuraZone.LOGO:
            cmd.extend(["-l"])
        elif zone == AuraZone.LIGHTBAR:
            cmd.extend(["-b"])
        
        # Add effect
        cmd.extend(["-m", effect.value])
        
        # Add color if specified
        if color and effect in [AuraEffect.STATIC, AuraEffect.BREATHING, AuraEffect.PULSE]:
            cmd.extend(["-c", f"{color.r},{color.g},{color.b}"])
        
        # Add speed (1-5)
        speed = max(1, min(5, speed))
        cmd.extend(["-s", str(speed)])
        
        # Add brightness (0-3)
        brightness = max(0, min(3, brightness))
        cmd.extend(["-B", str(brightness)])
        
        success, output = run_command(cmd)
        if not success:
            self.logger.error(f"asusctl command failed: {output}")
        
        return success
    
    def _set_openrgb_effect(self, zone: AuraZone, effect: AuraEffect,
                           color: Optional[RGBColor], speed: int, brightness: int) -> bool:
        """Set effect using OpenRGB"""
        # OpenRGB commands are more complex, this is a simplified implementation
        if color:
            cmd = ["openrgb", "-c", color.to_hex()]
            success, _ = run_command(cmd)
            return success
        
        return False
    
    def get_current_settings(self, zone: AuraZone) -> Optional[Dict]:
        """Get current lighting settings for a zone"""
        if not self.asusctl_available:
            return None
        
        success, output = run_command(["asusctl", "led-mode", "-g"])
        if success:
            # Parse current settings from output
            settings = {
                'zone': zone,
                'effect': None,
                'color': None,
                'speed': None,
                'brightness': None
            }
            
            # Simple parsing - would need to be improved based on actual asusctl output format
            for line in output.split('\n'):
                line = line.strip()
                if 'mode:' in line.lower():
                    mode = line.split(':')[-1].strip().lower()
                    for effect in AuraEffect:
                        if effect.value in mode:
                            settings['effect'] = effect
                            break
                elif 'color:' in line.lower():
                    # Parse color information
                    pass
            
            return settings
        
        return None
    
    def create_custom_animation(self, zone: AuraZone, 
                              color_sequence: List[RGBColor],
                              duration: float = 1.0) -> bool:
        """Create a custom color animation"""
        if not self.is_available():
            return False
        
        try:
            # Simple animation by cycling through colors
            for color in color_sequence:
                self.set_zone_effect(zone, AuraEffect.STATIC, color)
                time.sleep(duration / len(color_sequence))
            
            return True
        except Exception as e:
            self.logger.error(f"Animation failed: {e}")
            return False
    
    def save_profile(self, profile_name: str, settings: Dict[AuraZone, Dict]) -> bool:
        """Save lighting profile"""
        # This would typically save to asusctl profiles or a config file
        # Implementation depends on the specific tool capabilities
        try:
            if self.asusctl_available:
                # Some ASUS laptops support profile saving
                success, _ = run_command(["asusctl", "led-mode", "--save", profile_name])
                return success
        except Exception as e:
            self.logger.error(f"Failed to save profile: {e}")
        
        return False
    
    def load_profile(self, profile_name: str) -> bool:
        """Load a saved lighting profile"""
        try:
            if self.asusctl_available:
                success, _ = run_command(["asusctl", "led-mode", "--load", profile_name])
                return success
        except Exception as e:
            self.logger.error(f"Failed to load profile: {e}")
        
        return False


class KeyboardLightingManager:
    """Advanced keyboard lighting control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.aura_manager = AuraManager()
        
    def is_available(self) -> bool:
        """Check if keyboard lighting is available"""
        return AuraZone.KEYBOARD in self.aura_manager.get_available_zones()
    
    def set_per_key_color(self, key_map: Dict[str, RGBColor]) -> bool:
        """Set individual key colors (if supported)"""
        # This would require more advanced RGB control
        # Most ASUS laptops don't support per-key RGB, but some do
        self.logger.info("Per-key RGB not implemented yet")
        return False
    
    def set_zone_colors(self, zones: Dict[str, RGBColor]) -> bool:
        """Set colors for different keyboard zones"""
        # Some keyboards have multiple zones (WASD, arrows, etc.)
        success = True
        for zone_name, color in zones.items():
            # This would map zone names to specific keyboard areas
            if not self.aura_manager.set_zone_effect(AuraZone.KEYBOARD, AuraEffect.STATIC, color):
                success = False
        
        return success
    
    def create_typing_effect(self, base_color: RGBColor, 
                           highlight_color: RGBColor, 
                           fade_time: float = 0.5) -> bool:
        """Create a typing highlight effect"""
        # This would highlight keys as they're typed
        # Implementation would require key press detection
        self.logger.info("Typing effects not implemented yet")
        return False
    
    def set_game_mode_lighting(self, game_keys: List[str], 
                             highlight_color: RGBColor) -> bool:
        """Highlight gaming keys (WASD, etc.)"""
        # Highlight important gaming keys
        self.logger.info("Game mode lighting not implemented yet")
        return False


class MatrixDisplayManager:
    """Control for ASUS ROG matrix LED displays (like on some Zephyrus models)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available = self._check_matrix_display()
        
    def _check_matrix_display(self) -> bool:
        """Check if device has a matrix LED display"""
        # Check for matrix display support in asusctl
        if check_command_exists("asusctl"):
            success, output = run_command(["asusctl", "led-matrix", "--help"])
            return success
        return False
    
    def is_available(self) -> bool:
        """Check if matrix display is available"""
        return self.available
    
    def show_image(self, image_path: str) -> bool:
        """Display an image on the matrix display"""
        if not self.available:
            return False
        
        try:
            success, _ = run_command(["asusctl", "led-matrix", "-i", image_path])
            return success
        except Exception as e:
            self.logger.error(f"Failed to show image: {e}")
            return False
    
    def show_animation(self, gif_path: str) -> bool:
        """Display an animated GIF on the matrix display"""
        if not self.available:
            return False
        
        try:
            success, _ = run_command(["asusctl", "led-matrix", "-g", gif_path])
            return success
        except Exception as e:
            self.logger.error(f"Failed to show animation: {e}")
            return False
    
    def set_brightness(self, brightness: int) -> bool:
        """Set matrix display brightness (0-255)"""
        if not self.available:
            return False
        
        brightness = max(0, min(255, brightness))
        try:
            success, _ = run_command(["asusctl", "led-matrix", "-b", str(brightness)])
            return success
        except Exception as e:
            self.logger.error(f"Failed to set brightness: {e}")
            return False
    
    def show_text(self, text: str, color: RGBColor) -> bool:
        """Display text on the matrix display"""
        if not self.available:
            return False
        
        try:
            color_str = f"{color.r},{color.g},{color.b}"
            success, _ = run_command(["asusctl", "led-matrix", "-t", text, "-c", color_str])
            return success
        except Exception as e:
            self.logger.error(f"Failed to show text: {e}")
            return False


# Predefined color schemes
class ColorSchemes:
    """Predefined color schemes for easy access"""
    
    # Gaming themes
    GAMING_RED = RGBColor(255, 0, 0)
    GAMING_BLUE = RGBColor(0, 100, 255)
    GAMING_GREEN = RGBColor(0, 255, 0)
    GAMING_PURPLE = RGBColor(128, 0, 255)
    
    # ROG themes
    ROG_ORANGE = RGBColor(255, 128, 0)
    ROG_RED = RGBColor(255, 0, 64)
    
    # Work themes
    WORK_WHITE = RGBColor(255, 255, 255)
    WORK_WARM = RGBColor(255, 220, 180)
    WORK_COOL = RGBColor(180, 220, 255)
    
    # Rainbow
    RAINBOW_COLORS = [
        RGBColor(255, 0, 0),    # Red
        RGBColor(255, 127, 0),  # Orange
        RGBColor(255, 255, 0),  # Yellow
        RGBColor(0, 255, 0),    # Green
        RGBColor(0, 0, 255),    # Blue
        RGBColor(75, 0, 130),   # Indigo
        RGBColor(148, 0, 211),  # Violet
    ]
    
    @classmethod
    def get_temperature_color(cls, temp: float, min_temp: float = 30, max_temp: float = 80) -> RGBColor:
        """Get color based on temperature (blue=cool, red=hot)"""
        if temp <= min_temp:
            return RGBColor(0, 100, 255)  # Cool blue
        elif temp >= max_temp:
            return RGBColor(255, 0, 0)    # Hot red
        else:
            # Interpolate between blue and red
            ratio = (temp - min_temp) / (max_temp - min_temp)
            r = int(255 * ratio)
            g = int(100 * (1 - ratio))
            b = int(255 * (1 - ratio))
            return RGBColor(r, g, b)
    
    @classmethod
    def get_performance_color(cls, usage: float) -> RGBColor:
        """Get color based on performance usage (green=low, red=high)"""
        if usage <= 30:
            return RGBColor(0, 255, 0)    # Green
        elif usage <= 70:
            return RGBColor(255, 255, 0)  # Yellow
        else:
            return RGBColor(255, 0, 0)    # Red