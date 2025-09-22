"""
Audio enhancement module for Linux Armoury
Inspired by Armoury Crate's Sonic Studio and audio optimization features
"""

import logging
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from linux_armoury.core.utils import run_command, check_command_exists


class AudioProfile(Enum):
    """Audio enhancement profiles"""
    MUSIC = "music"
    GAMING = "gaming"
    MOVIE = "movie"
    VOICE = "voice"
    STREAMING = "streaming"
    CUSTOM = "custom"


class MicrophoneMode(Enum):
    """Microphone processing modes"""
    CLEAR = "clear"
    NOISE_REDUCTION = "noise_reduction"
    VOICE_ENHANCE = "voice_enhance"
    STREAMING = "streaming"
    GAMING_COMMS = "gaming_comms"


@dataclass
class EqualizerBand:
    """Equalizer band configuration"""
    frequency: int  # Hz
    gain: float     # dB (-12 to +12)
    q_factor: float = 1.0


@dataclass
class AudioSettings:
    """Audio profile settings"""
    name: str
    profile: AudioProfile
    equalizer_bands: List[EqualizerBand]
    bass_boost: float = 0.0      # dB
    treble_boost: float = 0.0    # dB
    surround_enabled: bool = False
    noise_reduction: bool = False
    voice_clarity: bool = False
    dynamic_range: float = 1.0   # Compression ratio
    spatial_audio: bool = False


