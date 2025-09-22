"""
Update tab for managing laptop-specific packages and drivers
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget,
    QTreeWidgetItem, QProgressBar, QTextEdit, QGroupBox, QCheckBox,
    QMessageBox, QScrollArea, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIcon

from linux_armoury.core.update_manager import UpdateManager, PackageInfo
from linux_armoury.core.config import Config


class UpdateWorker(QThread):
    """Worker thread for checking updates"""
    
    update_progress = Signal(str)
    update_finished = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, update_manager):
        super().__init__()
        self.update_manager = update_manager
    
    def run(self):
        """Run update check"""
        try:
            self.update_progress.emit("Checking for updates...")
            updates = self.update_manager.check_updates()
            self.update_finished.emit(updates)
        except Exception as e:
            self.error_occurred.emit(str(e))


class InstallWorker(QThread):
    """Worker thread for installing updates"""
    
    install_progress = Signal(str)
    install_finished = Signal(bool)
    error_occurred = Signal(str)
    
    def __init__(self, update_manager, packages):
        super().__init__()
        self.update_manager = update_manager
        self.packages = packages
    
    def run(self):
        """Run package installation"""
        try:
            self.install_progress.emit(f"Installing {len(self.packages)} packages...")
            success = self.update_manager.install_updates(self.packages)
            self.install_finished.emit(success)
        except Exception as e:
            self.error_occurred.emit(str(e))


class SystemInfoWidget(QFrame):
    """Widget showing system information"""
    
    def __init__(self, update_manager):
        super().__init__()
        self.update_manager = update_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("System Information")
        title.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(title)
        
        # System info
        sys_info = self.update_manager.get_system_info()
        
        for key, value in sys_info.items():
            info_layout = QHBoxLayout()
            key_label = QLabel(f"{key}:")
            key_label.setMinimumWidth(120)
            key_label.setFont(QFont("", 9, QFont.Bold))
            
            value_label = QLabel(str(value))
            value_label.setFont(QFont("", 9))
            
            info_layout.addWidget(key_label)
            info_layout.addWidget(value_label)
            info_layout.addStretch()
            
            layout.addLayout(info_layout)
        
        layout.addStretch()


class UpdateTab(QWidget):
    """Tab widget for managing updates"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.update_manager = UpdateManager()
        self.available_updates = {}
        self.selected_packages = []
        
        self.init_ui()
        self.setup_auto_check()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout(self)
        
        # Create splitter for layout
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - System info and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # System info
        self.system_info_widget = SystemInfoWidget(self.update_manager)
        left_layout.addWidget(self.system_info_widget)
        
        # Update controls
        controls_group = QGroupBox("Update Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Check updates button
        self.check_button = QPushButton("Check for Updates")
        self.check_button.clicked.connect(self.check_updates)
        controls_layout.addWidget(self.check_button)
        
        # Auto-check checkbox
        self.auto_check_checkbox = QCheckBox("Check automatically")
        self.auto_check_checkbox.setChecked(self.config.get("check_updates", True))
        self.auto_check_checkbox.toggled.connect(self.on_auto_check_toggled)
        controls_layout.addWidget(self.auto_check_checkbox)
        
        # Install button
        self.install_button = QPushButton("Install Selected Updates")
        self.install_button.setEnabled(False)
        self.install_button.clicked.connect(self.install_updates)
        controls_layout.addWidget(self.install_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("", 9))
        controls_layout.addWidget(self.status_label)
        
        left_layout.addWidget(controls_group)
        left_layout.addStretch()
        
        # Right panel - Updates list
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Updates tree
        updates_label = QLabel("Available Updates")
        updates_label.setFont(QFont("", 12, QFont.Bold))
        right_layout.addWidget(updates_label)
        
        self.updates_tree = QTreeWidget()
        self.updates_tree.setHeaderLabels(["Package", "Current", "Available", "Description"])
        self.updates_tree.setRootIsDecorated(True)
        self.updates_tree.itemChanged.connect(self.on_item_changed)
        right_layout.addWidget(self.updates_tree)
        
        # Update log
        log_label = QLabel("Update Log")
        log_label.setFont(QFont("", 10, QFont.Bold))
        right_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("monospace", 8))
        right_layout.addWidget(self.log_text)
        
        # Add panels to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([200, 400])
        
        # Initial update check
        QTimer.singleShot(1000, self.check_updates)
    
    def setup_auto_check(self):
        """Setup automatic update checking"""
        self.auto_check_timer = QTimer()
        self.auto_check_timer.timeout.connect(self.check_updates)
        
        if self.config.get("check_updates", True):
            interval = self.config.get("update_interval", 3600) * 1000  # Convert to ms
            self.auto_check_timer.start(interval)
    
    def check_updates(self):
        """Check for available updates"""
        if hasattr(self, 'update_worker') and self.update_worker.isRunning():
            return
        
        self.log_text.append("Starting update check...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.check_button.setEnabled(False)
        self.status_label.setText("Checking for updates...")
        
        # Start worker thread
        self.update_worker = UpdateWorker(self.update_manager)
        self.update_worker.update_progress.connect(self.on_update_progress)
        self.update_worker.update_finished.connect(self.on_update_finished)
        self.update_worker.error_occurred.connect(self.on_update_error)
        self.update_worker.start()
    
    def on_update_progress(self, message):
        """Handle update progress"""
        self.status_label.setText(message)
        self.log_text.append(message)
    
    def on_update_finished(self, updates):
        """Handle update check completion"""
        self.available_updates = updates
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)
        
        # Update the tree widget
        self.populate_updates_tree(updates)
        
        # Update status
        total_updates = sum(len(packages) for packages in updates.values())
        if total_updates > 0:
            self.status_label.setText(f"Found {total_updates} available updates")
            self.log_text.append(f"Found {total_updates} available updates")
        else:
            self.status_label.setText("No updates available")
            self.log_text.append("No updates available")
    
    def on_update_error(self, error):
        """Handle update check error"""
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)
        self.status_label.setText("Error checking updates")
        self.log_text.append(f"Error: {error}")
        
        QMessageBox.warning(self, "Update Check Error", f"Failed to check for updates:\n{error}")
    
    def populate_updates_tree(self, updates):
        """Populate the updates tree widget"""
        self.updates_tree.clear()
        
        for category, packages in updates.items():
            # Create category item
            category_item = QTreeWidgetItem(self.updates_tree)
            category_item.setText(0, f"{category} ({len(packages)} updates)")
            category_item.setFont(0, QFont("", 10, QFont.Bold))
            category_item.setExpanded(True)
            
            # Add package items
            for package in packages:
                package_item = QTreeWidgetItem(category_item)
                package_item.setText(0, package.name)
                package_item.setText(1, package.current_version)
                package_item.setText(2, package.available_version)
                package_item.setText(3, package.description[:50] + "..." if len(package.description) > 50 else package.description)
                
                # Make it checkable
                package_item.setFlags(package_item.flags() | Qt.ItemIsUserCheckable)
                package_item.setCheckState(0, Qt.Unchecked)
                
                # Store package info
                package_item.setData(0, Qt.UserRole, package)
        
        # Resize columns
        for i in range(4):
            self.updates_tree.resizeColumnToContents(i)
    
    def on_item_changed(self, item, column):
        """Handle item check state change"""
        if column == 0 and item.parent():  # Only handle package items
            package = item.data(0, Qt.UserRole)
            if package:
                if item.checkState(0) == Qt.Checked:
                    if package.name not in self.selected_packages:
                        self.selected_packages.append(package.name)
                else:
                    if package.name in self.selected_packages:
                        self.selected_packages.remove(package.name)
                
                # Update install button state
                self.install_button.setEnabled(len(self.selected_packages) > 0)
    
    def install_updates(self):
        """Install selected updates"""
        if not self.selected_packages:
            return
        
        # Confirm installation
        reply = QMessageBox.question(
            self,
            "Install Updates",
            f"Install {len(self.selected_packages)} selected packages?\n\n"
            "This will require administrator privileges.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.log_text.append(f"Installing {len(self.selected_packages)} packages...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.install_button.setEnabled(False)
        self.status_label.setText("Installing updates...")
        
        # Start install worker
        self.install_worker = InstallWorker(self.update_manager, self.selected_packages.copy())
        self.install_worker.install_progress.connect(self.on_install_progress)
        self.install_worker.install_finished.connect(self.on_install_finished)
        self.install_worker.error_occurred.connect(self.on_install_error)
        self.install_worker.start()
    
    def on_install_progress(self, message):
        """Handle installation progress"""
        self.status_label.setText(message)
        self.log_text.append(message)
    
    def on_install_finished(self, success):
        """Handle installation completion"""
        self.progress_bar.setVisible(False)
        self.install_button.setEnabled(True)
        
        if success:
            self.status_label.setText("Installation completed successfully")
            self.log_text.append("Installation completed successfully")
            
            # Clear selections and refresh
            self.selected_packages.clear()
            QTimer.singleShot(2000, self.check_updates)
            
            QMessageBox.information(
                self,
                "Installation Complete",
                "Updates installed successfully!\n\nSome updates may require a reboot to take effect."
            )
        else:
            self.status_label.setText("Installation failed")
            self.log_text.append("Installation failed")
    
    def on_install_error(self, error):
        """Handle installation error"""
        self.progress_bar.setVisible(False)
        self.install_button.setEnabled(True)
        self.status_label.setText("Installation error")
        self.log_text.append(f"Installation error: {error}")
        
        QMessageBox.critical(self, "Installation Error", f"Failed to install updates:\n{error}")
    
    def on_auto_check_toggled(self, enabled):
        """Handle auto-check toggle"""
        self.config.set("check_updates", enabled)
        self.config.save()
        
        if enabled:
            interval = self.config.get("update_interval", 3600) * 1000
            self.auto_check_timer.start(interval)
        else:
            self.auto_check_timer.stop()