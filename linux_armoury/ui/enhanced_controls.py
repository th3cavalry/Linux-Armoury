"""
Enhanced controls widget for Linux Armoury
Showcases advanced features inspired by ROG Control Center, G-Helper, and Armoury Crate
"""

import logging
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
        QPushButton, QSlider, QComboBox, QCheckBox, QTabWidget,
        QSpinBox, QProgressBar, QTextEdit, QGridLayout, QFrame
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont, QPalette
    
    # Try importing our enhanced modules
    try:
        from linux_armoury.core.hardware_monitor import (
            TemperatureMonitor, FanController, PerformanceMonitor, BatteryHealthManager
        )
        HARDWARE_MONITOR_AVAILABLE = True
    except ImportError:
        HARDWARE_MONITOR_AVAILABLE = False
    
    try:
        from linux_armoury.core.rgb_control import (
            AuraManager, RGBColor, ColorSchemes, AuraZone, AuraEffect
        )
        RGB_CONTROL_AVAILABLE = True
    except ImportError:
        RGB_CONTROL_AVAILABLE = False
    
    try:
        from linux_armoury.core.audio_manager import AudioProfileManager
        AUDIO_MANAGER_AVAILABLE = True
    except ImportError:
        AUDIO_MANAGER_AVAILABLE = False
    
    try:
        from linux_armoury.core.rog_integration import DisplayManager, PowerManagementManager
        ENHANCED_ROG_AVAILABLE = True
    except ImportError:
        ENHANCED_ROG_AVAILABLE = False
    
    from linux_armoury.core.config import Config
    
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


