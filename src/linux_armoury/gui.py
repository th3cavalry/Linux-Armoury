#!/usr/bin/env python3
"""
Linux Armoury - GUI Control Center for ASUS ROG Laptops
A G-Helper/Armoury Crate inspired control center for Linux
"""

import glob
import logging

# typing.Optional not used in this module
import threading
import time
from pathlib import Path

import customtkinter as ctk

from .config_manager import ConfigManager
from .widgets.toast import ToastNotification


def setup_logging():
    """Configure logging for the application"""
    log_dir = Path.home() / ".config" / "linux-armoury"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "linux-armoury.log"),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger("LinuxArmoury")


# Try to import system modules
try:
    from .modules.asusd_client import AsusdClient, ThrottlePolicy
    from .modules.battery_control import get_battery_controller
    from .modules.fan_control import get_fan_controller
    from .modules.keyboard_control import KeyboardController
    from .modules.system_monitor import SystemMonitor

    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False
    logger = logging.getLogger("LinuxArmoury")
    logger.warning("System modules not available, running in demo mode")


def get_cpu_temperature() -> float:
    """Get CPU temperature from hwmon or thermal zones"""
    try:
        # Try hwmon first (more accurate)
        hwmon_paths = glob.glob("/sys/class/hwmon/hwmon*/temp*_input")
        for path in hwmon_paths:
            # Look for CPU package temp
            name_path = path.replace("_input", "_label")
            try:
                with open(name_path) as f:
                    label = f.read().strip().lower()
                if "package" in label or "core" in label or "cpu" in label:
                    with open(path) as f:
                        # Temperature is in millidegrees
                        return float(f.read().strip()) / 1000
            except Exception:
                pass

        # Fallback to thermal zones
        zones = glob.glob("/sys/class/thermal/thermal_zone*/temp")
        if zones:
            with open(zones[0]) as f:
                return float(f.read().strip()) / 1000
    except Exception:
        pass
    return 0.0


def get_gpu_temperature() -> float:
    """Get GPU temperature (NVIDIA or AMD)"""
    try:
        # Try NVIDIA first
        import subprocess

        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass

    try:
        # Try AMD
        amd_paths = glob.glob("/sys/class/drm/card*/device/hwmon/hwmon*/temp1_input")
        if amd_paths:
            with open(amd_paths[0]) as f:
                return float(f.read().strip()) / 1000
    except Exception:
        pass

    return 0.0


# Color scheme inspired by G-Helper
COLOR_BG_DARK = "#0d0d0d"
COLOR_BG_MAIN = "#1a1a1a"
COLOR_BG_CARD = "#242424"
COLOR_BG_HOVER = "#2d2d2d"
COLOR_ACCENT = "#ff0066"  # ROG pink accent
COLOR_ACCENT_HOVER = "#cc0052"
COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY = "#b3b3b3"
COLOR_SUCCESS = "#00ff88"
COLOR_WARNING = "#ffaa00"
CORNER_RADIUS = 8

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PerformanceCard(ctk.CTkFrame):
    """Performance mode selector card with TDP profiles"""

    def __init__(self, master, asusd_client=None, **kwargs):
        super().__init__(
            master, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS, **kwargs
        )

        self.asusd_client = asusd_client
        self.keyboard_controller = None
        self.oc_controller = None
        if HAS_MODULES:
            try:
                self.keyboard_controller = KeyboardController()
            except Exception:
                pass
            try:
                from .modules.overclocking_control import OverclockingController

                self.oc_controller = OverclockingController()
            except Exception:
                pass

        # Title
        title = ctk.CTkLabel(
            self,
            text="⚡ Power Profile",
            font=("Segoe UI", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(15, 10), padx=20, anchor="w")

        # Define 7 TDP profiles with icons
        self.profiles = [
            ("🛟 Emergency", "10W", 10, 10, 10),  # Emergency - 10W (minimal power)
            ("🔋 Battery Saver", "18W", 18, 20, 18),  # Battery - 18W (maximize runtime)
            ("🌱 Efficient", "30W", 30, 35, 30),  # Efficient - 30W (light work)
            ("⚖️ Balanced", "40W", 40, 45, 40),  # Balanced - 40W (default)
            ("⚡ Performance", "55W", 55, 60, 55),  # Performance - 55W (demanding work)
            ("🎮 Gaming", "70W", 70, 75, 70),  # Gaming - 70W (high performance)
            ("🚀 Maximum", "90W", 90, 95, 90),  # Maximum - 90W (absolute max)
        ]

        self.mode_buttons = []

        for name, tdp_display, stapm, fast, slow in self.profiles:
            btn = ctk.CTkButton(
                self,
                text=f"{name} ({tdp_display})",
                fg_color=COLOR_BG_HOVER,
                hover_color=COLOR_ACCENT,
                corner_radius=6,
                height=35,
                font=("Segoe UI", 11),
                command=lambda n=name, s=stapm, f=fast, sl=slow: self.set_profile(
                    n, s, f, sl
                ),
            )
            btn.pack(pady=3, padx=20, fill="x")
            self.mode_buttons.append(btn)

        # Status label
        self.status_label = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 9), text_color=COLOR_TEXT_SECONDARY
        )
        self.status_label.pack(pady=(5, 10), padx=20)

        # Get current mode from asusctl if available
        self.current_profile = "Balanced"
        if self.asusd_client:
            try:
                policy = self.asusd_client.get_throttle_policy()
                if policy == ThrottlePolicy.QUIET:
                    self.current_profile = "Battery Saver"
                elif policy == ThrottlePolicy.PERFORMANCE:
                    self.current_profile = "Gaming"
                else:
                    self.current_profile = "Balanced"
            except Exception:
                pass

        self.update_selection()

    def set_profile(self, name: str, stapm: int, fast: int, slow: int):
        """Set TDP profile using RyzenAdj and asusd"""
        self.current_profile = name
        self.update_selection()

        # Set TDP via RyzenAdj if available
        if self.oc_controller and self.oc_controller.ryzenadj_available:
            try:
                success = self.oc_controller.set_ryzenadj_tdp(
                    stapm_limit=stapm, fast_limit=fast, slow_limit=slow
                )
                if success:
                    self.status_label.configure(
                        text=f"✓ TDP set to {stapm}W (requires RyzenAdj)",
                        text_color=COLOR_SUCCESS,
                    )
                else:
                    self.status_label.configure(
                        text="✗ Failed to set TDP (check permissions)",
                        text_color=COLOR_WARNING,
                    )
            except Exception as e:
                self.status_label.configure(
                    text=f"✗ Error: {str(e)}", text_color=COLOR_WARNING
                )
        else:
            self.status_label.configure(
                text="RyzenAdj not available (AMD CPU required)",
                text_color=COLOR_TEXT_SECONDARY,
            )

        # Also set asusd throttle policy for appropriate profiles
        if self.asusd_client:
            try:
                logger = logging.getLogger("LinuxArmoury")
                if name in ["Emergency", "Battery Saver", "Efficient"]:
                    self.asusd_client.set_throttle_policy(ThrottlePolicy.QUIET)
                    logger.info(f"Set throttle policy to QUIET for {name}")
                elif name in ["Gaming", "Maximum"]:
                    self.asusd_client.set_throttle_policy(ThrottlePolicy.PERFORMANCE)
                    logger.info(f"Set throttle policy to PERFORMANCE for {name}")
                else:
                    self.asusd_client.set_throttle_policy(ThrottlePolicy.BALANCED)
                    logger.info(f"Set throttle policy to BALANCED for {name}")
            except Exception as e:
                logger = logging.getLogger("LinuxArmoury")
                logger.error(f"Failed to set throttle policy: {e}")

    def update_selection(self):
        """Update button appearance based on current profile"""
        for btn, (name, _, _, _, _) in zip(self.mode_buttons, self.profiles):
            profile_name = name.split(" ", 1)[-1]  # Remove emoji
            if profile_name in self.current_profile:
                btn.configure(fg_color=COLOR_ACCENT)
            else:
                btn.configure(fg_color=COLOR_BG_HOVER)


