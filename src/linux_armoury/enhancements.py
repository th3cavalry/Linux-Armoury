"""
Enhancements Integration Module
Adds all new features (config, logging, toast, graphs, profiles) to the main GUI
"""

import logging
from pathlib import Path
from typing import Optional

import customtkinter as ctk

# Import our new modules
from .config_manager import ConfigManager
from .profile_manager import ProfileManager
from .widgets import MultiGraphPanel, ToastManager


def setup_logging() -> logging.Logger:
    """
    Set up application logging

    Returns:
        Configured logger instance
    """
    log_dir = Path.home() / ".config" / "linux-armoury"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "linux-armoury.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

    logger = logging.getLogger("LinuxArmoury")
    logger.info("=" * 60)
    logger.info("Linux Armoury Started")
    logger.info("=" * 60)

    return logger


class EnhancedAppMixin:
    """
    Mixin class that adds all enhancement features to the main GUI
    To use: class App(ctk.CTk, EnhancedAppMixin):
    """

    def init_enhancements(self):
        """Initialize all enhancement features"""
        # Set up logging
        self.logger = setup_logging()
        self.logger.info("Initializing enhancements...")

        # Config manager
        self.config = ConfigManager()
        self.logger.info(f"Config loaded: {len(self.config.all)} settings")

        # Toast manager
        self.toast_manager = ToastManager(self)
        self.logger.info("Toast notification system initialized")

        # Profile manager
        self.profile_manager = ProfileManager()
        profiles = self.profile_manager.list_profiles()
        builtin_count = len(profiles.get("builtin", []))
        custom_count = len(profiles.get("custom", []))
        self.logger.info(
            "Profiles loaded: %d builtin, %d custom",
            builtin_count,
            custom_count,
        )

        # Apply saved window settings
        self._apply_window_settings()

        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Set up save on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.logger.info("Enhancements initialized successfully")

    def _apply_window_settings(self):
        """Apply saved window position and size"""
        try:
            size = self.config.get("window_size", [1000, 650])
            self.geometry(f"{size[0]}x{size[1]}")

            position = self.config.get("window_position")
            if position:
                self.geometry(f"+{position[0]}+{position[1]}")

            self.logger.debug(f"Window settings applied: {size}")
        except Exception as e:
            self.logger.error(f"Failed to apply window settings: {e}")

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts"""
        try:
            # Navigation shortcuts (Ctrl+1-6)
            if hasattr(self, "show_dashboard"):
                self.bind("<Control-1>", lambda e: self.show_dashboard())
            if hasattr(self, "show_aura"):
                self.bind("<Control-2>", lambda e: self.show_aura())
            if hasattr(self, "show_performance"):
                self.bind("<Control-3>", lambda e: self.show_performance())
            if hasattr(self, "show_battery"):
                self.bind("<Control-4>", lambda e: self.show_battery())
            if hasattr(self, "show_fans"):
                self.bind("<Control-5>", lambda e: self.show_fans())
            if hasattr(self, "show_settings"):
                self.bind("<Control-6>", lambda e: self.show_settings())

            # Quick actions
            self.bind("<Control-q>", lambda e: self.quit())
            self.bind(
                "<F5>",
                lambda e: (
                    self._refresh_stats() if hasattr(self, "_refresh_stats") else None
                ),
            )

            # Profile shortcuts (Alt+1-4)
            self.bind("<Alt-1>", lambda e: self._quick_profile("Silent"))
            self.bind("<Alt-2>", lambda e: self._quick_profile("Balanced"))
            self.bind("<Alt-3>", lambda e: self._quick_profile("Gaming"))
            self.bind("<Alt-4>", lambda e: self._quick_profile("Turbo"))

            self.logger.info("Keyboard shortcuts configured")
        except Exception as e:
            self.logger.error(f"Failed to set up keyboard shortcuts: {e}")

    def _quick_profile(self, profile_name: str):
        """Quick profile switch via keyboard shortcut"""
        try:
            profile = self.profile_manager.get_profile(profile_name)
            if profile:
                self.profile_manager.apply_profile(profile, self)
                self.logger.info(f"Quick profile switch: {profile_name}")
        except Exception as e:
            self.logger.error(f"Failed to quick switch profile: {e}")

    def _on_closing(self):
        """Handle window close - save settings"""
        try:
            # Save window geometry
            geometry = self.geometry()
            # Parse: "1000x650+100+100"
            size_pos = geometry.split("+")
            size = size_pos[0].split("x")

            self.config.set("window_size", [int(size[0]), int(size[1])], save=False)

            if len(size_pos) >= 3:
                self.config.set(
                    "window_position", [int(size_pos[1]), int(size_pos[2])], save=False
                )

            # Save current profile
            if hasattr(self, "current_profile_name"):
                self.config.set(
                    "last_tdp_profile", self.current_profile_name, save=False
                )

            # Save auto profile switching state
            if hasattr(self, "auto_profile_switching"):
                self.config.set(
                    "auto_profile_switching", self.auto_profile_switching, save=False
                )

            # Save all at once
            self.config.save()

            self.logger.info("Settings saved on close")
            self.logger.info("Linux Armoury shutting down")

        except Exception as e:
            self.logger.error(f"Error saving settings on close: {e}")

        finally:
            self.destroy()

    def show_toast(self, message: str, type: str = "info"):
        """
        Show a toast notification

        Args:
            message: Message to display
            type: Notification type (success, error, info, warning)
        """
        try:
            duration = self.config.get("notification_duration", 5000)
            self.toast_manager.show(message, type, duration)
            self.logger.debug(f"Toast shown: [{type}] {message}")
        except Exception as e:
            self.logger.error(f"Failed to show toast: {e}")

    def create_monitoring_graphs(self, parent) -> Optional[MultiGraphPanel]:
        """
        Create monitoring graphs panel for dashboard

        Args:
            parent: Parent widget

        Returns:
            MultiGraphPanel instance or None if error
        """
        try:
            graphs_config = [
                {
                    "name": "cpu",
                    "title": "CPU Usage",
                    "color": "#ff0066",
                    "unit": "%",
                    "max_points": 60,
                },
                {
                    "name": "gpu",
                    "title": "GPU Usage",
                    "color": "#00ff88",
                    "unit": "%",
                    "max_points": 60,
                },
            ]

            panel = MultiGraphPanel(parent, graphs_config)
            self.logger.info("Monitoring graphs created")
            return panel

        except Exception as e:
            self.logger.error(f"Failed to create monitoring graphs: {e}")
            return None

    def create_profile_selector(self, parent) -> Optional[ctk.CTkFrame]:
        """
        Create quick profile selector widget

        Args:
            parent: Parent widget

        Returns:
            Frame with profile buttons or None if error
        """
        try:
            frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=8)

            # Title
            title = ctk.CTkLabel(
                frame, text="🎮 Quick Profiles", font=("Arial", 16, "bold")
            )
            title.pack(pady=(15, 10))

            # Button container
            btn_container = ctk.CTkFrame(frame, fg_color="transparent")
            btn_container.pack(fill="x", padx=20, pady=(0, 15))

            # Configure grid
            for i in range(6):
                btn_container.grid_columnconfigure(i, weight=1)

            # Create profile buttons
            profiles_to_show = ["Silent", "Balanced", "Work", "Gaming", "Turbo"]
            for i, profile_name in enumerate(profiles_to_show):
                profile = self.profile_manager.get_profile(profile_name)
                if profile:
                    btn = ctk.CTkButton(
                        btn_container,
                        text=f"{profile.name}\n{profile.tdp_watts}W",
                        command=lambda p=profile: self.profile_manager.apply_profile(
                            p, self
                        ),
                        fg_color="#ff0066",
                        hover_color="#cc0052",
                        height=50,
                    )
                    btn.grid(row=0, column=i, padx=5, sticky="ew")

            self.logger.info("Profile selector created")
            return frame

        except Exception as e:
            self.logger.error(f"Failed to create profile selector: {e}")
            return None

    def load_saved_profile(self):
        """Load and apply the last used profile"""
        try:
            last_profile_name = self.config.get("last_tdp_profile", "Balanced")
            profile = self.profile_manager.get_profile(last_profile_name)

            if profile:
                # Don't apply immediately, just set as current
                # User can apply manually if desired
                if hasattr(self, "current_profile_name"):
                    self.current_profile_name = profile.name

                self.logger.info(f"Last profile loaded: {profile.name}")
                return profile
        except Exception as e:
            self.logger.error(f"Failed to load saved profile: {e}")

        return None

    def restore_auto_profile_switching(self):
        """Restore auto profile switching state from config"""
        try:
            if hasattr(self, "auto_profile_switching"):
                saved_state = self.config.get("auto_profile_switching", False)
                self.auto_profile_switching = saved_state
                self.logger.info(f"Auto profile switching restored: {saved_state}")
        except Exception as e:
            self.logger.error(f"Failed to restore auto profile switching: {e}")


# Utility functions


def create_enhancement_summary_dialog(parent) -> ctk.CTkToplevel:
    """
    Create a dialog showing all available enhancements

    Args:
        parent: Parent window

    Returns:
        Dialog window
    """
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Linux Armoury - Enhancements")
    dialog.geometry("600x700")

    # Scrollable frame
    scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a1a")
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    # Title
    title = ctk.CTkLabel(
        scroll, text="✨ Enhancement Features", font=("Arial", 20, "bold")
    )
    title.pack(pady=(10, 20))

    # Features list
    features = [
        ("⚙️ Settings Persistence", "Your preferences are automatically saved"),
        ("📊 Real-Time Graphs", "Live monitoring with historical data"),
        ("🔔 Toast Notifications", "Visual feedback for all actions"),
        ("⌨️ Keyboard Shortcuts", "Ctrl+1-6 for navigation, Alt+1-4 for profiles"),
        ("🎮 Profile Presets", "One-click system configurations"),
        ("📝 Logging System", "Comprehensive error tracking and debugging"),
        ("🎨 ROG Themed UI", "Gaming-inspired interface design"),
        ("💾 Config Management", "Export/import your settings"),
        ("🔥 Auto Profile Switching", "Smart AC/Battery mode switching"),
        ("⚡ Quick Actions", "Fast access to common operations"),
    ]

    for icon_title, description in features:
        feature_frame = ctk.CTkFrame(scroll, fg_color="#2a2a2a", corner_radius=8)
        feature_frame.pack(fill="x", pady=5, padx=10)

        title_label = ctk.CTkLabel(
            feature_frame, text=icon_title, font=("Arial", 14, "bold"), anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(10, 5))

        desc_label = ctk.CTkLabel(
            feature_frame,
            text=description,
            font=("Arial", 11),
            text_color="#b3b3b3",
            anchor="w",
        )
        desc_label.pack(fill="x", padx=15, pady=(0, 10))

    # Close button
    close_btn = ctk.CTkButton(
        dialog,
        text="Close",
        command=dialog.destroy,
        fg_color="#ff0066",
        hover_color="#cc0052",
    )
    close_btn.pack(pady=10)

    return dialog


def show_keyboard_shortcuts_dialog(parent) -> ctk.CTkToplevel:
    """
    Show available keyboard shortcuts

    Args:
        parent: Parent window

    Returns:
        Dialog window
    """
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Keyboard Shortcuts")
    dialog.geometry("500x600")

    # Scrollable frame
    scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a1a")
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    # Title
    title = ctk.CTkLabel(
        scroll, text="⌨️ Keyboard Shortcuts", font=("Arial", 18, "bold")
    )
    title.pack(pady=(10, 20))

    # Shortcuts
    shortcuts = [
        (
            "Navigation",
            [
                ("Ctrl + 1", "Dashboard"),
                ("Ctrl + 2", "AURA RGB"),
                ("Ctrl + 3", "Performance"),
                ("Ctrl + 4", "Battery"),
                ("Ctrl + 5", "Fans"),
                ("Ctrl + 6", "Settings"),
            ],
        ),
        (
            "Profiles",
            [
                ("Alt + 1", "Silent Profile"),
                ("Alt + 2", "Balanced Profile"),
                ("Alt + 3", "Gaming Profile"),
                ("Alt + 4", "Turbo Profile"),
            ],
        ),
        (
            "Actions",
            [
                ("Ctrl + Q", "Quit Application"),
                ("F5", "Refresh Stats"),
            ],
        ),
    ]

    for category, items in shortcuts:
        # Category header
        category_label = ctk.CTkLabel(
            scroll,
            text=category,
            font=("Arial", 14, "bold"),
            text_color="#ff0066",
            anchor="w",
        )
        category_label.pack(fill="x", padx=15, pady=(15, 5))

        # Shortcuts in category
        for key, action in items:
            shortcut_frame = ctk.CTkFrame(
                scroll, fg_color="#2a2a2a", corner_radius=4, height=30
            )
            shortcut_frame.pack(fill="x", pady=2, padx=20)
            shortcut_frame.pack_propagate(False)

            key_label = ctk.CTkLabel(
                shortcut_frame,
                text=key,
                font=("Courier", 11, "bold"),
                text_color="#00ff88",
            )
            key_label.pack(side="left", padx=10)

            action_label = ctk.CTkLabel(
                shortcut_frame, text=action, font=("Arial", 11), text_color="#ffffff"
            )
            action_label.pack(side="left", padx=10)

    # Close button
    close_btn = ctk.CTkButton(
        dialog,
        text="Close",
        command=dialog.destroy,
        fg_color="#ff0066",
        hover_color="#cc0052",
    )
    close_btn.pack(pady=10)

    return dialog