class PulseAudioManager:
    """PulseAudio management for audio enhancement"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pactl_available = check_command_exists("pactl")
        self.pulseeffects_available = check_command_exists("pulseeffects")
        self.easyeffects_available = check_command_exists("easyeffects")
        
    def is_available(self) -> bool:
        """Check if PulseAudio control is available"""
        return self.pactl_available
    
    def get_audio_devices(self) -> Dict[str, List[Dict]]:
        """Get available audio input and output devices"""
        devices = {'sinks': [], 'sources': []}
        
        if not self.pactl_available:
            return devices
        
        try:
            # Get output devices (sinks)
            success, output = run_command(["pactl", "list", "short", "sinks"])
            if success:
                for line in output.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices['sinks'].append({
                                'index': parts[0],
                                'name': parts[1],
                                'description': parts[1]
                            })
            
            # Get input devices (sources)
            success, output = run_command(["pactl", "list", "short", "sources"])
            if success:
                for line in output.strip().split('\n'):
                    if line and not line.endswith('.monitor'):  # Skip monitor sources
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices['sources'].append({
                                'index': parts[0],
                                'name': parts[1],
                                'description': parts[1]
                            })
            
        except Exception as e:
            self.logger.error(f"Failed to get audio devices: {e}")
        
        return devices
    
    def set_default_device(self, device_name: str, device_type: str = 'sink') -> bool:
        """Set default audio device"""
        if not self.pactl_available:
            return False
        
        try:
            if device_type == 'sink':
                success, _ = run_command(["pactl", "set-default-sink", device_name])
            else:
                success, _ = run_command(["pactl", "set-default-source", device_name])
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to set default device: {e}")
            return False
    
    def set_volume(self, device_name: str, volume: int, device_type: str = 'sink') -> bool:
        """Set device volume (0-100)"""
        if not self.pactl_available:
            return False
        
        try:
            volume = max(0, min(100, volume))
            if device_type == 'sink':
                success, _ = run_command(["pactl", "set-sink-volume", device_name, f"{volume}%"])
            else:
                success, _ = run_command(["pactl", "set-source-volume", device_name, f"{volume}%"])
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to set volume: {e}")
            return False
    
    def toggle_mute(self, device_name: str, device_type: str = 'sink') -> bool:
        """Toggle device mute"""
        if not self.pactl_available:
            return False
        
        try:
            if device_type == 'sink':
                success, _ = run_command(["pactl", "set-sink-mute", device_name, "toggle"])
            else:
                success, _ = run_command(["pactl", "set-source-mute", device_name, "toggle"])
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to toggle mute: {e}")
            return False
    
    def load_module(self, module_name: str, args: str = "") -> bool:
        """Load a PulseAudio module"""
        if not self.pactl_available:
            return False
        
        try:
            cmd = ["pactl", "load-module", module_name]
            if args:
                cmd.append(args)
            
            success, _ = run_command(cmd)
            return success
        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {e}")
            return False
    
    def unload_module(self, module_id: str) -> bool:
        """Unload a PulseAudio module"""
        if not self.pactl_available:
            return False
        
        try:
            success, _ = run_command(["pactl", "unload-module", module_id])
            return success
        except Exception as e:
            self.logger.error(f"Failed to unload module {module_id}: {e}")
            return False


class EqualizerManager:
    """Audio equalizer management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pulse_manager = PulseAudioManager()
        self.eq_module_id = None
        
    def is_available(self) -> bool:
        """Check if equalizer is available"""
        return self.pulse_manager.is_available()
    
    def load_equalizer(self) -> bool:
        """Load the PulseAudio equalizer module"""
        if not self.is_available():
            return False
        
        try:
            # Try to load the equalizer module
            success, output = run_command([
                "pactl", "load-module", "module-equalizer-sink"
            ])
            
            if success:
                # Parse module ID from output
                try:
                    self.eq_module_id = output.strip()
                    self.logger.info(f"Loaded equalizer module: {self.eq_module_id}")
                    return True
                except Exception:
                    pass
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to load equalizer: {e}")
            return False
    
    def unload_equalizer(self) -> bool:
        """Unload the equalizer module"""
        if self.eq_module_id:
            return self.pulse_manager.unload_module(self.eq_module_id)
        return True
    
    def apply_equalizer_preset(self, bands: List[EqualizerBand]) -> bool:
        """Apply equalizer settings"""
        # This would require a more sophisticated equalizer implementation
        # For now, we'll log the attempt
        self.logger.info(f"Applying equalizer preset with {len(bands)} bands")
        
        # In a real implementation, this would:
        # 1. Configure the equalizer module with the band settings
        # 2. Apply the gains to each frequency band
        # 3. Handle Q factors and filter types
        
        return True
    
    def get_preset_bands(self, preset: str) -> List[EqualizerBand]:
        """Get predefined equalizer presets"""
        presets = {
            'flat': [
                EqualizerBand(60, 0.0),
                EqualizerBand(170, 0.0),
                EqualizerBand(310, 0.0),
                EqualizerBand(600, 0.0),
                EqualizerBand(1000, 0.0),
                EqualizerBand(3000, 0.0),
                EqualizerBand(6000, 0.0),
                EqualizerBand(12000, 0.0),
                EqualizerBand(14000, 0.0),
                EqualizerBand(16000, 0.0)
            ],
            'gaming': [
                EqualizerBand(60, 2.0),      # Enhanced bass for explosions
                EqualizerBand(170, 1.0),
                EqualizerBand(310, 0.0),
                EqualizerBand(600, -1.0),
                EqualizerBand(1000, 0.0),
                EqualizerBand(3000, 2.0),    # Enhanced mids for voices
                EqualizerBand(6000, 3.0),    # Enhanced highs for footsteps
                EqualizerBand(12000, 2.0),
                EqualizerBand(14000, 1.0),
                EqualizerBand(16000, 0.0)
            ],
            'music': [
                EqualizerBand(60, 3.0),
                EqualizerBand(170, 2.0),
                EqualizerBand(310, 1.0),
                EqualizerBand(600, 0.0),
                EqualizerBand(1000, 0.0),
                EqualizerBand(3000, 1.0),
                EqualizerBand(6000, 2.0),
                EqualizerBand(12000, 3.0),
                EqualizerBand(14000, 2.0),
                EqualizerBand(16000, 1.0)
            ],
            'voice': [
                EqualizerBand(60, -2.0),
                EqualizerBand(170, -1.0),
                EqualizerBand(310, 0.0),
                EqualizerBand(600, 2.0),
                EqualizerBand(1000, 4.0),
                EqualizerBand(3000, 3.0),
                EqualizerBand(6000, 1.0),
                EqualizerBand(12000, -1.0),
                EqualizerBand(14000, -2.0),
                EqualizerBand(16000, -3.0)
            ]
        }
        
        return presets.get(preset, presets['flat'])