class SystemMonitorCard(ctk.CTkFrame):
    """Real-time system monitoring card with enhanced metrics"""

    def __init__(self, master, **kwargs):
        super().__init__(
            master, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS, **kwargs
        )

        # Title
        title = ctk.CTkLabel(
            self,
            text="📊 System Monitor",
            font=("Segoe UI", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(15, 10), padx=20, anchor="w")

        # CPU Monitor
        self.cpu_label = ctk.CTkLabel(
            self,
            text="CPU: -- %",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.cpu_label.pack(pady=3, padx=20, anchor="w")

        self.cpu_bar = ctk.CTkProgressBar(
            self, width=260, fg_color=COLOR_BG_HOVER, progress_color=COLOR_ACCENT
        )
        self.cpu_bar.pack(pady=3, padx=20)
        self.cpu_bar.set(0)

        self.cpu_temp = ctk.CTkLabel(
            self,
            text="Temp: -- °C",
            font=("Segoe UI", 9),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.cpu_temp.pack(pady=(0, 8), padx=20, anchor="w")

        # GPU Monitor
        self.gpu_label = ctk.CTkLabel(
            self,
            text="GPU: -- %",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.gpu_label.pack(pady=3, padx=20, anchor="w")

        self.gpu_bar = ctk.CTkProgressBar(
            self, width=260, fg_color=COLOR_BG_HOVER, progress_color=COLOR_SUCCESS
        )
        self.gpu_bar.pack(pady=3, padx=20)
        self.gpu_bar.set(0)

        self.gpu_temp = ctk.CTkLabel(
            self,
            text="Temp: -- °C",
            font=("Segoe UI", 9),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.gpu_temp.pack(pady=(0, 8), padx=20, anchor="w")

        # RAM Monitor
        self.ram_label = ctk.CTkLabel(
            self,
            text="RAM: -- %",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.ram_label.pack(pady=3, padx=20, anchor="w")

        self.ram_bar = ctk.CTkProgressBar(
            self, width=260, fg_color=COLOR_BG_HOVER, progress_color="#00aaff"
        )
        self.ram_bar.pack(pady=3, padx=20)
        self.ram_bar.set(0)

        self.ram_details = ctk.CTkLabel(
            self,
            text="-- / -- GB",
            font=("Segoe UI", 9),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.ram_details.pack(pady=(0, 8), padx=20, anchor="w")

        # Disk Monitor
        self.disk_label = ctk.CTkLabel(
            self,
            text="Disk: -- %",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.disk_label.pack(pady=3, padx=20, anchor="w")

        self.disk_bar = ctk.CTkProgressBar(
            self, width=260, fg_color=COLOR_BG_HOVER, progress_color="#ffaa00"
        )
        self.disk_bar.pack(pady=3, padx=20)
        self.disk_bar.set(0)

        self.disk_details = ctk.CTkLabel(
            self,
            text="-- / -- GB",
            font=("Segoe UI", 9),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.disk_details.pack(pady=(0, 10), padx=20, anchor="w")

    def update_stats(
        self,
        cpu_usage: float,
        cpu_temp: float,
        gpu_usage: float,
        gpu_temp: float,
        ram_usage: float = 0,
        ram_used_gb: float = 0,
        ram_total_gb: float = 0,
        disk_usage: float = 0,
        disk_used_gb: float = 0,
        disk_total_gb: float = 0,
    ):
        # CPU
        self.cpu_label.configure(text=f"CPU: {cpu_usage:.0f} %")
        self.cpu_bar.set(cpu_usage / 100)
        self.cpu_temp.configure(text=f"Temp: {cpu_temp:.0f} °C")

        # GPU
        self.gpu_label.configure(text=f"GPU: {gpu_usage:.0f} %")
        self.gpu_bar.set(gpu_usage / 100)
        self.gpu_temp.configure(text=f"Temp: {gpu_temp:.0f} °C")

        # RAM
        self.ram_label.configure(text=f"RAM: {ram_usage:.0f} %")
        self.ram_bar.set(ram_usage / 100)
        self.ram_details.configure(text=f"{ram_used_gb:.1f} / {ram_total_gb:.1f} GB")

        # Disk
        self.disk_label.configure(text=f"Disk: {disk_usage:.0f} %")
        self.disk_bar.set(disk_usage / 100)
        self.disk_details.configure(text=f"{disk_used_gb:.0f} / {disk_total_gb:.0f} GB")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Linux Armoury")
        self.geometry("1000x650")
        self.configure(fg_color=COLOR_BG_MAIN)

        # Initialize logging
        self.logger = setup_logging()
        self.logger.info("Linux Armoury started")

        # Initialize config manager
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.load_settings()
        self.logger.info(f"Settings loaded: {self.settings}")

        # Provide config property for profile manager compatibility
        self.config = self.config_manager

        # Apply window size from settings if available
        if self.settings.get("window_size"):
            width, height = self.settings["window_size"]
            self.geometry(f"{width}x{height}")
            self.logger.info(f"Window size restored: {width}x{height}")

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize system monitor
        if HAS_MODULES:
            try:
                self.system_monitor = SystemMonitor()
                self.logger.info("System monitor initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize system monitor: {e}")
                self.system_monitor = None
        else:
            self.system_monitor = None

        # Initialize asusd client
        if HAS_MODULES:
            try:
                self.asusd_client = AsusdClient()
                if self.asusd_client.is_available():
                    self.logger.info("Asusd client connected successfully")
                else:
                    self.logger.info("Asusd daemon not available")
                    self.asusd_client = None
            except Exception as e:
                self.logger.error(f"Failed to initialize asusd client: {e}")
                self.asusd_client = None
        else:
            self.asusd_client = None

        # Initialize auto profile switching
        self.auto_profile_switching = False
        self.last_ac_status = None  # Track AC adapter state

        # Initialize controllers for profile management
        self.gpu_controller = None
        self.fan_controller = None
        self.keyboard_controller = None
        self.battery_controller = None

        if HAS_MODULES:
            try:
                from .modules.gpu_control import GpuController

                self.gpu_controller = GpuController()
            except Exception:
                pass

            try:
                self.fan_controller = get_fan_controller()
            except Exception:
                pass

            try:
                self.keyboard_controller = KeyboardController()
            except Exception:
                pass

            try:
                self.battery_controller = get_battery_controller()
            except Exception:
                pass

        # Sidebar
        self.create_sidebar()

        # Main content
        self.create_main_content()

        # Initialize with Dashboard
        self.show_dashboard()

        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.monitor_thread.start()

        # Setup keyboard shortcuts
        self.setup_keybindings()

    def setup_keybindings(self):
        """Setup keyboard shortcuts for the application"""
        # Navigation shortcuts (Ctrl+number)
        self.bind("<Control-1>", lambda e: self.show_dashboard())
        self.bind("<Control-2>", lambda e: self.show_aura())
        self.bind("<Control-3>", lambda e: self.show_performance())
        self.bind("<Control-4>", lambda e: self.show_battery())
        self.bind("<Control-5>", lambda e: self.show_fans())
        self.bind("<Control-6>", lambda e: self.show_settings())

        # Quick actions
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<F5>", lambda e: self.logger.info("Refresh triggered"))

        self.logger.info("Keyboard shortcuts initialized")

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=200, corner_radius=0, fg_color=COLOR_BG_DARK
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        logo = ctk.CTkLabel(
            self.sidebar,
            text="⚔️ ROG",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_ACCENT,
        )
        logo.pack(pady=(30, 20))

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="LINUX ARMOURY",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        )
        subtitle.pack(pady=(0, 30))

        # Navigation buttons
        nav_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🎨 Aura RGB", self.show_aura),
            ("⚡ Performance", self.show_performance),
            ("🌡️ Fans", self.show_fans),
            ("🔋 Battery", self.show_battery),
            ("⚙️ Settings", self.show_settings),
        ]

        self.nav_buttons = []
        for text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                text_color=COLOR_TEXT_SECONDARY,
                hover_color=COLOR_BG_HOVER,
                anchor="w",
                height=40,
                font=("Segoe UI", 12),
            )
            btn.pack(pady=2, padx=15, fill="x")
            self.nav_buttons.append(btn)

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG_MAIN)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_toast(
        self, message: str, notification_type: str = "info", duration: int = 3000
    ):
        """Display a toast notification"""
        try:
            ToastNotification(self, message, notification_type, duration)
            self.logger.info(f"Toast shown: [{notification_type}] {message}")
        except Exception as e:
            self.logger.error(f"Failed to show toast: {e}")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_frame()

        # Page title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(0, 20), anchor="w")

        # Cards container
        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True)

        # Left column
        left_col = ctk.CTkFrame(cards_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Performance card with asusd client integration
        self.perf_card = PerformanceCard(left_col, asusd_client=self.asusd_client)
        self.perf_card.pack(fill="x", pady=(0, 10))

        # Quick actions card
        quick_card = ctk.CTkFrame(
            left_col, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        quick_card.pack(fill="x")

        ctk.CTkLabel(
            quick_card,
            text="⚡ Quick Actions",
            font=("Segoe UI", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 10), padx=20, anchor="w")

        # Quick action functions
        def toggle_gpu_mode():
            """Cycle through GPU modes"""
            if HAS_MODULES:
                try:
                    from .modules.gpu_control import GpuController, GpuMode

                    gpu_ctrl = GpuController()
                    if gpu_ctrl.supergfxctl_available:
                        status = gpu_ctrl.get_switching_status()
                        if status.current_mode == GpuMode.INTEGRATED:
                            gpu_ctrl.set_gpu_mode(GpuMode.HYBRID)
                            print("Switched to Hybrid GPU mode")
                        elif status.current_mode == GpuMode.HYBRID:
                            gpu_ctrl.set_gpu_mode(GpuMode.ASUS_MUX_DGPU)
                            print("Switched to dGPU mode")
                        else:
                            gpu_ctrl.set_gpu_mode(GpuMode.INTEGRATED)
                            print("Switched to iGPU mode")
                    else:
                        logger = logging.getLogger("LinuxArmoury")
                        logger.info("GPU switching not available")
                except Exception as e:
                    logger = logging.getLogger("LinuxArmoury")
                    logger.error(f"GPU toggle error: {e}")

        def cycle_keyboard_brightness():
            """Cycle keyboard brightness"""
            if HAS_MODULES:
                try:
                    logger = logging.getLogger("LinuxArmoury")
                    kbd = KeyboardController()
                    if kbd.is_supported():
                        success, msg = kbd.cycle_brightness()
                        logger.info(f"Keyboard brightness: {msg}")
                    else:
                        logger.info("Keyboard backlight not supported")
                except Exception as e:
                    logger = logging.getLogger("LinuxArmoury")
                    logger.error(f"Keyboard brightness error: {e}")

        def open_system_monitor():
            """Open system monitor application"""
            try:
                logger = logging.getLogger("LinuxArmoury")
                import subprocess

                # Try common system monitors
                monitors = ["gnome-system-monitor", "plasma-systemmonitor", "htop"]
                for monitor in monitors:
                    try:
                        subprocess.Popen([monitor])
                        logger.info(f"Opened {monitor}")
                        break
                    except FileNotFoundError:
                        continue
            except Exception as e:
                logger = logging.getLogger("LinuxArmoury")
                logger.error(f"System monitor error: {e}")

        # Quick action buttons with actual functionality
        ctk.CTkButton(
            quick_card,
            text="🔄 Toggle GPU Mode",
            fg_color=COLOR_BG_HOVER,
            hover_color=COLOR_ACCENT,
            corner_radius=6,
            height=35,
            command=toggle_gpu_mode,
        ).pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(
            quick_card,
            text="💡 Keyboard Brightness",
            fg_color=COLOR_BG_HOVER,
            hover_color=COLOR_ACCENT,
            corner_radius=6,
            height=35,
            command=cycle_keyboard_brightness,
        ).pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(
            quick_card,
            text="📊 System Monitor",
            fg_color=COLOR_BG_HOVER,
            hover_color=COLOR_ACCENT,
            corner_radius=6,
            height=35,
            command=open_system_monitor,
        ).pack(pady=(5, 15), padx=20, fill="x")

        # Right column - System Monitor
        self.monitor_card = SystemMonitorCard(cards_frame)
        self.monitor_card.pack(side="right", fill="both", expand=True)

    def show_aura(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="🎨 Aura RGB Lighting",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(0, 20), anchor="w")

        # Initialize keyboard controller if available
        kbd = None
        if HAS_MODULES:
            try:
                kbd = KeyboardController()
            except Exception:
                pass

        # Brightness Control
        brightness_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        brightness_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            brightness_frame,
            text="⚡ Brightness",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        # Current brightness label
        current_brightness = 0
        if kbd and kbd.is_supported():
            current_brightness = kbd.get_brightness() or 0

        brightness_label = ctk.CTkLabel(
            brightness_frame,
            text=f"Level: {current_brightness}",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY,
        )
        brightness_label.pack(pady=(0, 5), padx=20, anchor="w")

        # Brightness slider
        def on_brightness_change(value):
            if kbd and kbd.is_supported():
                level = int(value)
                success, msg = kbd.set_brightness(level)
                brightness_label.configure(text=f"Level: {level} - {msg}")
            else:
                brightness_label.configure(text=f"Level: {int(value)} - Not supported")

        max_brightness = kbd.get_max_brightness() if kbd else 3
        brightness_slider = ctk.CTkSlider(
            brightness_frame,
            from_=0,
            to=max_brightness,
            command=on_brightness_change,
            fg_color=COLOR_BG_HOVER,
            button_color=COLOR_ACCENT,
            button_hover_color=COLOR_ACCENT_HOVER,
        )
        brightness_slider.pack(pady=10, padx=20, fill="x")
        brightness_slider.set(current_brightness)

        ctk.CTkLabel(brightness_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # RGB Color Control
        if kbd and kbd.has_rgb():
            color_frame = ctk.CTkFrame(
                self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
            )
            color_frame.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(
                color_frame,
                text="🎨 RGB Color",
                font=("Segoe UI", 14, "bold"),
                text_color=COLOR_TEXT_PRIMARY,
            ).pack(pady=(15, 5), padx=20, anchor="w")

            # Current color display
            current_rgb = kbd.get_rgb_color()
            color_hex = current_rgb.to_hex() if current_rgb else "#FFFFFF"

            color_status = ctk.CTkLabel(
                color_frame,
                text=f"Current: {color_hex}",
                font=("Segoe UI", 11),
                text_color=COLOR_TEXT_SECONDARY,
            )
            color_status.pack(pady=(0, 10), padx=20, anchor="w")

            # Preset colors grid
            preset_colors = {
                "Red": "#ff0000",
                "Green": "#00ff00",
                "Blue": "#0000ff",
                "Yellow": "#ffff00",
                "Cyan": "#00ffff",
                "Magenta": "#ff00ff",
                "White": "#ffffff",
                "Orange": "#ffa500",
                "Purple": "#800080",
                "Pink": "#ffc0cb",
                "ROG Pink": "#ff0066",
            }

            def set_preset_color(color_name, hex_color):
                if kbd:
                    from .modules.keyboard_control import RGB

                    rgb = RGB.from_hex(hex_color)
                    success, msg = kbd.set_rgb_color(rgb)
                    color_status.configure(text=f"Current: {hex_color} - {msg}")

            # Create 3 columns for colors
            colors_grid = ctk.CTkFrame(color_frame, fg_color="transparent")
            colors_grid.pack(pady=10, padx=20, fill="x")

            row = 0
            col = 0
            for name, hex_val in preset_colors.items():
                btn = ctk.CTkButton(
                    colors_grid,
                    text=name,
                    fg_color=hex_val if hex_val != "#ffffff" else COLOR_BG_HOVER,
                    hover_color=COLOR_ACCENT,
                    text_color=(
                        "#000000"
                        if hex_val
                        in ["#ffff00", "#00ffff", "#ffffff", "#ffa500", "#ffc0cb"]
                        else "#ffffff"
                    ),
                    corner_radius=6,
                    height=35,
                    command=lambda n=name, h=hex_val: set_preset_color(n, h),
                )
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            # Configure grid columns to expand
            colors_grid.grid_columnconfigure(0, weight=1)
            colors_grid.grid_columnconfigure(1, weight=1)
            colors_grid.grid_columnconfigure(2, weight=1)

            ctk.CTkLabel(color_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # Effects with asusctl integration
        effects_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        effects_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            effects_frame,
            text="✨ Keyboard Effects",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        # Status label for effects
        effects_status = ctk.CTkLabel(
            effects_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        )
        effects_status.pack(pady=(0, 10), padx=20, anchor="w")

        # Import AuraEffect for the effects
        try:
            from .modules.keyboard_control import AuraEffect

            aura_effects_available = True
        except ImportError:
            aura_effects_available = False

        def set_keyboard_effect(effect_name: str):
            """Set keyboard effect using asusctl"""
            if not kbd or not aura_effects_available:
                effects_status.configure(
                    text="Keyboard effects not available", text_color=COLOR_WARNING
                )
                return

            try:
                # Map display names to enum values
                effect_map = {
                    "Static": AuraEffect.STATIC,
                    "Breathe": AuraEffect.BREATHE,
                    "Color Cycle": AuraEffect.COLOR_CYCLE,
                    "Rainbow": AuraEffect.RAINBOW,
                    "Star": AuraEffect.STAR,
                    "Rain": AuraEffect.RAIN,
                    "Highlight": AuraEffect.HIGHLIGHT,
                    "Laser": AuraEffect.LASER,
                    "Ripple": AuraEffect.RIPPLE,
                    "Strobe": AuraEffect.STROBE,
                    "Comet": AuraEffect.COMET,
                    "Flash": AuraEffect.FLASH,
                    "Multi Static": AuraEffect.MULTI_STATIC,
                }

                if effect_name not in effect_map:
                    effects_status.configure(
                        text=f"Unknown effect: {effect_name}", text_color=COLOR_WARNING
                    )
                    return

                effect = effect_map[effect_name]
                success, msg = kbd.set_effect(effect)
                if success:
                    effects_status.configure(text=f"✓ {msg}", text_color=COLOR_SUCCESS)
                else:
                    effects_status.configure(text=f"✗ {msg}", text_color=COLOR_WARNING)
            except Exception as e:
                effects_status.configure(
                    text=f"Error: {str(e)}", text_color=COLOR_WARNING
                )

        # All 13 effects from AuraEffect enum
        effect_names = [
            "Static",
            "Breathe",
            "Color Cycle",
            "Rainbow",
            "Star",
            "Rain",
            "Highlight",
            "Laser",
            "Ripple",
            "Strobe",
            "Comet",
            "Flash",
            "Multi Static",
        ]

        # Create 2 columns for effects
        effects_grid = ctk.CTkFrame(effects_frame, fg_color="transparent")
        effects_grid.pack(pady=10, padx=20, fill="x")

        row = 0
        col = 0
        for effect in effect_names:
            btn = ctk.CTkButton(
                effects_grid,
                text=effect,
                fg_color=COLOR_BG_HOVER,
                hover_color=COLOR_ACCENT,
                corner_radius=6,
                height=35,
                command=lambda e=effect: set_keyboard_effect(e),
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

            col += 1
            if col >= 2:
                col = 0
                row += 1

        # Configure grid columns
        effects_grid.grid_columnconfigure(0, weight=1)
        effects_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(effects_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

    def show_performance(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="⚡ Performance Tuning",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(0, 20), anchor="w")

        # Initialize GPU controller
        gpu_ctrl = None
        if HAS_MODULES:
            try:
                from .modules.gpu_control import GpuController

                gpu_ctrl = GpuController()
            except Exception:
                pass

        # GPU Mode Switching
        gpu_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        gpu_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            gpu_frame,
            text="🎮 GPU Mode",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        # Get current GPU status
        current_mode = None
        gpu_status_text = "Not available"
        if gpu_ctrl and gpu_ctrl.supergfxctl_available:
            try:
                status = gpu_ctrl.get_switching_status()
                if status.available:
                    current_mode = status.current_mode
                    gpu_status_text = (
                        f"Current: {current_mode.value if current_mode else 'Unknown'}"
                    )
                    if status.dgpu_vendor != "Unknown":
                        gpu_status_text += f" | dGPU: {status.dgpu_vendor}"
                    if status.pending_mode:
                        gpu_status_text += f" | Pending: {status.pending_mode.value}"
            except Exception:
                gpu_status_text = "Error reading status"

        status_label = ctk.CTkLabel(
            gpu_frame,
            text=gpu_status_text,
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        )
        status_label.pack(pady=(0, 10), padx=20, anchor="w")

        # GPU mode buttons
        def set_gpu_mode(mode_enum):
            if gpu_ctrl and gpu_ctrl.supergfxctl_available:
                success, msg = gpu_ctrl.set_gpu_mode(mode_enum)
                status_label.configure(text=msg)
            else:
                status_label.configure(text="supergfxctl not available")

        # Define GPU modes
        gpu_modes = [
            ("🌿 Eco Mode (iGPU Only)", "Integrated", "GpuMode.INTEGRATED"),
            ("⚡ Standard (Hybrid)", "Hybrid", "GpuMode.HYBRID"),
            ("🚀 Ultimate (dGPU)", "AsusMuxDgpu", "GpuMode.ASUS_MUX_DGPU"),
            ("🎯 Optimized", "Vfio", "GpuMode.VFIO"),
        ]

        for display_name, mode_name, mode_enum_str in gpu_modes:
            # Extract enum value
            try:
                if HAS_MODULES and gpu_ctrl:
                    # GpuMode is already imported earlier; avoid re-import/redefinition
                    mode_enum = eval(mode_enum_str)

                    # Highlight current mode
                    is_current = current_mode and current_mode == mode_enum
                    fg = COLOR_ACCENT if is_current else COLOR_BG_HOVER

                    btn = ctk.CTkButton(
                        gpu_frame,
                        text=display_name,
                        fg_color=fg,
                        hover_color=COLOR_ACCENT,
                        corner_radius=6,
                        height=40,
                        command=lambda m=mode_enum: set_gpu_mode(m),
                    )
                    btn.pack(pady=5, padx=20, fill="x")
                else:
                    # Demo mode - disabled buttons
                    btn = ctk.CTkButton(
                        gpu_frame,
                        text=display_name,
                        fg_color=COLOR_BG_HOVER,
                        hover_color=COLOR_ACCENT,
                        corner_radius=6,
                        height=40,
                        state="disabled",
                    )
                    btn.pack(pady=5, padx=20, fill="x")
            except Exception:
                # Fallback for missing enums
                btn = ctk.CTkButton(
                    gpu_frame,
                    text=display_name,
                    fg_color=COLOR_BG_HOVER,
                    hover_color=COLOR_ACCENT,
                    corner_radius=6,
                    height=40,
                    state="disabled",
                )
                btn.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(gpu_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # GPU Live Stats
        stats_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        stats_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            stats_frame,
            text="📊 GPU Statistics",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 10), padx=20, anchor="w")

        if gpu_ctrl:
            try:
                stats = gpu_ctrl.get_live_stats()

                # GPU info grid
                info_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
                info_grid.pack(pady=10, padx=20, fill="x")

                stats_items = [
                    ("GPU:", stats.gpu_name or "Unknown"),
                    ("Usage:", f"{stats.gpu_usage_percent}%"),
                    ("Temperature:", f"{stats.gpu_temp_c}°C"),
                    ("Clock:", f"{stats.gpu_clock_mhz} MHz"),
                    (
                        "VRAM Used:",
                        f"{stats.vram_used_mb} MB / {stats.vram_total_mb} MB",
                    ),
                    (
                        "Power:",
                        f"{stats.power_draw_w:.1f}W / {stats.power_limit_w:.1f}W",
                    ),
                ]

                row = 0
                for label_text, value_text in stats_items:
                    label = ctk.CTkLabel(
                        info_grid,
                        text=label_text,
                        font=("Segoe UI", 10, "bold"),
                        text_color=COLOR_TEXT_SECONDARY,
                        anchor="w",
                    )
                    label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)

                    value = ctk.CTkLabel(
                        info_grid,
                        text=value_text,
                        font=("Segoe UI", 10),
                        text_color=COLOR_TEXT_PRIMARY,
                        anchor="w",
                    )
                    value.grid(row=row, column=1, sticky="w", pady=2)
                    row += 1

                info_grid.grid_columnconfigure(1, weight=1)
            except Exception:
                ctk.CTkLabel(
                    stats_frame,
                    text="GPU statistics unavailable",
                    font=("Segoe UI", 10),
                    text_color=COLOR_TEXT_SECONDARY,
                ).pack(pady=10, padx=20, anchor="w")
        else:
            ctk.CTkLabel(
                stats_frame,
                text="GPU control modules not available (demo mode)",
                font=("Segoe UI", 10),
                text_color=COLOR_TEXT_SECONDARY,
            ).pack(pady=10, padx=20, anchor="w")

        ctk.CTkLabel(stats_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

    def show_fans(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="🌡️ Fan Control",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(0, 20), anchor="w")

        # Initialize fan controller
        fan_ctrl = None
        if HAS_MODULES:
            try:
                fan_ctrl = get_fan_controller()
            except Exception:
                pass

        # Fan Status Card
        status_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        status_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            status_frame,
            text="💨 Fan Status",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 10), padx=20, anchor="w")

        if fan_ctrl and fan_ctrl.is_supported():
            # Get current fan speeds
            fan_speeds = fan_ctrl.get_all_fan_speeds()

            if fan_speeds:
                # Fan status grid
                fan_grid = ctk.CTkFrame(status_frame, fg_color="transparent")
                fan_grid.pack(pady=10, padx=20, fill="x")

                for idx, fan_status in enumerate(fan_speeds):
                    # Fan label
                    label = ctk.CTkLabel(
                        fan_grid,
                        text=f"{fan_status.name}:",
                        font=("Segoe UI", 11, "bold"),
                        text_color=COLOR_TEXT_SECONDARY,
                        anchor="w",
                    )
                    label.grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=5)

                    # RPM value
                    value = ctk.CTkLabel(
                        fan_grid,
                        text=f"{fan_status.rpm} RPM",
                        font=("Segoe UI", 11),
                        text_color=COLOR_TEXT_PRIMARY,
                        anchor="w",
                    )
                    value.grid(row=idx, column=1, sticky="w", pady=5)

                fan_grid.grid_columnconfigure(1, weight=1)
            else:
                ctk.CTkLabel(
                    status_frame,
                    text="No fan sensors detected",
                    font=("Segoe UI", 10),
                    text_color=COLOR_TEXT_SECONDARY,
                ).pack(pady=10, padx=20, anchor="w")
        else:
            ctk.CTkLabel(
                status_frame,
                text="Fan control not supported",
                font=("Segoe UI", 10),
                text_color=COLOR_TEXT_SECONDARY,
            ).pack(pady=10, padx=20, anchor="w")

        ctk.CTkLabel(status_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # Temperature Status Card
        temp_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        temp_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            temp_frame,
            text="🌡️ Temperatures",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 10), padx=20, anchor="w")

        if fan_ctrl:
            temps = fan_ctrl.get_temperatures()

            temp_grid = ctk.CTkFrame(temp_frame, fg_color="transparent")
            temp_grid.pack(pady=10, padx=20, fill="x")

            row = 0
            for name, temp in temps.items():
                if temp is not None:
                    label = ctk.CTkLabel(
                        temp_grid,
                        text=f"{name.upper()}:",
                        font=("Segoe UI", 11, "bold"),
                        text_color=COLOR_TEXT_SECONDARY,
                        anchor="w",
                    )
                    label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)

                    # Color code temperature
                    temp_color = COLOR_TEXT_PRIMARY
                    if temp > 80:
                        temp_color = COLOR_WARNING
                    elif temp > 90:
                        temp_color = "#ff0000"

                    value = ctk.CTkLabel(
                        temp_grid,
                        text=f"{temp:.1f}°C",
                        font=("Segoe UI", 11),
                        text_color=temp_color,
                        anchor="w",
                    )
                    value.grid(row=row, column=1, sticky="w", pady=5)
                    row += 1

            temp_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(temp_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # Fan Profile Presets
        profile_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        profile_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            profile_frame,
            text="🎚️ Fan Profiles",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        ctk.CTkLabel(
            profile_frame,
            text="Preset fan curves for different scenarios",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(pady=(0, 10), padx=20, anchor="w")

        # Profile buttons
        profiles = [
            ("🤫 Quiet", "Minimal fan noise, lower cooling"),
            ("⚖️ Balanced", "Balanced noise and cooling"),
            ("🚀 Performance", "Maximum cooling, higher noise"),
            ("💯 Full Speed", "Fans at 100% (emergency)"),
        ]

        status_label = ctk.CTkLabel(
            profile_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        )
        status_label.pack(pady=(0, 10), padx=20)

        def set_profile(profile_name):
            if fan_ctrl and fan_ctrl.has_fan_curves():
                # Enable custom curves
                success, msg = fan_ctrl.enable_custom_fan_curve(True)
                status_label.configure(
                    text=f"{profile_name}: {msg}",
                    text_color=COLOR_SUCCESS if success else COLOR_WARNING,
                )
            else:
                status_label.configure(
                    text="Custom fan curves not supported by hardware",
                    text_color=COLOR_TEXT_SECONDARY,
                )

        for profile_name, description in profiles:
            btn_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
            btn_frame.pack(pady=5, padx=20, fill="x")

            btn = ctk.CTkButton(
                btn_frame,
                text=profile_name,
                fg_color=COLOR_BG_HOVER,
                hover_color=COLOR_ACCENT,
                corner_radius=6,
                height=40,
                width=150,
                command=lambda p=profile_name: set_profile(p),
            )
            btn.pack(side="left", padx=(0, 10))

            desc = ctk.CTkLabel(
                btn_frame,
                text=description,
                font=("Segoe UI", 9),
                text_color=COLOR_TEXT_SECONDARY,
                anchor="w",
            )
            desc.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(profile_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # Custom Fan Curve (Advanced)
        curve_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        curve_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            curve_frame,
            text="📈 Custom Fan Curve",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        ctk.CTkLabel(
            curve_frame,
            text="Advanced fan curve editing requires asusctl integration",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(pady=(0, 10), padx=20, anchor="w")

        ctk.CTkButton(
            curve_frame,
            text="Open Fan Curve Editor (Coming Soon)",
            fg_color=COLOR_BG_HOVER,
            hover_color=COLOR_ACCENT,
            corner_radius=6,
            height=40,
            state="disabled",
        ).pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(curve_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

    def show_battery(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="🔋 Battery Settings",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(0, 20), anchor="w")

        # Initialize battery controller
        battery_ctrl = None
        if HAS_MODULES:
            try:
                battery_ctrl = get_battery_controller()
            except Exception:
                pass

        # Battery Info Card
        info_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        info_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text="⚡ Battery Status",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 10), padx=20, anchor="w")

        if battery_ctrl:
            info = battery_ctrl.get_battery_info()

            # Info grid
            info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
            info_grid.pack(pady=10, padx=20, fill="x")

            info_items = [
                ("Current Charge:", f"{info.get('capacity', 'N/A')}%"),
                ("Status:", info.get("status", "Unknown")),
                (
                    "Health:",
                    (
                        f"{info.get('health', 'N/A')}%"
                        if isinstance(info.get("health"), (int, float))
                        else "N/A"
                    ),
                ),
            ]

            row = 0
            for label_text, value_text in info_items:
                label = ctk.CTkLabel(
                    info_grid,
                    text=label_text,
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLOR_TEXT_SECONDARY,
                    anchor="w",
                )
                label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)

                value = ctk.CTkLabel(
                    info_grid,
                    text=value_text,
                    font=("Segoe UI", 11),
                    text_color=COLOR_TEXT_PRIMARY,
                    anchor="w",
                )
                value.grid(row=row, column=1, sticky="w", pady=5)
                row += 1

            info_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

        # Charge Limit Control
        limit_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        limit_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            limit_frame,
            text="🎯 Charge Limit",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        ctk.CTkLabel(
            limit_frame,
            text="Set maximum charge level to preserve battery health",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(pady=(0, 10), padx=20, anchor="w")

        # Get current charge limit
        current_limit = 80  # Default
        if battery_ctrl and battery_ctrl.is_supported():
            limit = battery_ctrl.get_charge_limit()
            if limit:
                current_limit = limit

        # Status label
        status_label = ctk.CTkLabel(
            limit_frame,
            text=f"Current limit: {current_limit}%",
            font=("Segoe UI", 11),
            text_color=(
                COLOR_SUCCESS
                if battery_ctrl and battery_ctrl.is_supported()
                else COLOR_TEXT_SECONDARY
            ),
        )
        status_label.pack(pady=(0, 10), padx=20, anchor="w")

        # Preset buttons
        presets_grid = ctk.CTkFrame(limit_frame, fg_color="transparent")
        presets_grid.pack(pady=10, padx=20, fill="x")

        def set_charge_limit(limit_value, preset_name):
            if battery_ctrl and battery_ctrl.is_supported():
                success, msg = battery_ctrl.set_charge_limit(limit_value)
                if success:
                    status_label.configure(text=f"✓ {msg}", text_color=COLOR_SUCCESS)
                    limit_slider.set(limit_value)
                else:
                    status_label.configure(text=f"✗ {msg}", text_color=COLOR_WARNING)
            else:
                status_label.configure(
                    text="Charge limit control not supported", text_color=COLOR_WARNING
                )

        presets = [
            ("🔋 Maximum (100%)", 100),
            ("⚖️ Balanced (80%)", 80),
            ("❤️ Lifespan (60%)", 60),
        ]

        col = 0
        for preset_name, preset_value in presets:
            is_current = preset_value == current_limit
            btn = ctk.CTkButton(
                presets_grid,
                text=preset_name,
                fg_color=COLOR_ACCENT if is_current else COLOR_BG_HOVER,
                hover_color=COLOR_ACCENT,
                corner_radius=6,
                height=40,
                command=lambda v=preset_value, n=preset_name: set_charge_limit(v, n),
            )
            btn.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            col += 1

        presets_grid.grid_columnconfigure(0, weight=1)
        presets_grid.grid_columnconfigure(1, weight=1)
        presets_grid.grid_columnconfigure(2, weight=1)

        # Custom limit slider
        ctk.CTkLabel(
            limit_frame,
            text="Custom Limit:",
            font=("Segoe UI", 11, "bold"),
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        def on_slider_change(value):
            limit_value_label.configure(text=f"{int(value)}%")

        limit_slider = ctk.CTkSlider(
            limit_frame,
            from_=60,
            to=100,
            command=on_slider_change,
            fg_color=COLOR_BG_HOVER,
            button_color=COLOR_ACCENT,
            button_hover_color=COLOR_ACCENT_HOVER,
        )
        limit_slider.pack(pady=10, padx=20, fill="x")
        limit_slider.set(current_limit)

        limit_value_label = ctk.CTkLabel(
            limit_frame,
            text=f"{current_limit}%",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXT_PRIMARY,
        )
        limit_value_label.pack(pady=(0, 10), padx=20)

        # Apply button for custom limit
        ctk.CTkButton(
            limit_frame,
            text="Apply Custom Limit",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            corner_radius=6,
            height=40,
            command=lambda: set_charge_limit(int(limit_slider.get()), "Custom"),
        ).pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(limit_frame, text=" ", font=("Segoe UI", 5)).pack(pady=5)

    def show_settings(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(
            self.main_frame,
            text="⚙️ Settings",
            font=("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.pack(pady=(0, 20), anchor="w")

        # General Settings
        general_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        general_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            general_frame,
            text="⚙️ General",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 10), padx=20, anchor="w")

        ctk.CTkSwitch(
            general_frame,
            text="Start with System",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=5, padx=20, anchor="w")

        ctk.CTkSwitch(
            general_frame,
            text="Minimize to Tray",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(5, 15), padx=20, anchor="w")

        # Power Management Settings
        power_frame = ctk.CTkFrame(
            self.main_frame, fg_color=COLOR_BG_CARD, corner_radius=CORNER_RADIUS
        )
        power_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            power_frame,
            text="🔌 Power Management",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(pady=(15, 5), padx=20, anchor="w")

        ctk.CTkLabel(
            power_frame,
            text="Automatically switch power profiles based on AC adapter status",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(pady=(0, 10), padx=20, anchor="w")

        # Auto profile switching toggle
        def toggle_auto_profile():
            self.auto_profile_switching = auto_switch.get()
            if self.auto_profile_switching:
                status_label.configure(
                    text="✓ Auto switching enabled - Gaming / Battery Saver",
                    text_color=COLOR_SUCCESS,
                )
                print("Auto profile switching enabled")
            else:
                status_label.configure(
                    text="Auto profile switching disabled",
                    text_color=COLOR_TEXT_SECONDARY,
                )
                print("Auto profile switching disabled")

        auto_switch = ctk.CTkSwitch(
            power_frame,
            text="Auto Profile Switching",
            font=("Segoe UI", 12),
            text_color=COLOR_TEXT_PRIMARY,
            command=toggle_auto_profile,
        )
        auto_switch.pack(pady=5, padx=20, anchor="w")

        # Set initial state
        if hasattr(self, "auto_profile_switching") and self.auto_profile_switching:
            auto_switch.select()

        # Status label
        status_label = ctk.CTkLabel(
            power_frame,
            text=(
                "Auto profile switching disabled"
                if not hasattr(self, "auto_profile_switching")
                or not self.auto_profile_switching
                else "✓ Auto switching enabled - Gaming / Battery Saver"
            ),
            font=("Segoe UI", 10),
            text_color=(
                COLOR_TEXT_SECONDARY
                if not hasattr(self, "auto_profile_switching")
                or not self.auto_profile_switching
                else COLOR_SUCCESS
            ),
        )
        status_label.pack(pady=(5, 15), padx=20, anchor="w")

    def update_loop(self):
        """Background thread for updating system stats"""
        # Initialize GPU controller once
        gpu_ctrl = None
        if HAS_MODULES:
            try:
                from .modules.gpu_control import GpuController

                gpu_ctrl = GpuController()
            except Exception:
                pass

        while self.monitoring:
            try:
                if self.system_monitor:
                    # Get CPU stats
                    cpu_stats = self.system_monitor.get_cpu_stats()
                    cpu_usage = cpu_stats.usage_percent
                    cpu_temp = get_cpu_temperature()

                    # Get GPU stats using GpuController
                    gpu_usage = 0.0
                    gpu_temp = 0.0

                    if gpu_ctrl:
                        try:
                            gpu_stats = gpu_ctrl.get_live_stats()
                            gpu_usage = float(gpu_stats.gpu_usage_percent)
                            gpu_temp = float(gpu_stats.gpu_temp_c)

                            # If GPU stats are zero, try to get temperature at least
                            if gpu_temp == 0:
                                gpu_temp = get_gpu_temperature()
                        except Exception:
                            # Fallback to basic temperature reading
                            gpu_temp = get_gpu_temperature()
                    else:
                        # Fallback to basic temperature reading
                        gpu_temp = get_gpu_temperature()

                    # Get RAM stats
                    mem_stats = self.system_monitor.get_memory_stats()
                    ram_usage = mem_stats.usage_percent
                    ram_used_gb = mem_stats.used_mb / 1024
                    ram_total_gb = mem_stats.total_mb / 1024

                    # Get Disk stats (root partition)
                    disk_stats_list = self.system_monitor.get_disk_stats()
                    disk_usage = 0.0
                    disk_used_gb = 0.0
                    disk_total_gb = 0.0

                    if disk_stats_list:
                        # Find root partition
                        for disk in disk_stats_list:
                            if disk.mountpoint == "/":
                                disk_usage = disk.usage_percent
                                disk_used_gb = disk.used_gb
                                disk_total_gb = disk.total_gb
                                break
                        # If no root found, use first partition
                        if disk_usage == 0.0 and disk_stats_list:
                            disk = disk_stats_list[0]
                            disk_usage = disk.usage_percent
                            disk_used_gb = disk.used_gb
                            disk_total_gb = disk.total_gb
                else:
                    # Fallback to random data in demo mode
                    import random

                    cpu_usage = random.randint(20, 60)
                    cpu_temp = random.randint(50, 75)
                    gpu_usage = random.randint(10, 40)
                    gpu_temp = random.randint(45, 65)
                    ram_usage = random.randint(40, 70)
                    ram_used_gb = random.randint(8, 14)
                    ram_total_gb = 16
                    disk_usage = random.randint(50, 80)
                    disk_used_gb = random.randint(100, 300)
                    disk_total_gb = 512

                # Update UI on main thread
                if hasattr(self, "monitor_card"):
                    # Update monitor UI via a small helper (keeps lines short)
                    def _update_monitor():
                        self.monitor_card.update_stats(
                            cpu_usage,
                            cpu_temp,
                            gpu_usage,
                            gpu_temp,
                            ram_usage,
                            ram_used_gb,
                            ram_total_gb,
                            disk_usage,
                            disk_used_gb,
                            disk_total_gb,
                        )

                    self.after(0, _update_monitor)

                # Auto profile switching based on AC adapter
                if self.auto_profile_switching and self.asusd_client and HAS_MODULES:
                    try:
                        # Check AC adapter status via battery controller
                        battery_ctrl = get_battery_controller()
                        if battery_ctrl and battery_ctrl.is_supported():
                            battery_status = battery_ctrl.get_battery_status()

                            # Determine if on AC (Charging or Full means plugged in)
                            on_ac = battery_status in [
                                "Charging",
                                "Full",
                                "Not charging",
                            ]

                            # Only switch if status changed
                            if on_ac != self.last_ac_status:
                                self.last_ac_status = on_ac

                                if on_ac:
                                    # Plugged in - switch to Gaming (70W Performance)
                                    print("AC adapter connected - switching to Gaming")
                                    self.asusd_client.set_throttle_policy(
                                        ThrottlePolicy.PERFORMANCE
                                    )

                                    # Also set TDP if overclocking controller available
                                    try:
                                        from .modules.overclocking_control import (
                                            OverclockingController,
                                        )

                                        oc_ctrl = OverclockingController()
                                        if oc_ctrl.ryzenadj_available:
                                            oc_ctrl.set_ryzenadj_tdp(
                                                stapm_limit=70,
                                                fast_limit=75,
                                                slow_limit=70,
                                            )
                                            print("TDP set to Gaming profile (70W)")
                                    except Exception:
                                        pass
                                else:
                                    # On battery - switch to Battery Saver (18W)
                                    print("On battery - switching to Battery Saver")
                                    self.asusd_client.set_throttle_policy(
                                        ThrottlePolicy.QUIET
                                    )

                                    # Also set TDP if overclocking controller available
                                    try:
                                        from .modules.overclocking_control import (
                                            OverclockingController,
                                        )

                                        oc_ctrl = OverclockingController()
                                        if oc_ctrl.ryzenadj_available:
                                            oc_ctrl.set_ryzenadj_tdp(
                                                stapm_limit=18,
                                                fast_limit=20,
                                                slow_limit=18,
                                            )
                                            print("TDP set to Battery Saver (18W)")
                                    except Exception:
                                        pass
                    except Exception as e:
                        print(f"Auto profile switching error: {e}")

                time.sleep(2)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(2)

    def set_tdp(self, watts: int) -> bool:
        """Set TDP using RyzenAdj if available"""
        if hasattr(self, "perf_card") and self.perf_card.oc_controller:
            try:
                success = self.perf_card.oc_controller.set_ryzenadj_tdp(
                    stapm_limit=watts, fast_limit=watts + 5, slow_limit=watts
                )
                if success:
                    self.show_toast(f"TDP set to {watts}W", "success")
                else:
                    self.show_toast("Failed to set TDP", "warning")
                return success
            except Exception as e:
                self.logger.error(f"Failed to set TDP: {e}")
                self.show_toast(f"Error setting TDP: {e}", "error")
                return False
        else:
            self.show_toast("RyzenAdj not available", "warning")
            return False

    def destroy(self):
        self.monitoring = False
        # Save current window size to settings
        self.settings["window_size"] = [self.winfo_width(), self.winfo_height()]
        self.config_manager.save_settings(self.settings)
        super().destroy()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