class EnhancedControlsWidget(QWidget):
    """Widget showcasing enhanced features from other ROG applications"""
    
    profile_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.init_managers()
        
        # Setup UI
        self.init_ui()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def init_managers(self):
        """Initialize enhanced managers"""
        if HARDWARE_MONITOR_AVAILABLE:
            self.temp_monitor = TemperatureMonitor()
            self.fan_controller = FanController()
            self.perf_monitor = PerformanceMonitor()
            self.battery_manager = BatteryHealthManager()
        else:
            self.temp_monitor = None
            self.fan_controller = None
            self.perf_monitor = None
            self.battery_manager = None
        
        if RGB_CONTROL_AVAILABLE:
            self.aura_manager = AuraManager()
        else:
            self.aura_manager = None
        
        if AUDIO_MANAGER_AVAILABLE:
            self.audio_manager = AudioProfileManager()
        else:
            self.audio_manager = None
        
        if ENHANCED_ROG_AVAILABLE:
            self.display_manager = DisplayManager()
            self.power_manager = PowerManagementManager()
        else:
            self.display_manager = None
            self.power_manager = None
    
    def init_ui(self):
        """Initialize the enhanced UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different feature categories
        self.tab_widget = QTabWidget()
        
        # Hardware Monitoring Tab
        self.create_hardware_tab()
        
        # RGB Lighting Tab
        self.create_rgb_tab()
        
        # Audio Enhancement Tab
        self.create_audio_tab()
        
        # Performance Tab
        self.create_performance_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_hardware_tab(self):
        """Create hardware monitoring tab"""
        hardware_widget = QWidget()
        layout = QVBoxLayout(hardware_widget)
        
        # Temperature Monitoring
        temp_group = QGroupBox("🌡️ Temperature Monitoring")
        temp_layout = QGridLayout(temp_group)
        
        self.cpu_temp_label = QLabel("CPU: --°C")
        self.gpu_temp_label = QLabel("GPU: --°C") 
        self.cpu_temp_bar = QProgressBar()
        self.cpu_temp_bar.setRange(0, 100)
        self.gpu_temp_bar = QProgressBar()
        self.gpu_temp_bar.setRange(0, 100)
        
        temp_layout.addWidget(QLabel("CPU Temperature:"), 0, 0)
        temp_layout.addWidget(self.cpu_temp_label, 0, 1)
        temp_layout.addWidget(self.cpu_temp_bar, 0, 2)
        temp_layout.addWidget(QLabel("GPU Temperature:"), 1, 0)
        temp_layout.addWidget(self.gpu_temp_label, 1, 1)
        temp_layout.addWidget(self.gpu_temp_bar, 1, 2)
        
        layout.addWidget(temp_group)
        
        # Fan Control
        fan_group = QGroupBox("🌪️ Fan Control")
        fan_layout = QVBoxLayout(fan_group)
        
        self.fan_mode_combo = QComboBox()
        self.fan_mode_combo.addItems(["Auto", "Silent", "Performance", "Manual"])
        self.fan_mode_combo.currentTextChanged.connect(self.on_fan_mode_changed)
        
        self.manual_fan_slider = QSlider(Qt.Horizontal)
        self.manual_fan_slider.setRange(0, 100)
        self.manual_fan_slider.setValue(50)
        self.manual_fan_slider.setEnabled(False)
        self.manual_fan_slider.valueChanged.connect(self.on_manual_fan_changed)
        
        self.fan_speed_label = QLabel("Fan Speed: 0 RPM")
        
        fan_layout.addWidget(QLabel("Fan Mode:"))
        fan_layout.addWidget(self.fan_mode_combo)
        fan_layout.addWidget(QLabel("Manual Speed:"))
        fan_layout.addWidget(self.manual_fan_slider)
        fan_layout.addWidget(self.fan_speed_label)
        
        layout.addWidget(fan_group)
        
        # Battery Health
        battery_group = QGroupBox("🔋 Battery Health")
        battery_layout = QGridLayout(battery_group)
        
        self.charge_limit_spinbox = QSpinBox()
        self.charge_limit_spinbox.setRange(20, 100)
        self.charge_limit_spinbox.setValue(80)
        self.charge_limit_spinbox.setSuffix("%")
        self.charge_limit_spinbox.valueChanged.connect(self.on_charge_limit_changed)
        
        self.battery_health_label = QLabel("Health: --%")
        self.cycle_count_label = QLabel("Cycles: --")
        
        battery_layout.addWidget(QLabel("Charge Limit:"), 0, 0)
        battery_layout.addWidget(self.charge_limit_spinbox, 0, 1)
        battery_layout.addWidget(self.battery_health_label, 1, 0)
        battery_layout.addWidget(self.cycle_count_label, 1, 1)
        
        layout.addWidget(battery_group)
        
        self.tab_widget.addTab(hardware_widget, "🔧 Hardware")
    
    def create_rgb_tab(self):
        """Create RGB lighting control tab"""
        rgb_widget = QWidget()
        layout = QVBoxLayout(rgb_widget)
        
        # Aura Lighting Control
        aura_group = QGroupBox("🌈 Aura Lighting")
        aura_layout = QGridLayout(aura_group)
        
        self.lighting_zone_combo = QComboBox()
        self.lighting_zone_combo.addItems(["Keyboard", "Logo", "Lightbar", "All Zones"])
        
        self.lighting_effect_combo = QComboBox()
        self.lighting_effect_combo.addItems(["Static", "Breathing", "Rainbow", "Pulse", "Comet", "Wave"])
        self.lighting_effect_combo.currentTextChanged.connect(self.on_lighting_effect_changed)
        
        self.lighting_speed_slider = QSlider(Qt.Horizontal)
        self.lighting_speed_slider.setRange(1, 5)
        self.lighting_speed_slider.setValue(3)
        
        self.lighting_brightness_slider = QSlider(Qt.Horizontal)
        self.lighting_brightness_slider.setRange(0, 3)
        self.lighting_brightness_slider.setValue(2)
        
        # Color selection buttons
        color_layout = QHBoxLayout()
        colors = [
            ("Red", ColorSchemes.GAMING_RED),
            ("Blue", ColorSchemes.GAMING_BLUE),
            ("Green", ColorSchemes.GAMING_GREEN),
            ("Purple", ColorSchemes.GAMING_PURPLE),
            ("ROG Orange", ColorSchemes.ROG_ORANGE)
        ]
        
        for name, color in colors:
            btn = QPushButton(name)
            btn.setStyleSheet(f"background-color: {color.to_hex()}; color: white;")
            btn.clicked.connect(lambda checked, c=color: self.on_color_selected(c))
            color_layout.addWidget(btn)
        
        aura_layout.addWidget(QLabel("Zone:"), 0, 0)
        aura_layout.addWidget(self.lighting_zone_combo, 0, 1)
        aura_layout.addWidget(QLabel("Effect:"), 1, 0)
        aura_layout.addWidget(self.lighting_effect_combo, 1, 1)
        aura_layout.addWidget(QLabel("Speed:"), 2, 0)
        aura_layout.addWidget(self.lighting_speed_slider, 2, 1)
        aura_layout.addWidget(QLabel("Brightness:"), 3, 0)
        aura_layout.addWidget(self.lighting_brightness_slider, 3, 1)
        aura_layout.addLayout(color_layout, 4, 0, 1, 2)
        
        layout.addWidget(aura_group)
        
        # Gaming Profiles
        gaming_group = QGroupBox("🎮 Gaming RGB Profiles")
        gaming_layout = QHBoxLayout(gaming_group)
        
        gaming_profiles = [
            ("FPS", ColorSchemes.GAMING_RED),
            ("MOBA", ColorSchemes.GAMING_BLUE),
            ("Racing", ColorSchemes.GAMING_GREEN),
            ("RPG", ColorSchemes.GAMING_PURPLE)
        ]
        
        for name, color in gaming_profiles:
            btn = QPushButton(f"{name} Mode")
            btn.clicked.connect(lambda checked, c=color: self.apply_gaming_profile(c))
            gaming_layout.addWidget(btn)
        
        layout.addWidget(gaming_group)
        
        self.tab_widget.addTab(rgb_widget, "🌈 RGB")
    
    def create_audio_tab(self):
        """Create audio enhancement tab"""
        audio_widget = QWidget()
        layout = QVBoxLayout(audio_widget)
        
        # Audio Profiles
        profile_group = QGroupBox("🎵 Audio Profiles")
        profile_layout = QHBoxLayout(profile_group)
        
        self.audio_profile_combo = QComboBox()
        if self.audio_manager:
            self.audio_profile_combo.addItems(self.audio_manager.get_available_profiles())
        else:
            self.audio_profile_combo.addItems(["Gaming", "Music", "Voice", "Streaming"])
        self.audio_profile_combo.currentTextChanged.connect(self.on_audio_profile_changed)
        
        profile_layout.addWidget(QLabel("Profile:"))
        profile_layout.addWidget(self.audio_profile_combo)
        
        layout.addWidget(profile_group)
        
        # Microphone Enhancement
        mic_group = QGroupBox("🎤 Microphone Enhancement")
        mic_layout = QVBoxLayout(mic_group)
        
        self.noise_reduction_checkbox = QCheckBox("Noise Reduction")
        self.echo_cancellation_checkbox = QCheckBox("Echo Cancellation")
        self.voice_clarity_checkbox = QCheckBox("Voice Clarity Enhancement")
        
        self.noise_reduction_checkbox.toggled.connect(self.on_noise_reduction_toggled)
        self.echo_cancellation_checkbox.toggled.connect(self.on_echo_cancellation_toggled)
        
        mic_layout.addWidget(self.noise_reduction_checkbox)
        mic_layout.addWidget(self.echo_cancellation_checkbox)
        mic_layout.addWidget(self.voice_clarity_checkbox)
        
        layout.addWidget(mic_group)
        
        # Equalizer
        eq_group = QGroupBox("🎛️ Equalizer")
        eq_layout = QVBoxLayout(eq_group)
        
        eq_presets = QPushButton("Load Gaming EQ")
        eq_presets.clicked.connect(self.load_gaming_equalizer)
        eq_layout.addWidget(eq_presets)
        
        layout.addWidget(eq_group)
        
        self.tab_widget.addTab(audio_widget, "🎵 Audio")
    
    def create_performance_tab(self):
        """Create performance monitoring tab"""
        perf_widget = QWidget()
        layout = QVBoxLayout(perf_widget)
        
        # Performance Overview
        overview_group = QGroupBox("📊 Performance Overview")
        overview_layout = QGridLayout(overview_group)
        
        self.cpu_usage_bar = QProgressBar()
        self.memory_usage_bar = QProgressBar()
        self.gpu_usage_bar = QProgressBar()
        
        self.cpu_usage_label = QLabel("CPU: 0%")
        self.memory_usage_label = QLabel("Memory: 0%")
        self.gpu_usage_label = QLabel("GPU: 0%")
        
        overview_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        overview_layout.addWidget(self.cpu_usage_label, 0, 1)
        overview_layout.addWidget(self.cpu_usage_bar, 0, 2)
        overview_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        overview_layout.addWidget(self.memory_usage_label, 1, 1)
        overview_layout.addWidget(self.memory_usage_bar, 1, 2)
        overview_layout.addWidget(QLabel("GPU Usage:"), 2, 0)
        overview_layout.addWidget(self.gpu_usage_label, 2, 1)
        overview_layout.addWidget(self.gpu_usage_bar, 2, 2)
        
        layout.addWidget(overview_group)
        
        # Power Management
        power_group = QGroupBox("⚡ Power Management")
        power_layout = QGridLayout(power_group)
        
        self.platform_profile_combo = QComboBox()
        if self.power_manager:
            profiles = self.power_manager.get_available_platform_profiles()
            self.platform_profile_combo.addItems(profiles)
        else:
            self.platform_profile_combo.addItems(["balanced", "performance", "power-saver"])
        self.platform_profile_combo.currentTextChanged.connect(self.on_platform_profile_changed)
        
        self.cpu_boost_checkbox = QCheckBox("CPU Boost")
        self.cpu_boost_checkbox.toggled.connect(self.on_cpu_boost_toggled)
        
        power_layout.addWidget(QLabel("Platform Profile:"), 0, 0)
        power_layout.addWidget(self.platform_profile_combo, 0, 1)
        power_layout.addWidget(self.cpu_boost_checkbox, 1, 0, 1, 2)
        
        layout.addWidget(power_group)
        
        # Display Controls
        display_group = QGroupBox("🖥️ Display Controls")
        display_layout = QGridLayout(display_group)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(10, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        
        self.panel_overdrive_checkbox = QCheckBox("Panel Overdrive")
        self.panel_overdrive_checkbox.toggled.connect(self.on_panel_overdrive_toggled)
        
        display_layout.addWidget(QLabel("Brightness:"), 0, 0)
        display_layout.addWidget(self.brightness_slider, 0, 1)
        display_layout.addWidget(self.panel_overdrive_checkbox, 1, 0, 1, 2)
        
        layout.addWidget(display_group)
        
        self.tab_widget.addTab(perf_widget, "📊 Performance")
    
    def update_status(self):
        """Update all status displays"""
        try:
            # Update temperature monitoring
            if self.temp_monitor:
                cpu_temp = self.temp_monitor.get_cpu_temperature()
                if cpu_temp:
                    self.cpu_temp_label.setText(f"CPU: {cpu_temp:.1f}°C")
                    temp_percent = min(100, max(0, (cpu_temp - 30) * 100 / 50))  # 30-80°C range
                    self.cpu_temp_bar.setValue(int(temp_percent))
                    
                    # Update temperature-based RGB color
                    if self.aura_manager and self.aura_manager.is_available():
                        temp_color = ColorSchemes.get_temperature_color(cpu_temp)
                        # Could apply temperature-based lighting here
            
            # Update fan speeds
            if self.fan_controller:
                fan_speeds = self.fan_controller.get_fan_speeds()
                if fan_speeds:
                    avg_speed = sum(fan_speeds.values()) // len(fan_speeds)
                    self.fan_speed_label.setText(f"Fan Speed: {avg_speed} RPM")
            
            # Update performance metrics
            if self.perf_monitor:
                self.perf_monitor.update_metrics()
                stats = self.perf_monitor.get_current_stats()
                
                if stats.get('cpu'):
                    cpu_percent = stats['cpu'].get('percent', 0)
                    self.cpu_usage_label.setText(f"CPU: {cpu_percent:.1f}%")
                    self.cpu_usage_bar.setValue(int(cpu_percent))
                
                if stats.get('memory'):
                    mem_percent = stats['memory'].get('percent', 0)
                    self.memory_usage_label.setText(f"Memory: {mem_percent:.1f}%")
                    self.memory_usage_bar.setValue(int(mem_percent))
                
                if stats.get('gpu'):
                    gpu_percent = stats['gpu'].get('utilization', 0)
                    self.gpu_usage_label.setText(f"GPU: {gpu_percent:.1f}%")
                    self.gpu_usage_bar.setValue(int(gpu_percent))
            
            # Update battery health
            if self.battery_manager:
                battery_info = self.battery_manager.get_battery_health_info()
                health = battery_info.get('health_percentage')
                cycles = battery_info.get('cycle_count')
                
                if health:
                    self.battery_health_label.setText(f"Health: {health}%")
                if cycles:
                    self.cycle_count_label.setText(f"Cycles: {cycles}")
        
        except Exception as e:
            self.logger.debug(f"Status update error: {e}")
    
    def on_fan_mode_changed(self, mode):
        """Handle fan mode change"""
        self.manual_fan_slider.setEnabled(mode == "Manual")
        if mode != "Manual" and self.fan_controller:
            # Apply preset fan curve
            self.logger.info(f"Fan mode changed to: {mode}")
    
    def on_manual_fan_changed(self, value):
        """Handle manual fan speed change"""
        if self.fan_controller:
            success = self.fan_controller.set_manual_fan_speed("cpu", value)
            if success:
                self.logger.info(f"Manual fan speed set to: {value}%")
    
    def on_charge_limit_changed(self, limit):
        """Handle battery charge limit change"""
        if self.battery_manager:
            success = self.battery_manager.set_charge_limit(limit)
            if success:
                self.logger.info(f"Battery charge limit set to: {limit}%")
    
    def on_lighting_effect_changed(self, effect):
        """Handle lighting effect change"""
        if self.aura_manager and self.aura_manager.is_available():
            # Apply the selected effect
            self.logger.info(f"Lighting effect changed to: {effect}")
    
    def on_color_selected(self, color):
        """Handle color selection"""
        if self.aura_manager and self.aura_manager.is_available():
            zone = AuraZone.KEYBOARD  # Default to keyboard
            effect = AuraEffect.STATIC
            speed = self.lighting_speed_slider.value()
            brightness = self.lighting_brightness_slider.value()
            
            success = self.aura_manager.set_zone_effect(zone, effect, color, speed, brightness)
            if success:
                self.logger.info(f"Applied color {color.to_hex()} to {zone.value}")
    
    def apply_gaming_profile(self, color):
        """Apply a gaming RGB profile"""
        if self.aura_manager and self.aura_manager.is_available():
            # Apply gaming effect with the selected color
            success = self.aura_manager.set_zone_effect(
                AuraZone.KEYBOARD, 
                AuraEffect.PULSE, 
                color, 
                speed=4, 
                brightness=3
            )
            if success:
                self.logger.info(f"Applied gaming profile with color {color.to_hex()}")
    
    def on_audio_profile_changed(self, profile):
        """Handle audio profile change"""
        if self.audio_manager:
            success = self.audio_manager.apply_profile(profile.lower())
            if success:
                self.logger.info(f"Applied audio profile: {profile}")
    
    def on_noise_reduction_toggled(self, enabled):
        """Handle noise reduction toggle"""
        if self.audio_manager and hasattr(self.audio_manager, 'microphone'):
            if enabled:
                self.audio_manager.microphone.enable_noise_reduction()
            else:
                self.audio_manager.microphone.disable_noise_reduction()
    
    def on_echo_cancellation_toggled(self, enabled):
        """Handle echo cancellation toggle"""
        if self.audio_manager and hasattr(self.audio_manager, 'microphone'):
            if enabled:
                self.audio_manager.microphone.enable_echo_cancellation()
            else:
                self.audio_manager.microphone.disable_echo_cancellation()
    
    def load_gaming_equalizer(self):
        """Load gaming equalizer preset"""
        if self.audio_manager:
            success = self.audio_manager.apply_profile('gaming')
            if success:
                self.logger.info("Applied gaming equalizer preset")
    
    def on_platform_profile_changed(self, profile):
        """Handle platform profile change"""
        if self.power_manager:
            success = self.power_manager.set_platform_profile(profile)
            if success:
                self.logger.info(f"Platform profile changed to: {profile}")
    
    def on_cpu_boost_toggled(self, enabled):
        """Handle CPU boost toggle"""
        if self.power_manager:
            success = self.power_manager.set_cpu_boost(enabled)
            if success:
                self.logger.info(f"CPU boost {'enabled' if enabled else 'disabled'}")
    
    def on_brightness_changed(self, value):
        """Handle brightness change"""
        if self.display_manager:
            success = self.display_manager.set_brightness(value)
            if success:
                self.logger.info(f"Brightness set to: {value}%")
    
    def on_panel_overdrive_toggled(self, enabled):
        """Handle panel overdrive toggle"""
        if self.display_manager:
            success = self.display_manager.set_panel_overdrive(enabled)
            if success:
                self.logger.info(f"Panel overdrive {'enabled' if enabled else 'disabled'}")


# For testing without Qt
if not PYSIDE6_AVAILABLE:
    class EnhancedControlsWidget:
        def __init__(self):
            print("Enhanced controls widget would be available with PySide6")
            print("Features include:")
            print("- Advanced temperature monitoring with fan curves")
            print("- RGB lighting control with gaming profiles")  
            print("- Audio enhancement with equalizer presets")
            print("- Performance monitoring dashboard")
            print("- Display and power management controls")