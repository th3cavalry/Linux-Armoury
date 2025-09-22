"""
Main window for Linux Armoury GUI application
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QFrame, QPushButton, QComboBox, QCheckBox, QGroupBox,
    QProgressBar, QTextEdit, QScrollArea, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QIcon

from linux_armoury.core.config import Config
from linux_armoury.core.utils import get_battery_info, get_cpu_info, get_memory_info, format_bytes, format_time
from linux_armoury.core.rog_integration import (
    ASUSCtlManager, SuperGfxCtlManager, TDPManager, RefreshRateManager
)
from linux_armoury.ui.update_tab import UpdateTab


class StatusWidget(QFrame):
    """Widget showing system status information"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("System Status")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Status information
        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("Memory: --")
        self.battery_label = QLabel("Battery: --")
        self.temp_label = QLabel("Temperature: --")
        
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.battery_label)
        layout.addWidget(self.temp_label)
        
        layout.addStretch()
    
    def setup_timer(self):
        """Setup timer for updating status"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Initial update
        self.update_status()
    
    def update_status(self):
        """Update system status information"""
        # CPU info
        cpu_info = get_cpu_info()
        self.cpu_label.setText(f"CPU: {cpu_info['usage']:.1f}% @ {cpu_info['frequency']:.0f}MHz")
        self.temp_label.setText(f"Temperature: {cpu_info['temperature']:.1f}°C")
        
        # Memory info
        memory_info = get_memory_info()
        memory_used = format_bytes(memory_info['used'])
        memory_total = format_bytes(memory_info['total'])
        self.memory_label.setText(f"Memory: {memory_used}/{memory_total} ({memory_info['percent']:.1f}%)")
        
        # Battery info
        battery_info = get_battery_info()
        power_source = "AC" if battery_info['plugged'] else "Battery"
        time_left = format_time(battery_info['time_left']) if battery_info['time_left'] else ""
        self.battery_label.setText(f"Battery: {battery_info['percent']:.0f}% ({power_source}) {time_left}")


class ControlWidget(QFrame):
    """Widget for ROG laptop controls"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.init_managers()
        self.init_ui()
        self.load_current_settings()
    
    def init_managers(self):
        """Initialize ROG control managers"""
        self.asus_manager = ASUSCtlManager()
        self.gpu_manager = SuperGfxCtlManager()
        self.tdp_manager = TDPManager()
        self.refresh_manager = RefreshRateManager()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("ROG Controls")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # ASUS Profile
        if self.asus_manager.is_available():
            asus_group = QGroupBox("ASUS Performance Profile")
            asus_layout = QHBoxLayout(asus_group)
            
            self.asus_combo = QComboBox()
            self.asus_combo.addItems(self.asus_manager.get_profiles())
            self.asus_combo.currentTextChanged.connect(self.on_asus_profile_changed)
            
            asus_layout.addWidget(QLabel("Profile:"))
            asus_layout.addWidget(self.asus_combo)
            asus_layout.addStretch()
            
            layout.addWidget(asus_group)
        
        # GPU Mode
        if self.gpu_manager.is_available():
            gpu_group = QGroupBox("GPU Mode")
            gpu_layout = QHBoxLayout(gpu_group)
            
            self.gpu_combo = QComboBox()
            self.gpu_combo.addItems(self.gpu_manager.get_gpu_modes())
            self.gpu_combo.currentTextChanged.connect(self.on_gpu_mode_changed)
            
            gpu_layout.addWidget(QLabel("Mode:"))
            gpu_layout.addWidget(self.gpu_combo)
            gpu_layout.addStretch()
            
            layout.addWidget(gpu_group)
        
        # TDP Management
        if self.tdp_manager.is_available():
            tdp_group = QGroupBox("TDP Management")
            tdp_layout = QHBoxLayout(tdp_group)
            
            self.tdp_combo = QComboBox()
            self.tdp_combo.addItems(self.tdp_manager.get_profiles())
            self.tdp_combo.currentTextChanged.connect(self.on_tdp_profile_changed)
            
            tdp_layout.addWidget(QLabel("Profile:"))
            tdp_layout.addWidget(self.tdp_combo)
            tdp_layout.addStretch()
            
            layout.addWidget(tdp_group)
        
        # Refresh Rate Management
        if self.refresh_manager.is_available():
            refresh_group = QGroupBox("Refresh Rate")
            refresh_layout = QVBoxLayout(refresh_group)
            
            # Profile selection
            profile_layout = QHBoxLayout()
            self.refresh_combo = QComboBox()
            self.refresh_combo.addItems(self.refresh_manager.get_profiles())
            self.refresh_combo.currentTextChanged.connect(self.on_refresh_profile_changed)
            
            profile_layout.addWidget(QLabel("Profile:"))
            profile_layout.addWidget(self.refresh_combo)
            profile_layout.addStretch()
            
            # VRR toggle
            self.vrr_checkbox = QCheckBox("Variable Refresh Rate (VRR)")
            self.vrr_checkbox.toggled.connect(self.on_vrr_toggled)
            
            refresh_layout.addLayout(profile_layout)
            refresh_layout.addWidget(self.vrr_checkbox)
            
            layout.addWidget(refresh_group)
        
        # Auto-switching
        auto_group = QGroupBox("Automatic Switching")
        auto_layout = QVBoxLayout(auto_group)
        
        self.auto_switch_checkbox = QCheckBox("Auto-switch profiles based on power source")
        self.auto_switch_checkbox.setChecked(self.config.get("auto_switch_power", True))
        self.auto_switch_checkbox.toggled.connect(self.on_auto_switch_toggled)
        
        auto_layout.addWidget(self.auto_switch_checkbox)
        layout.addWidget(auto_group)
        
        layout.addStretch()
    
    def load_current_settings(self):
        """Load current settings from the system"""
        # Load ASUS profile
        if hasattr(self, 'asus_combo') and self.asus_manager.is_available():
            current_profile = self.asus_manager.get_current_profile()
            if current_profile:
                index = self.asus_combo.findText(current_profile)
                if index >= 0:
                    self.asus_combo.setCurrentIndex(index)
        
        # Load GPU mode
        if hasattr(self, 'gpu_combo') and self.gpu_manager.is_available():
            current_mode = self.gpu_manager.get_current_gpu_mode()
            if current_mode:
                index = self.gpu_combo.findText(current_mode)
                if index >= 0:
                    self.gpu_combo.setCurrentIndex(index)
        
        # Load saved profiles from config
        if hasattr(self, 'tdp_combo'):
            saved_profile = self.config.get("tdp_profile", "balanced")
            index = self.tdp_combo.findText(saved_profile)
            if index >= 0:
                self.tdp_combo.setCurrentIndex(index)
        
        if hasattr(self, 'refresh_combo'):
            saved_profile = self.config.get("refresh_rate_profile", "balanced")
            index = self.refresh_combo.findText(saved_profile)
            if index >= 0:
                self.refresh_combo.setCurrentIndex(index)
    
    def on_asus_profile_changed(self, profile):
        """Handle ASUS profile change"""
        if self.asus_manager.set_profile(profile):
            self.config.set("asus_profile", profile)
            self.config.save()
    
    def on_gpu_mode_changed(self, mode):
        """Handle GPU mode change"""
        if self.gpu_manager.set_gpu_mode(mode):
            self.config.set("gpu_mode", mode)
            self.config.save()
            
            # Check if reboot is needed
            if self.gpu_manager.needs_reboot():
                QMessageBox.information(
                    self, 
                    "Reboot Required", 
                    "A reboot is required for the GPU mode change to take effect."
                )
    
    def on_tdp_profile_changed(self, profile):
        """Handle TDP profile change"""
        if self.tdp_manager.set_profile(profile):
            self.config.set("tdp_profile", profile)
            self.config.save()
    
    def on_refresh_profile_changed(self, profile):
        """Handle refresh rate profile change"""
        if self.refresh_manager.set_profile(profile):
            self.config.set("refresh_rate_profile", profile)
            self.config.save()
    
    def on_vrr_toggled(self, enabled):
        """Handle VRR toggle"""
        if self.refresh_manager.toggle_vrr(enabled):
            self.config.set("vrr_enabled", enabled)
            self.config.save()
    
    def on_auto_switch_toggled(self, enabled):
        """Handle auto-switch toggle"""
        self.config.set("auto_switch_power", enabled)
        self.config.save()


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    minimize_to_tray = Signal()
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        self.restore_geometry()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Linux Armoury")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Status and Controls
        left_panel = QVBoxLayout()
        
        # Status widget
        self.status_widget = StatusWidget()
        left_panel.addWidget(self.status_widget)
        
        # Control widget
        self.control_widget = ControlWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.control_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(300)
        left_panel.addWidget(scroll_area)
        
        # Right panel - Tabs
        self.tab_widget = QTabWidget()
        
        # Update tab
        self.update_tab = UpdateTab()
        self.tab_widget.addTab(self.update_tab, "Updates")
        
        # Settings tab (placeholder)
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        settings_label = QLabel("Settings")
        settings_label.setFont(QFont("", 12, QFont.Bold))
        settings_layout.addWidget(settings_label)
        
        # Auto-start checkbox
        self.autostart_checkbox = QCheckBox("Start automatically on boot")
        self.autostart_checkbox.setChecked(self.config.get("auto_start", False))
        self.autostart_checkbox.toggled.connect(self.on_autostart_toggled)
        settings_layout.addWidget(self.autostart_checkbox)
        
        # Start minimized checkbox
        self.start_minimized_checkbox = QCheckBox("Start minimized to system tray")
        self.start_minimized_checkbox.setChecked(self.config.get("start_minimized", False))
        self.start_minimized_checkbox.toggled.connect(self.on_start_minimized_toggled)
        settings_layout.addWidget(self.start_minimized_checkbox)
        
        # Notifications checkbox
        self.notifications_checkbox = QCheckBox("Show notifications")
        self.notifications_checkbox.setChecked(self.config.get("show_notifications", True))
        self.notifications_checkbox.toggled.connect(self.on_notifications_toggled)
        settings_layout.addWidget(self.notifications_checkbox)
        
        settings_layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "Settings")
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.tab_widget, 2)
    
    def restore_geometry(self):
        """Restore window geometry from config"""
        geometry = self.config.get("window_geometry")
        if geometry:
            try:
                x, y, width, height = geometry
                self.setGeometry(x, y, width, height)
            except (ValueError, TypeError):
                pass
    
    def save_geometry(self):
        """Save window geometry to config"""
        geometry = self.geometry()
        self.config.set("window_geometry", [geometry.x(), geometry.y(), geometry.width(), geometry.height()])
        self.config.save()
    
    def on_autostart_toggled(self, enabled):
        """Handle autostart toggle"""
        from linux_armoury.core.utils import create_desktop_entry, remove_autostart
        
        self.config.set("auto_start", enabled)
        self.config.save()
        
        if enabled:
            create_desktop_entry(autostart=True)
        else:
            remove_autostart()
    
    def on_start_minimized_toggled(self, enabled):
        """Handle start minimized toggle"""
        self.config.set("start_minimized", enabled)
        self.config.save()
    
    def on_notifications_toggled(self, enabled):
        """Handle notifications toggle"""
        self.config.set("show_notifications", enabled)
        self.config.save()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        self.minimize_to_tray.emit()
        
        # Save geometry
        self.save_geometry()
    
    def show_and_raise(self):
        """Show window and bring to front"""
        self.show()
        self.raise_()
        self.activateWindow()