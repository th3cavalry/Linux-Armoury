#!/usr/bin/env python3
"""
Main entry point for Linux Armoury GUI application
"""

import sys
import os
import signal
from pathlib import Path

# Add the package directory to the Python path
package_dir = Path(__file__).parent.parent
sys.path.insert(0, str(package_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, QTimer
from PySide6.QtGui import QIcon

from linux_armoury.ui.main_window import MainWindow
from linux_armoury.ui.tray_icon import SystemTrayIcon
from linux_armoury.core.config import Config
from linux_armoury.core.utils import setup_logging


def handle_signal(signum, frame):
    """Handle system signals for graceful shutdown"""
    QApplication.quit()


def main():
    """Main application entry point"""
    # Handle signals for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Setup logging
    setup_logging()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Linux Armoury")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("th3cavalry")
    app.setQuitOnLastWindowClosed(False)  # Don't quit when main window closes
    
    # Load configuration
    config = Config()
    
    # Set application icon
    icon_path = Path(__file__).parent / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create main window
    main_window = MainWindow()
    
    # Create system tray icon
    tray_icon = SystemTrayIcon(main_window)
    
    # Show main window if not set to start minimized
    if not config.get("start_minimized", False):
        main_window.show()
    
    # Setup timer to handle Qt signals properly
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()