class MicrophoneEnhancer:
    """Microphone enhancement and noise reduction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pulse_manager = PulseAudioManager()
        self.noise_module_id = None
        self.echo_module_id = None
        
    def is_available(self) -> bool:
        """Check if microphone enhancement is available"""
        return self.pulse_manager.is_available()
    
    def enable_noise_reduction(self) -> bool:
        """Enable noise reduction for microphone"""
        if not self.is_available():
            return False
        
        try:
            # Load noise suppression module
            success, output = run_command([
                "pactl", "load-module", "module-echo-cancel",
                "aec_method=webrtc", "aec_args=noise_suppression=1"
            ])
            
            if success:
                self.noise_module_id = output.strip()
                self.logger.info("Enabled microphone noise reduction")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to enable noise reduction: {e}")
            return False
    
    def disable_noise_reduction(self) -> bool:
        """Disable noise reduction for microphone"""
        if self.noise_module_id:
            success = self.pulse_manager.unload_module(self.noise_module_id)
            if success:
                self.noise_module_id = None
                self.logger.info("Disabled microphone noise reduction")
            return success
        return True
    
    def enable_echo_cancellation(self) -> bool:
        """Enable echo cancellation"""
        if not self.is_available():
            return False
        
        try:
            success, output = run_command([
                "pactl", "load-module", "module-echo-cancel",
                "aec_method=webrtc", "aec_args=echo_suppression=1"
            ])
            
            if success:
                self.echo_module_id = output.strip()
                self.logger.info("Enabled echo cancellation")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to enable echo cancellation: {e}")
            return False
    
    def disable_echo_cancellation(self) -> bool:
        """Disable echo cancellation"""
        if self.echo_module_id:
            success = self.pulse_manager.unload_module(self.echo_module_id)
            if success:
                self.echo_module_id = None
                self.logger.info("Disabled echo cancellation")
            return success
        return True
    
    def set_microphone_gain(self, gain_db: float) -> bool:
        """Set microphone gain boost"""
        if not self.is_available():
            return False
        
        try:
            # Get default source
            success, output = run_command(["pactl", "get-default-source"])
            if success:
                source_name = output.strip()
                
                # Calculate volume percentage from dB gain
                # This is a simplified conversion
                volume_percent = max(0, min(200, 100 + (gain_db * 10)))
                
                return self.pulse_manager.set_volume(source_name, int(volume_percent), 'source')
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to set microphone gain: {e}")
            return False


class SpatialAudioManager:
    """Spatial audio and surround sound management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pulse_manager = PulseAudioManager()
        self.spatial_module_id = None
        
    def is_available(self) -> bool:
        """Check if spatial audio is available"""
        return self.pulse_manager.is_available()
    
    def enable_virtual_surround(self, channels: int = 8) -> bool:
        """Enable virtual surround sound"""
        if not self.is_available():
            return False
        
        try:
            # Load virtual surround module
            success, output = run_command([
                "pactl", "load-module", "module-virtual-surround-sink",
                f"channels={channels}"
            ])
            
            if success:
                self.spatial_module_id = output.strip()
                self.logger.info(f"Enabled virtual {channels}-channel surround")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to enable virtual surround: {e}")
            return False
    
    def disable_virtual_surround(self) -> bool:
        """Disable virtual surround sound"""
        if self.spatial_module_id:
            success = self.pulse_manager.unload_module(self.spatial_module_id)
            if success:
                self.spatial_module_id = None
                self.logger.info("Disabled virtual surround")
            return success
        return True
    
    def set_channel_mapping(self, mapping: Dict[str, float]) -> bool:
        """Set channel mapping for spatial audio"""
        # This would configure how audio channels are mapped in space
        self.logger.info(f"Channel mapping not fully implemented: {mapping}")
        return True


