"""
System tray icon for Linux Armoury
"""

import logging
from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QApplication, QMessageBox, QWidgetAction, QLabel,
    QVBoxLayout, QWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QFont, QAction

from linux_armoury.core.config import Config
from linux_armoury.core.utils import get_battery_info, get_cpu_info


class QuickStatusWidget(QWidget):
    """Quick status widget for tray menu"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title = QLabel("Quick Status")
        title.setFont(QFont("", 9, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status labels
        self.cpu_label = QLabel("CPU: --")
        self.battery_label = QLabel("Battery: --")
        self.temp_label = QLabel("Temp: --")
        
        for label in [self.cpu_label, self.battery_label, self.temp_label]:
            label.setFont(QFont("", 8))
            layout.addWidget(label)
        
        self.setFixedWidth(150)
    
    def setup_timer(self):
        """Setup timer for status updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # Update every 5 seconds
        self.update_status()
    
    def update_status(self):
        """Update status information"""
        # CPU info
        cpu_info = get_cpu_info()
        self.cpu_label.setText(f"CPU: {cpu_info['usage']:.0f}%")
        self.temp_label.setText(f"Temp: {cpu_info['temperature']:.0f}°C")
        
        # Battery info
        battery_info = get_battery_info()
        power_source = "AC" if battery_info['plugged'] else "Bat"
        self.battery_label.setText(f"Battery: {battery_info['percent']:.0f}% ({power_source})")


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for Linux Armoury"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        self.create_icon()
        self.create_menu()
        self.setup_connections()
        
        # Show the tray icon
        self.show()
        
        # Show initial message if notifications are enabled
        if self.config.get("show_notifications", True):
            self.showMessage(
                "Linux Armoury",
                "Application started and running in system tray",
                QSystemTrayIcon.Information,
                3000
            )
    
    def create_icon(self):
        """Create the tray icon"""
        # Create a simple icon if no icon file exists
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.blue)
        painter.setPen(Qt.white)
        painter.drawEllipse(2, 2, 12, 12)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "LA")
        painter.end()
        
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setToolTip("Linux Armoury - ASUS ROG Control")
    
    def create_menu(self):
        """Create the context menu"""
        menu = QMenu()
        
        # Quick status widget
        self.status_widget = QuickStatusWidget()
        status_action = QWidgetAction(menu)
        status_action.setDefaultWidget(self.status_widget)
        menu.addAction(status_action)
        
        menu.addSeparator()
        
        # Main window actions
        show_action = QAction("Show Window", menu)
        show_action.triggered.connect(self.show_main_window)
        menu.addAction(show_action)
        
        hide_action = QAction("Hide Window", menu)
        hide_action.triggered.connect(self.hide_main_window)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        # Quick profile actions
        profiles_menu = menu.addMenu("Quick Profiles")
        
        # TDP profiles
        tdp_menu = profiles_menu.addMenu("TDP")
        tdp_profiles = ["gaming", "performance", "balanced", "efficient", "power_saver"]
        for profile in tdp_profiles:
            action = QAction(profile.title(), tdp_menu)
            action.triggered.connect(lambda checked, p=profile: self.set_tdp_profile(p))
            tdp_menu.addAction(action)
        
        # Refresh rate profiles
        refresh_menu = profiles_menu.addMenu("Refresh Rate")
        refresh_profiles = ["gaming", "performance", "balanced", "efficient", "power_saver", "ultra_low"]
        for profile in refresh_profiles:
            action = QAction(profile.replace("_", " ").title(), refresh_menu)
            action.triggered.connect(lambda checked, p=profile: self.set_refresh_profile(p))
            refresh_menu.addAction(action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings", menu)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # About
        about_action = QAction("About", menu)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect tray icon activation
        self.activated.connect(self.on_tray_activated)
        
        # Connect main window signal
        self.main_window.minimize_to_tray.connect(self.on_minimized_to_tray)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_main_window()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - could show a quick status tooltip
            pass
    
    def on_minimized_to_tray(self):
        """Handle minimize to tray signal"""
        if self.config.get("show_notifications", True):
            self.showMessage(
                "Linux Armoury",
                "Application minimized to system tray",
                QSystemTrayIcon.Information,
                2000
            )
    
    def toggle_main_window(self):
        """Toggle main window visibility"""
        if self.main_window.isVisible():
            self.hide_main_window()
        else:
            self.show_main_window()
    
    def show_main_window(self):
        """Show the main window"""
        self.main_window.show_and_raise()
    
    def hide_main_window(self):
        """Hide the main window"""
        self.main_window.hide()
    
    def set_tdp_profile(self, profile):
        """Set TDP profile via tray menu"""
        try:
            from linux_armoury.core.rog_integration import TDPManager
            tdp_manager = TDPManager()
            
            if tdp_manager.is_available():
                if tdp_manager.set_profile(profile):
                    if self.config.get("show_notifications", True):
                        self.showMessage(
                            "TDP Profile Changed",
                            f"TDP profile set to {profile}",
                            QSystemTrayIcon.Information,
                            2000
                        )
                    
                    # Update config
                    self.config.set("tdp_profile", profile)
                    self.config.save()
                else:
                    self.showMessage(
                        "Error",
                        f"Failed to set TDP profile to {profile}",
                        QSystemTrayIcon.Critical,
                        3000
                    )
            else:
                self.showMessage(
                    "Error",
                    "TDP management not available",
                    QSystemTrayIcon.Warning,
                    3000
                )
        except Exception as e:
            self.logger.error(f"Error setting TDP profile: {e}")
    
    def set_refresh_profile(self, profile):
        """Set refresh rate profile via tray menu"""
        try:
            from linux_armoury.core.rog_integration import RefreshRateManager
            refresh_manager = RefreshRateManager()
            
            if refresh_manager.is_available():
                if refresh_manager.set_profile(profile):
                    if self.config.get("show_notifications", True):
                        self.showMessage(
                            "Refresh Rate Changed",
                            f"Refresh rate profile set to {profile.replace('_', ' ')}",
                            QSystemTrayIcon.Information,
                            2000
                        )
                    
                    # Update config
                    self.config.set("refresh_rate_profile", profile)
                    self.config.save()
                else:
                    self.showMessage(
                        "Error",
                        f"Failed to set refresh rate profile to {profile}",
                        QSystemTrayIcon.Critical,
                        3000
                    )
            else:
                self.showMessage(
                    "Error",
                    "Refresh rate management not available",
                    QSystemTrayIcon.Warning,
                    3000
                )
        except Exception as e:
            self.logger.error(f"Error setting refresh rate profile: {e}")
    
    def show_settings(self):
        """Show settings tab in main window"""
        self.show_main_window()
        # Switch to settings tab (assuming it's the second tab)
        self.main_window.tab_widget.setCurrentIndex(1)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            None,
            "About Linux Armoury",
            """<h3>Linux Armoury v1.0.0</h3>
            <p>A sleek GUI application for controlling ASUS ROG laptops on Linux.</p>
            <p><b>Features:</b></p>
            <ul>
            <li>TDP Management</li>
            <li>Refresh Rate Control</li>
            <li>GPU Mode Switching</li>
            <li>System Tray Integration</li>
            <li>Package Updates</li>
            </ul>
            <p><b>Author:</b> th3cavalry</p>
            <p><b>License:</b> MIT</p>
            <p>For ASUS ROG Flow Z13 (GZ302) and compatible devices.</p>"""
        )
    
    def quit_application(self):
        """Quit the application"""
        self.hide()
        QApplication.quit()
    
    def update_icon_status(self, status_info):
        """Update icon based on system status"""
        # This could be used to change icon color based on temperature, battery, etc.
        # For now, just update the tooltip
        cpu_temp = status_info.get('temperature', 0)
        battery_percent = status_info.get('battery_percent', 0)
        power_source = "AC" if status_info.get('on_ac', True) else "Battery"
        
        tooltip = f"""Linux Armoury
CPU: {cpu_temp:.0f}°C
Battery: {battery_percent:.0f}% ({power_source})
Right-click for options"""
        
        self.setToolTip(tooltip)