class AudioProfileManager:
    """Main audio profile management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pulse_manager = PulseAudioManager()
        self.equalizer = EqualizerManager()
        self.microphone = MicrophoneEnhancer()
        self.spatial = SpatialAudioManager()
        self.current_profile = None
        self.profiles = self._get_default_profiles()
        
    def _get_default_profiles(self) -> Dict[str, AudioSettings]:
        """Get default audio profiles"""
        return {
            'gaming': AudioSettings(
                name="Gaming",
                profile=AudioProfile.GAMING,
                equalizer_bands=self.equalizer.get_preset_bands('gaming'),
                bass_boost=2.0,
                surround_enabled=True,
                noise_reduction=True,
                voice_clarity=True
            ),
            'music': AudioSettings(
                name="Music",
                profile=AudioProfile.MUSIC,
                equalizer_bands=self.equalizer.get_preset_bands('music'),
                bass_boost=3.0,
                treble_boost=2.0,
                spatial_audio=True
            ),
            'voice': AudioSettings(
                name="Voice/Communication",
                profile=AudioProfile.VOICE,
                equalizer_bands=self.equalizer.get_preset_bands('voice'),
                noise_reduction=True,
                voice_clarity=True
            ),
            'streaming': AudioSettings(
                name="Streaming",
                profile=AudioProfile.STREAMING,
                equalizer_bands=self.equalizer.get_preset_bands('flat'),
                noise_reduction=True,
                voice_clarity=True,
                dynamic_range=0.7  # Light compression
            )
        }
    
    def apply_profile(self, profile_name: str) -> bool:
        """Apply an audio profile"""
        if profile_name not in self.profiles:
            self.logger.error(f"Unknown audio profile: {profile_name}")
            return False
        
        settings = self.profiles[profile_name]
        
        try:
            self.logger.info(f"Applying audio profile: {settings.name}")
            
            # Apply equalizer settings
            if self.equalizer.is_available():
                self.equalizer.load_equalizer()
                self.equalizer.apply_equalizer_preset(settings.equalizer_bands)
            
            # Apply microphone enhancements
            if settings.noise_reduction:
                self.microphone.enable_noise_reduction()
            else:
                self.microphone.disable_noise_reduction()
            
            if settings.voice_clarity:
                self.microphone.enable_echo_cancellation()
            else:
                self.microphone.disable_echo_cancellation()
            
            # Apply spatial audio
            if settings.surround_enabled:
                self.spatial.enable_virtual_surround()
            else:
                self.spatial.disable_virtual_surround()
            
            self.current_profile = profile_name
            self.logger.info(f"Applied audio profile: {settings.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply audio profile: {e}")
            return False
    
    def get_current_profile(self) -> Optional[str]:
        """Get current audio profile"""
        return self.current_profile
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profiles"""
        return list(self.profiles.keys())
    
    def create_custom_profile(self, name: str, settings: AudioSettings) -> bool:
        """Create a custom audio profile"""
        try:
            self.profiles[name.lower()] = settings
            self.logger.info(f"Created custom audio profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create custom profile: {e}")
            return False
    
    def get_audio_devices(self) -> Dict:
        """Get available audio devices"""
        return self.pulse_manager.get_audio_devices()
    
    def set_default_audio_device(self, device_name: str, device_type: str = 'sink') -> bool:
        """Set default audio device"""
        return self.pulse_manager.set_default_device(device_name, device_type)
    
    def adjust_volume(self, device_name: str, volume: int, device_type: str = 'sink') -> bool:
        """Adjust device volume"""
        return self.pulse_manager.set_volume(device_name, volume, device_type)
    
    def toggle_device_mute(self, device_name: str, device_type: str = 'sink') -> bool:
        """Toggle device mute"""
        return self.pulse_manager.toggle_mute(device_name, device_type)
    
    def get_audio_status(self) -> Dict:
        """Get current audio system status"""
        return {
            'current_profile': self.current_profile,
            'available_profiles': self.get_available_profiles(),
            'devices': self.get_audio_devices(),
            'features': {
                'equalizer': self.equalizer.is_available(),
                'microphone_enhancement': self.microphone.is_available(),
                'spatial_audio': self.spatial.is_available(),
                'pulse_audio': self.pulse_manager.is_available()
            }
        }