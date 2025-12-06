#!/usr/bin/env python3
"""
Linux Armoury - GUI Control Center for ASUS ROG Laptops
A modern GTK4/libadwaita control center inspired by ROG Control Center
Features: Power profiles, display control, fan curves, RGB keyboard, battery management
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
import json
import os
import shlex
import subprocess
import sys
from typing import Optional

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

# New modules for configuration and system utilities
try:
    from .config import Config
except Exception:

    class Config:  # minimal fallback if config.py not installed
        APP_ID = "com.github.th3cavalry.linux-armoury"
        DEFAULT_RESOLUTION = "2560x1600"
        VERSION = "1.0.0"


try:
    from .system_utils import SystemUtils
except Exception:

    class SystemUtils:  # minimal fallbacks
        @staticmethod
        def get_primary_display():
            return "eDP-1"

        @staticmethod
        def get_display_resolution():
            try:
                w, h = Config.DEFAULT_RESOLUTION.split("x")
                return (int(w), int(h))
            except Exception:
                return (2560, 1600)

        @staticmethod
        def get_current_refresh_rate():
            return None

        @staticmethod
        def get_current_tdp():
            return None


# New feature modules (optional - gracefully handle if not present)
try:
    from .modules.battery_control import ChargeLimitPreset, get_battery_controller

    HAS_BATTERY_CONTROL = True
except ImportError:
    HAS_BATTERY_CONTROL = False

try:
    from .modules.fan_control import get_fan_controller

    HAS_FAN_CONTROL = True
except ImportError:
    HAS_FAN_CONTROL = False

try:
    from .modules.keyboard_control import get_keyboard_controller

    HAS_KEYBOARD_CONTROL = True
except ImportError:
    HAS_KEYBOARD_CONTROL = False

try:
    from .modules.hardware_detection import HardwareFeature, detect_hardware

    HAS_HARDWARE_DETECTION = True
except ImportError:
    HAS_HARDWARE_DETECTION = False

try:
    from .fan_curve_editor import FanCurveEditorDialog, FanCurveWidget, get_preset_curve

    HAS_FAN_CURVE_EDITOR = True
except ImportError:
    HAS_FAN_CURVE_EDITOR = False

try:
    from .modules.session_stats import SessionStatistics, get_session_stats

    HAS_SESSION_STATS = True
except ImportError:
    HAS_SESSION_STATS = False

try:
    from .tray_icon import SystemTrayIcon, create_tray_icon

    HAS_TRAY_ICON = True
except ImportError:
    HAS_TRAY_ICON = False

try:
    from .modules.overclocking_control import (
        TDP_PRESETS,
        CPUInfo,
        GPUInfo,
        OverclockingController,
    )

    HAS_OVERCLOCKING = True
except ImportError:
    HAS_OVERCLOCKING = False

try:
    from .modules.gpu_control import (
        GpuController,
        GpuLiveStats,
        GpuMode,
        GpuPowerStatus,
        GpuSwitchingStatus,
    )
    from .modules.gpu_control import get_controller as get_gpu_controller

    HAS_GPU_CONTROL = True
except ImportError:
    HAS_GPU_CONTROL = False

try:
    from .modules.system_monitor import (
        CpuStats,
        DiskStats,
        MemoryStats,
        NetworkStats,
        ProcessInfo,
        SystemMonitor,
        SystemOverview,
        get_monitor,
    )

    HAS_SYSTEM_MONITOR = True
except ImportError:
    HAS_SYSTEM_MONITOR = False

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/linux-armoury")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Custom CSS for styling
CUSTOM_CSS = """
/* ========================================
   Linux Armoury - CYBERPUNK GAMING UI
   Aggressive, high-tech aesthetic for ROG
   Neon accents, sharp angles, glow effects
   ======================================== */

/* === Global Dark Theme with Hex Grid === */
@define-color neon_cyan #00fff9;
@define-color neon_magenta #ff00ff;
@define-color neon_red #ff0040;
@define-color neon_orange #ff6600;
@define-color neon_green #00ff41;
@define-color neon_blue #0080ff;
@define-color cyber_bg #0a0a0f;
@define-color cyber_surface #12121a;
@define-color cyber_card #1a1a28;
@define-color cyber_accent #ff00ff;

window.background {
    background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%);
    background-image:
        linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%),
        repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0, 255, 249, 0.03) 2px, rgba(0, 255, 249, 0.03) 4px),
        repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255, 0, 255, 0.03) 2px, rgba(255, 0, 255, 0.03) 4px);
}

/* === CYBER STATUS CARDS === */
.status-card {
    background: linear-gradient(145deg,
        @cyber_card,
        alpha(@cyber_card, 0.8));
    border-radius: 4px;
    padding: 20px;
    margin: 8px 0;
    box-shadow:
        0 0 20px alpha(@neon_cyan, 0.2),
        0 4px 15px alpha(black, 0.5),
        inset 0 1px 0 alpha(@neon_cyan, 0.2);
    border: 1px solid alpha(@neon_cyan, 0.3);
    border-left: 3px solid @neon_cyan;
}

.status-card:hover {
    background: linear-gradient(145deg,
        shade(@cyber_card, 1.2),
        @cyber_card);
    box-shadow:
        0 0 30px alpha(@neon_cyan, 0.4),
        0 6px 20px alpha(black, 0.6),
        inset 0 1px 0 alpha(@neon_cyan, 0.4);
    border-color: @neon_cyan;
    transform: translateY(-2px);
}

/* === CYBER STAT CARDS === */
.stat-card {
    background: linear-gradient(135deg,
        alpha(@neon_magenta, 0.15),
        alpha(@cyber_card, 0.9));
    border-radius: 2px;
    padding: 16px;
    border: 1px solid alpha(@neon_magenta, 0.4);
    border-top: 3px solid @neon_magenta;
    box-shadow:
        0 0 15px alpha(@neon_magenta, 0.3),
        inset 0 0 20px alpha(@neon_magenta, 0.05);
}

.stat-value {
    font-size: 2.5em;
    font-weight: 900;
    color: @neon_cyan;
    text-shadow:
        0 0 10px @neon_cyan,
        0 0 20px alpha(@neon_cyan, 0.5);
    font-family: 'Orbitron', 'Rajdhani', 'Share Tech Mono', monospace;
    letter-spacing: 2px;
}

.stat-label {
    font-size: 0.85em;
    color: alpha(@neon_cyan, 0.7);
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* === CYBER TEMPERATURE COLORS === */
.temp-cool {
    color: @neon_cyan;
    text-shadow:
        0 0 10px @neon_cyan,
        0 0 20px alpha(@neon_cyan, 0.5),
        0 0 30px alpha(@neon_cyan, 0.3);
    font-weight: 700;
}
.temp-warm {
    color: @neon_orange;
    text-shadow:
        0 0 10px @neon_orange,
        0 0 20px alpha(@neon_orange, 0.5),
        0 0 30px alpha(@neon_orange, 0.3);
    font-weight: 700;
}
.temp-hot {
    color: @neon_red;
    text-shadow:
        0 0 12px @neon_red,
        0 0 24px alpha(@neon_red, 0.6),
        0 0 36px alpha(@neon_red, 0.4);
    font-weight: 800;
    animation: pulse-hot 2s ease-in-out infinite;
}
.temp-critical {
    color: @neon_red;
    text-shadow:
        0 0 15px @neon_red,
        0 0 30px @neon_red,
        0 0 45px alpha(@neon_red, 0.5);
    font-weight: 900;
    animation: pulse-critical 1s ease-in-out infinite;
}

@keyframes pulse-hot {
    0%, 100% {
        text-shadow:
            0 0 12px @neon_red,
            0 0 24px alpha(@neon_red, 0.6),
            0 0 36px alpha(@neon_red, 0.4);
    }
    50% {
        text-shadow:
            0 0 15px @neon_red,
            0 0 30px @neon_red,
            0 0 45px alpha(@neon_red, 0.6);
    }
}

@keyframes pulse-critical {
    0%, 100% {
        text-shadow:
            0 0 15px @neon_red,
            0 0 30px @neon_red,
            0 0 45px alpha(@neon_red, 0.5);
    }
    50% {
        text-shadow:
            0 0 20px @neon_red,
            0 0 40px @neon_red,
            0 0 60px @neon_red;
    }
}

/* === CYBER PROFILE CARDS === */
.profile-card {
    border-radius: 2px;
    padding: 16px;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    background: @cyber_card;
    border: 1px solid alpha(@neon_magenta, 0.2);
    border-left: 3px solid transparent;
}

.profile-card:hover {
    background: linear-gradient(135deg, alpha(@neon_magenta, 0.15), @cyber_card);
    transform: translateX(5px);
    box-shadow:
        -5px 0 20px alpha(@neon_magenta, 0.3),
        0 4px 15px alpha(black, 0.3);
    border-left-color: @neon_magenta;
}

.profile-card.selected {
    background: linear-gradient(135deg,
        alpha(@neon_cyan, 0.2),
        alpha(@cyber_card, 0.9));
    border: 1px solid @neon_cyan;
    border-left: 4px solid @neon_cyan;
    box-shadow:
        -5px 0 25px alpha(@neon_cyan, 0.5),
        0 0 30px alpha(@neon_cyan, 0.3),
        inset 0 0 20px alpha(@neon_cyan, 0.1);
    transform: translateX(8px);
}

.profile-card.selected label {
    color: @neon_cyan;
    font-weight: 800;
    text-shadow: 0 0 10px @neon_cyan;
}

/* === CYBER BATTERY INDICATORS === */
.battery-low {
    color: @neon_red;
    text-shadow: 0 0 10px @neon_red, 0 0 20px alpha(@neon_red, 0.5);
    animation: battery-warning 1.5s ease-in-out infinite;
}
.battery-medium {
    color: @neon_orange;
    text-shadow: 0 0 8px @neon_orange, 0 0 16px alpha(@neon_orange, 0.4);
}
.battery-good {
    color: @neon_green;
    text-shadow: 0 0 8px @neon_green, 0 0 16px alpha(@neon_green, 0.3);
}
.battery-charging {
    color: @neon_cyan;
    text-shadow: 0 0 10px @neon_cyan, 0 0 20px @neon_cyan;
    animation: charging-pulse 1.5s ease-in-out infinite;
}

@keyframes battery-warning {
    0%, 100% {
        text-shadow: 0 0 10px @neon_red, 0 0 20px alpha(@neon_red, 0.5);
    }
    50% {
        text-shadow: 0 0 15px @neon_red, 0 0 30px @neon_red;
    }
}

@keyframes charging-pulse {
    0%, 100% {
        text-shadow: 0 0 10px @neon_cyan, 0 0 20px @neon_cyan;
        opacity: 1;
    }
    50% {
        text-shadow: 0 0 15px @neon_cyan, 0 0 30px @neon_cyan, 0 0 40px alpha(@neon_cyan, 0.5);
        opacity: 0.8;
    }
}

/* === CYBER SECTION HEADERS === */
.section-header {
    font-weight: 900;
    font-size: 1.4em;
    letter-spacing: 2px;
    color: @neon_cyan;
    text-transform: uppercase;
    text-shadow:
        0 0 10px @neon_cyan,
        0 0 20px alpha(@neon_cyan, 0.5);
    font-family: 'Orbitron', 'Rajdhani', sans-serif;
    border-bottom: 2px solid @neon_cyan;
    padding-bottom: 8px;
    margin-bottom: 12px;
}

/* === CYBER SIDEBAR === */
.navigation-sidebar {
    background: linear-gradient(180deg, @cyber_bg, @cyber_surface);
    border-right: 1px solid alpha(@neon_cyan, 0.2);
    box-shadow: inset -5px 0 15px alpha(@neon_cyan, 0.1);
}

.navigation-sidebar row {
    margin: 3px 6px;
    border-radius: 2px;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    border-left: 3px solid transparent;
}

.navigation-sidebar row:hover {
    background: linear-gradient(90deg,
        alpha(@neon_magenta, 0.15),
        transparent);
    border-left-color: @neon_magenta;
    transform: translateX(5px);
    box-shadow: 0 0 15px alpha(@neon_magenta, 0.3);
}

.navigation-sidebar row:selected {
    background: linear-gradient(90deg,
        alpha(@neon_cyan, 0.25),
        alpha(@neon_cyan, 0.05));
    border-left: 4px solid @neon_cyan;
    box-shadow:
        0 0 20px alpha(@neon_cyan, 0.4),
        inset 0 0 15px alpha(@neon_cyan, 0.1);
    transform: translateX(8px);
}

.sidebar-row {
    padding: 12px 16px;
    border-radius: 0;
    margin: 3px 8px;
}

.sidebar-row image {
    color: alpha(@neon_cyan, 0.6);
    filter: drop-shadow(0 0 5px alpha(@neon_cyan, 0.3));
}

.sidebar-row:selected image {
    color: @neon_cyan;
    filter: drop-shadow(0 0 8px @neon_cyan);
}

.sidebar-row:selected label {
    color: @neon_cyan;
    font-weight: 700;
    text-shadow: 0 0 8px alpha(@neon_cyan, 0.5);
}

/* === CYBER RGB PREVIEW === */
.rgb-preview {
    border-radius: 2px;
    min-width: 60px;
    min-height: 60px;
    box-shadow:
        0 0 20px alpha(currentColor, 0.6),
        0 4px 15px alpha(black, 0.5),
        inset 0 0 30px alpha(currentColor, 0.3);
    border: 2px solid currentColor;
}

/* === CYBER FAN INDICATOR === */
.fan-indicator {
    font-family: 'Share Tech Mono', 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 1.3em;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 2px;
    background: @cyber_card;
    border: 1px solid @neon_green;
    border-left: 3px solid @neon_green;
    color: @neon_green;
    text-shadow: 0 0 8px @neon_green;
    box-shadow:
        0 0 15px alpha(@neon_green, 0.3),
        inset 0 0 10px alpha(@neon_green, 0.1);
}

/* === CYBER QUICK TOGGLE BUTTONS === */
.quick-toggle {
    border-radius: 2px;
    padding: 12px 20px;
    min-width: 110px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    background: @cyber_card;
    border: 1px solid alpha(@neon_magenta, 0.3);
    color: @neon_magenta;
}

.quick-toggle:hover {
    background: linear-gradient(135deg, alpha(@neon_magenta, 0.2), @cyber_card);
    border-color: @neon_magenta;
    box-shadow:
        0 0 20px alpha(@neon_magenta, 0.4),
        inset 0 0 15px alpha(@neon_magenta, 0.1);
    transform: scale(1.05);
}

.quick-toggle.active {
    background: linear-gradient(135deg, alpha(@neon_cyan, 0.3), alpha(@neon_magenta, 0.2));
    color: @neon_cyan;
    border: 2px solid @neon_cyan;
    box-shadow:
        0 0 25px @neon_cyan,
        inset 0 0 20px alpha(@neon_cyan, 0.2);
    text-shadow: 0 0 10px @neon_cyan;
    transform: scale(1.1);
}

/* === CYBER PILL BUTTONS (TDP Presets) === */
.pill {
    border-radius: 2px;
    padding: 10px 18px;
    min-width: 90px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    background: @cyber_card;
    border: 1px solid alpha(@neon_orange, 0.4);
    color: @neon_orange;
}

.pill:hover {
    background: linear-gradient(135deg, alpha(@neon_orange, 0.2), @cyber_card);
    border-color: @neon_orange;
    box-shadow:
        0 0 20px alpha(@neon_orange, 0.4),
        inset 0 0 15px alpha(@neon_orange, 0.1);
    transform: translateY(-3px) scale(1.05);
    text-shadow: 0 0 8px @neon_orange;
}

.pill.suggested-action {
    background: linear-gradient(135deg, alpha(@neon_red, 0.3), alpha(@neon_orange, 0.2));
    color: @neon_red;
    border: 2px solid @neon_red;
    box-shadow:
        0 0 25px alpha(@neon_red, 0.5),
        inset 0 0 20px alpha(@neon_red, 0.2);
    text-shadow: 0 0 10px @neon_red;
}

.pill.suggested-action:hover {
    background: linear-gradient(135deg, alpha(@neon_red, 0.4), alpha(@neon_orange, 0.3));
    box-shadow:
        0 0 30px @neon_red,
        inset 0 0 25px alpha(@neon_red, 0.3);
    transform: translateY(-4px) scale(1.08);
}

/* === CYBER OVERCLOCKING SECTIONS === */
.oc-cpu-section {
    background: linear-gradient(135deg,
        alpha(@neon_blue, 0.15),
        alpha(@cyber_card, 0.9));
    border-radius: 2px;
    border: 1px solid @neon_blue;
    border-top: 3px solid @neon_blue;
    box-shadow:
        0 0 25px alpha(@neon_blue, 0.3),
        inset 0 0 30px alpha(@neon_blue, 0.05);
}

.oc-gpu-section {
    background: linear-gradient(135deg,
        alpha(@neon_orange, 0.15),
        alpha(@cyber_card, 0.9));
    border-radius: 2px;
    border: 1px solid @neon_orange;
    border-top: 3px solid @neon_orange;
    box-shadow:
        0 0 25px alpha(@neon_orange, 0.3),
        inset 0 0 30px alpha(@neon_orange, 0.05);
}

.oc-tdp-section {
    background: linear-gradient(135deg,
        alpha(@neon_red, 0.15),
        alpha(@cyber_card, 0.9));
    border-radius: 2px;
    border: 1px solid @neon_red;
    border-top: 3px solid @neon_red;
    box-shadow:
        0 0 25px alpha(@neon_red, 0.3),
        inset 0 0 30px alpha(@neon_red, 0.05);
}

/* === CYBER SCALES/SLIDERS === */
scale trough {
    border-radius: 0;
    min-height: 6px;
    background: @cyber_card;
    border: 1px solid alpha(@neon_magenta, 0.3);
    box-shadow: inset 0 0 10px alpha(@neon_magenta, 0.1);
}

scale highlight {
    border-radius: 0;
    background: linear-gradient(90deg, @neon_magenta, @neon_cyan);
    box-shadow:
        0 0 15px @neon_cyan,
        inset 0 0 10px alpha(@neon_cyan, 0.3);
}

scale slider {
    border-radius: 2px;
    min-width: 20px;
    min-height: 20px;
    background: @neon_cyan;
    border: 2px solid @cyber_bg;
    box-shadow:
        0 0 15px @neon_cyan,
        0 2px 6px alpha(black, 0.4);
}

scale slider:hover {
    background: @neon_magenta;
    box-shadow:
        0 0 20px @neon_magenta,
        0 3px 8px alpha(black, 0.5);
    transform: scale(1.2);
}

/* === CYBER PROGRESS BARS === */
progressbar trough {
    border-radius: 0;
    min-height: 12px;
    background: @cyber_card;
    border: 1px solid alpha(@neon_cyan, 0.3);
    box-shadow: inset 0 0 10px alpha(black, 0.5);
}

progressbar progress {
    border-radius: 0;
    background: linear-gradient(90deg,
        @neon_cyan,
        @neon_magenta,
        @neon_cyan);
    background-size: 200% 100%;
    animation: progress-shine 2s linear infinite;
    box-shadow:
        0 0 15px @neon_cyan,
        inset 0 0 10px alpha(@neon_cyan, 0.5);
}

@keyframes progress-shine {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

/* === CYBER LEVEL BARS === */
levelbar block.filled {
    border-radius: 0;
    background: linear-gradient(90deg, @neon_cyan, @neon_magenta);
    box-shadow:
        0 0 10px @neon_cyan,
        inset 0 0 5px alpha(@neon_cyan, 0.5);
    margin: 1px;
}

levelbar block.empty {
    border-radius: 0;
    background: @cyber_card;
    border: 1px solid alpha(@neon_cyan, 0.2);
    margin: 1px;
}

levelbar.low block.filled {
    background: @neon_red;
    box-shadow:
        0 0 12px @neon_red,
        inset 0 0 8px alpha(@neon_red, 0.5);
    animation: level-warning 1.5s ease-in-out infinite;
}

levelbar.high block.filled {
    background: @neon_green;
    box-shadow:
        0 0 10px @neon_green,
        inset 0 0 5px alpha(@neon_green, 0.5);
}

@keyframes level-warning {
    0%, 100% {
        box-shadow: 0 0 12px @neon_red, inset 0 0 8px alpha(@neon_red, 0.5);
    }
    50% {
        box-shadow: 0 0 18px @neon_red, inset 0 0 12px alpha(@neon_red, 0.7);
    }
}

/* === CYBER INFO BADGES === */
.info-badge {
    background: alpha(@neon_cyan, 0.2);
    border-radius: 2px;
    padding: 5px 12px;
    font-size: 0.85em;
    font-weight: 700;
    color: @neon_cyan;
    border: 1px solid @neon_cyan;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow:
        0 0 10px alpha(@neon_cyan, 0.3),
        inset 0 0 5px alpha(@neon_cyan, 0.1);
}

.warning-badge {
    background: alpha(@neon_orange, 0.2);
    color: @neon_orange;
    border-radius: 2px;
    padding: 5px 12px;
    font-size: 0.85em;
    font-weight: 700;
    border: 1px solid @neon_orange;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow:
        0 0 10px alpha(@neon_orange, 0.3),
        inset 0 0 5px alpha(@neon_orange, 0.1);
}

.error-badge {
    background: alpha(@neon_red, 0.2);
    color: @neon_red;
    border-radius: 2px;
    padding: 5px 12px;
    font-size: 0.85em;
    font-weight: 700;
    border: 1px solid @neon_red;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow:
        0 0 10px alpha(@neon_red, 0.3),
        inset 0 0 5px alpha(@neon_red, 0.1);
    animation: badge-pulse 2s ease-in-out infinite;
}

.success-badge {
    background: alpha(@neon_green, 0.2);
    color: @neon_green;
    border-radius: 2px;
    padding: 5px 12px;
    font-size: 0.85em;
    font-weight: 700;
    border: 1px solid @neon_green;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow:
        0 0 10px alpha(@neon_green, 0.3),
        inset 0 0 5px alpha(@neon_green, 0.1);
}

@keyframes badge-pulse {
    0%, 100% {
        box-shadow: 0 0 10px alpha(@neon_red, 0.3), inset 0 0 5px alpha(@neon_red, 0.1);
    }
    50% {
        box-shadow: 0 0 20px alpha(@neon_red, 0.6), inset 0 0 10px alpha(@neon_red, 0.2);
    }
}

/* === CYBER LIST BOXES === */
list {
    background: transparent;
}

list row {
    border-radius: 0;
    margin: 2px 0;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
    border-left: 2px solid transparent;
}

list row:hover {
    background: linear-gradient(90deg, alpha(@neon_magenta, 0.1), transparent);
    border-left-color: @neon_magenta;
    box-shadow: 0 0 15px alpha(@neon_magenta, 0.2);
}

/* === CYBER COMBO ROWS === */
comborow dropdown {
    border-radius: 0;
    background: @cyber_card;
    border: 1px solid alpha(@neon_cyan, 0.3);
    box-shadow: 0 4px 15px alpha(black, 0.5);
}

/* === CYBER SWITCH === */
switch {
    border-radius: 0;
    min-width: 54px;
    background: @cyber_card;
    border: 1px solid alpha(@neon_magenta, 0.3);
    box-shadow: inset 0 0 10px alpha(black, 0.5);
}

switch:checked {
    background: linear-gradient(90deg, @neon_cyan, @neon_magenta);
    border-color: @neon_cyan;
    box-shadow:
        0 0 15px @neon_cyan,
        inset 0 0 10px alpha(@neon_cyan, 0.3);
}

switch slider {
    border-radius: 2px;
    background: @neon_magenta;
    border: 2px solid @cyber_bg;
    box-shadow: 0 0 10px @neon_magenta;
}

switch:checked slider {
    background: @neon_cyan;
    box-shadow: 0 0 15px @neon_cyan;
}

/* === CYBER HEADER BAR === */
headerbar {
    background: linear-gradient(90deg, @cyber_bg, @cyber_surface, @cyber_bg);
    border-bottom: 1px solid alpha(@neon_cyan, 0.3);
    box-shadow:
        0 2px 10px alpha(black, 0.5),
        inset 0 -1px 0 alpha(@neon_cyan, 0.2);
}

headerbar button {
    border-radius: 2px;
    border: 1px solid alpha(@neon_magenta, 0.2);
    background: alpha(@cyber_card, 0.5);
}

headerbar button:hover {
    background: alpha(@neon_magenta, 0.2);
    border-color: @neon_magenta;
    box-shadow:
        0 0 15px alpha(@neon_magenta, 0.3),
        inset 0 0 10px alpha(@neon_magenta, 0.1);
}

headerbar button:active {
    background: alpha(@neon_cyan, 0.3);
    border-color: @neon_cyan;
    box-shadow: 0 0 20px alpha(@neon_cyan, 0.5);
}

/* === CYBER TOAST NOTIFICATIONS === */
toast {
    border-radius: 2px;
    background: @cyber_card;
    border: 1px solid @neon_cyan;
    border-left: 4px solid @neon_cyan;
    box-shadow:
        0 0 20px alpha(@neon_cyan, 0.4),
        0 6px 20px alpha(black, 0.5);
}

toast label {
    color: @neon_cyan;
    text-shadow: 0 0 5px alpha(@neon_cyan, 0.5);
}

/* === CYBER PREFERENCES GROUPS === */
preferencesgroup {
    background: alpha(@cyber_card, 0.5);
    border: 1px solid alpha(@neon_cyan, 0.2);
    border-left: 2px solid @neon_cyan;
    box-shadow:
        0 0 15px alpha(@neon_cyan, 0.1),
        inset 0 0 20px alpha(black, 0.3);
}

preferencesgroup > box > box:first-child {
    padding-bottom: 8px;
    border-bottom: 1px solid alpha(@neon_cyan, 0.2);
}

preferencesgroup .title {
    color: @neon_cyan;
    font-weight: 700;
    text-shadow: 0 0 8px alpha(@neon_cyan, 0.3);
}

/* === CYBER TITLES === */
.title-1 {
    font-size: 2.5em;
    font-weight: 900;
    color: @neon_cyan;
    text-shadow:
        0 0 15px @neon_cyan,
        0 0 30px alpha(@neon_cyan, 0.5);
    font-family: 'Orbitron', 'Rajdhani', sans-serif;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.title-2 {
    font-size: 1.8em;
    font-weight: 800;
    color: @neon_magenta;
    text-shadow:
        0 0 10px @neon_magenta,
        0 0 20px alpha(@neon_magenta, 0.4);
    font-family: 'Orbitron', 'Rajdhani', sans-serif;
    letter-spacing: 2px;
}

.title-3 {
    font-size: 1.3em;
    font-weight: 700;
    color: @neon_cyan;
    text-shadow: 0 0 8px alpha(@neon_cyan, 0.4);
    letter-spacing: 1px;
}

.title-4 {
    font-size: 1.1em;
    font-weight: 700;
    font-family: 'Share Tech Mono', monospace;
}

.dim-label {
    opacity: 0.6;
    color: alpha(@neon_cyan, 0.7);
}

.accent {
    color: @neon_cyan;
    text-shadow: 0 0 10px alpha(@neon_cyan, 0.5);
}

/* === CYBER ANIMATIONS === */
.active-indicator {
    animation: cyber-glow 1.5s ease-in-out infinite alternate;
}

@keyframes cyber-glow {
    from {
        box-shadow:
            0 0 10px alpha(@neon_cyan, 0.5),
            0 0 20px alpha(@neon_cyan, 0.3);
    }
    to {
        box-shadow:
            0 0 20px @neon_cyan,
            0 0 40px alpha(@neon_cyan, 0.6),
            0 0 60px alpha(@neon_cyan, 0.4);
    }
}

/* === CYBER BUTTON ENHANCEMENTS === */
button {
    border-radius: 2px;
    border: 1px solid alpha(@neon_magenta, 0.3);
    background: @cyber_card;
    color: @neon_magenta;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

button:hover {
    background: linear-gradient(135deg, alpha(@neon_magenta, 0.2), @cyber_card);
    border-color: @neon_magenta;
    box-shadow:
        0 0 15px alpha(@neon_magenta, 0.3),
        inset 0 0 10px alpha(@neon_magenta, 0.1);
    transform: translateY(-2px);
}

button:active {
    background: linear-gradient(135deg, alpha(@neon_cyan, 0.3), @cyber_card);
    border-color: @neon_cyan;
    box-shadow: 0 0 20px alpha(@neon_cyan, 0.5);
    transform: translateY(0);
}

button.suggested-action {
    background: linear-gradient(135deg, alpha(@neon_cyan, 0.3), alpha(@neon_magenta, 0.2));
    border: 2px solid @neon_cyan;
    color: @neon_cyan;
    box-shadow:
        0 0 20px alpha(@neon_cyan, 0.4),
        inset 0 0 15px alpha(@neon_cyan, 0.1);
    text-shadow: 0 0 8px alpha(@neon_cyan, 0.5);
}

button.suggested-action:hover {
    box-shadow:
        0 0 25px @neon_cyan,
        inset 0 0 20px alpha(@neon_cyan, 0.2);
    transform: translateY(-3px) scale(1.02);
}

button.destructive-action {
    background: linear-gradient(135deg, alpha(@neon_red, 0.3), alpha(@cyber_card, 0.9));
    border: 2px solid @neon_red;
    color: @neon_red;
    box-shadow:
        0 0 20px alpha(@neon_red, 0.4),
        inset 0 0 15px alpha(@neon_red, 0.1);
}

/* === CYBER SCROLLBARS === */
scrollbar {
    background: @cyber_bg;
    border-left: 1px solid alpha(@neon_cyan, 0.2);
}

scrollbar slider {
    background: linear-gradient(180deg, @neon_magenta, @neon_cyan);
    border-radius: 0;
    border: 1px solid alpha(@neon_cyan, 0.3);
    min-width: 10px;
    min-height: 30px;
}

scrollbar slider:hover {
    background: linear-gradient(180deg, @neon_cyan, @neon_magenta);
    box-shadow: 0 0 15px alpha(@neon_cyan, 0.5);
}

/* === CYBER ENTRIES/TEXT INPUTS === */
entry {
    border-radius: 0;
    background: @cyber_card;
    border: 1px solid alpha(@neon_cyan, 0.3);
    color: @neon_cyan;
    caret-color: @neon_cyan;
    box-shadow: inset 0 0 10px alpha(black, 0.5);
}

entry:focus {
    border-color: @neon_cyan;
    box-shadow:
        0 0 15px alpha(@neon_cyan, 0.3),
        inset 0 0 15px alpha(@neon_cyan, 0.1);
}

entry selection {
    background: alpha(@neon_magenta, 0.4);
}

/* === GLITCH EFFECT (optional - can be added to specific elements) === */
@keyframes glitch {
    0%, 100% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
}

/* === SCAN LINE EFFECT === */
@keyframes scan-line {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}
"""


class LinuxArmouryApp(Adw.Application):
    """Main application class"""

    def __init__(self):
        # Prefer Config.APP_ID if available
        app_id = getattr(Config, "APP_ID", "com.github.th3cavalry.linux-armoury")
        super().__init__(application_id=app_id, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.settings = self.load_settings()

        # Track last notification id counter
        self._notify_counter = 0

        # Application-level actions
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda a, p: self.quit())
        self.add_action(quit_action)
        # Global accelerators
        try:
            accel = getattr(Config, "SHORTCUTS", {}).get("quit", "<Control>q")
            self.set_accels_for_action("app.quit", [accel])
        except Exception:
            pass

    def do_startup(self):
        """Called when the application starts"""
        Adw.Application.do_startup(self)

        # Load custom CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CUSTOM_CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Initialize tray icon
        self.tray_icon = None
        if HAS_TRAY_ICON:
            self.tray_icon = create_tray_icon()
            self.tray_icon.on_quit = self.quit

    def do_activate(self):
        """Called when the application is activated"""
        if not self.window:
            self.window = MainWindow(application=self, settings=self.settings)

            # Connect tray icon to window
            if self.tray_icon:
                self.tray_icon.window = self.window
                self.tray_icon.on_show_window = self._show_window

            # Only show window if not starting minimized
            if not self.settings.get("start_minimized", False):
                self.window.present()
        else:
            # If window already exists, just present it
            self.window.present()

    def _show_window(self):
        """Show the main window (called from tray icon)"""
        if self.window:
            self.window.set_visible(True)
            self.window.present()

    def show_tray_notification(self, title: str, body: str):
        """Show a notification from the tray"""
        # This is optional - just update the tray tooltip
        if self.tray_icon:
            self.tray_icon.set_title(f"{title} - {body}")

    def load_settings(self):
        """Load application settings from file"""
        os.makedirs(CONFIG_DIR, exist_ok=True)

        default_settings = {
            "theme": "auto",  # auto, light, dark
            "autostart": False,
            "minimize_to_tray": True,
            "current_power_profile": "balanced",
            "current_refresh_rate": "balanced",
            "auto_profile_switch": False,
            "custom_profiles": [],  # User-defined custom profiles
        }

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")

        return default_settings

    def save_settings(self):
        """Save application settings to file"""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def notify(self, title: str, body: str, priority: str = "normal"):
        """Send a desktop notification via Gio.Notification."""
        try:
            n = Gio.Notification.new(title)
            n.set_body(body)
            pr_map = {
                "low": Gio.NotificationPriority.LOW,
                "normal": Gio.NotificationPriority.NORMAL,
                "high": Gio.NotificationPriority.HIGH,
                "urgent": Gio.NotificationPriority.URGENT,
            }
            n.set_priority(pr_map.get(priority, Gio.NotificationPriority.NORMAL))
            # Unique id per notification
            self._notify_counter += 1
            self.send_notification(f"linux-armoury-{self._notify_counter}", n)
        except Exception as e:
            # Notifications are optional; log and continue
            print(f"Notification error: {e}")


class MainWindow(Adw.ApplicationWindow):
    """Main application window with modern sidebar navigation"""

    # Navigation sections
    SECTIONS = [
        ("dashboard", "Dashboard", "go-home-symbolic"),
        ("monitor", "Monitor", "utilities-system-monitor-symbolic"),
        ("performance", "Performance", "speedometer-symbolic"),
        ("gpu", "GPU", "video-display-symbolic"),
        ("display", "Display", "preferences-desktop-display-symbolic"),
        ("cooling", "Cooling", "fan-symbolic"),
        ("overclocking", "Overclocking", "power-profile-performance-symbolic"),
        ("keyboard", "Keyboard", "input-keyboard-symbolic"),
        ("battery", "Battery", "battery-symbolic"),
        ("automation", "Automation", "system-run-symbolic"),
        ("system", "System Info", "computer-symbolic"),
    ]

    def __init__(self, *args, **kwargs):
        self.settings = kwargs.pop("settings", {})
        super().__init__(*args, **kwargs)

        self.set_title("Linux Armoury")
        self.set_default_size(1000, 700)

        # Track last AC state for auto-profile switching
        self.last_ac_state = None

        # Store references to dynamic widgets
        self.status_widgets = {}
        self.profile_widgets = {}

        # Apply theme
        self.apply_theme(self.settings.get("theme", "auto"))

        # Build UI
        self.setup_ui()

        # Setup keyboard shortcuts
        self.setup_shortcuts()

        # Load current status
        self.refresh_status()

        # Setup periodic monitoring (every 2 seconds)
        monitor_interval = getattr(Config, "MONITOR_INTERVAL", 2000)
        GLib.timeout_add(monitor_interval, self.refresh_status)

        # Setup close-request handler for minimize to tray
        self.connect("close-request", self.on_close_request)

    def on_close_request(self, window):
        """Handle window close request - always minimize to tray and keep running"""
        # Always hide window instead of closing - keep app running in background
        self.set_visible(False)

        # Show notification that app is still running
        app = self.get_application()
        if hasattr(app, "show_tray_notification"):
            app.show_tray_notification(
                "Linux Armoury", "Running in background. Right-click tray icon to quit."
            )

        # Always return True to prevent window from closing
        return True

    def apply_theme(self, theme):
        """Apply light/dark theme"""
        style_manager = Adw.StyleManager.get_default()
        if theme == "light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif theme == "dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:  # auto
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def setup_ui(self):
        """Build the modern user interface with sidebar navigation"""
        # Toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay()

        # Use OverlaySplitView for collapsible sidebar
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_collapsed(False)
        self.split_view.set_max_sidebar_width(280)
        self.split_view.set_min_sidebar_width(220)

        # Create sidebar
        sidebar = self.create_sidebar()
        self.split_view.set_sidebar(sidebar)

        # Create content area with ViewStack
        self.view_stack = Gtk.Stack()
        self.view_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.view_stack.set_transition_duration(200)

        # Create content pages
        self.create_dashboard_page()
        self.create_monitor_page()
        self.create_performance_page()
        self.create_gpu_page()
        self.create_display_page()
        self.create_cooling_page()
        self.create_overclocking_page()
        self.create_keyboard_page()
        self.create_battery_page()
        self.create_automation_page()
        self.create_system_info_page()

        # Content wrapper with toolbar
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header bar for content area
        header = Adw.HeaderBar()
        header.set_show_start_title_buttons(True)
        header.set_show_end_title_buttons(True)

        # Toggle sidebar button (for mobile/collapsed view)
        sidebar_button = Gtk.Button()
        sidebar_button.set_icon_name("sidebar-show-symbolic")
        sidebar_button.set_tooltip_text("Toggle Sidebar")
        sidebar_button.connect(
            "clicked",
            lambda b: self.split_view.set_show_sidebar(
                not self.split_view.get_show_sidebar()
            ),
        )
        header.pack_start(sidebar_button)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()

        # Theme submenu
        theme_menu = Gio.Menu()
        theme_menu.append("Light Mode", "win.theme-light")
        theme_menu.append("Dark Mode", "win.theme-dark")
        theme_menu.append("System Default", "win.theme-auto")
        menu.append_submenu("Appearance", theme_menu)

        menu.append("Preferences", "win.preferences")
        menu.append("Keyboard Shortcuts", "win.shortcuts")
        menu.append("About Linux Armoury", "win.about")
        menu.append("Quit", "app.quit")

        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)

        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh Status (F5)")
        refresh_button.connect("clicked", lambda b: self.refresh_status())
        header.pack_end(refresh_button)

        content_box.append(header)
        content_box.append(self.view_stack)

        self.split_view.set_content(content_box)

        # Wrap in toast overlay
        self.toast_overlay.set_child(self.split_view)
        self.set_content(self.toast_overlay)

        # Setup actions
        self.setup_actions()

    def create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.add_css_class("sidebar")

        # Sidebar header with app branding
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(16)
        header_box.set_margin_start(16)
        header_box.set_margin_end(16)

        # App icon and title
        icon = Gtk.Image.new_from_icon_name("applications-system-symbolic")
        icon.set_pixel_size(48)
        header_box.append(icon)

        title = Gtk.Label(label="Linux Armoury")
        title.add_css_class("title-2")
        header_box.append(title)

        subtitle = Gtk.Label(label="ROG Control Center")
        subtitle.add_css_class("dim-label")
        header_box.append(subtitle)

        sidebar_box.append(header_box)

        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sidebar_box.append(separator)

        # Navigation list
        self.nav_listbox = Gtk.ListBox()
        self.nav_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.nav_listbox.add_css_class("navigation-sidebar")
        self.nav_listbox.set_margin_top(8)
        self.nav_listbox.set_margin_bottom(8)

        for section_id, section_name, icon_name in self.SECTIONS:
            row = self.create_nav_row(section_id, section_name, icon_name)
            self.nav_listbox.append(row)

        # Select first row
        first_row = self.nav_listbox.get_row_at_index(0)
        if first_row:
            self.nav_listbox.select_row(first_row)

        self.nav_listbox.connect("row-selected", self.on_nav_row_selected)

        # Scrollable navigation
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.nav_listbox)

        sidebar_box.append(scrolled)

        # Bottom status indicator
        status_box = self.create_sidebar_status()
        sidebar_box.append(status_box)

        return sidebar_box

    def create_nav_row(self, section_id, section_name, icon_name):
        """Create a navigation row for the sidebar"""
        row = Gtk.ListBoxRow()
        row.section_id = section_id
        row.set_margin_start(8)
        row.set_margin_end(8)
        row.set_margin_top(2)
        row.set_margin_bottom(2)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)

        icon = Gtk.Image.new_from_icon_name(icon_name)
        box.append(icon)

        label = Gtk.Label(label=section_name)
        label.set_xalign(0)
        label.set_hexpand(True)
        box.append(label)

        row.set_child(box)
        return row

    def create_sidebar_status(self):
        """Create a compact status display at bottom of sidebar"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_bottom(12)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_bottom(8)
        box.append(separator)

        # Quick status indicators
        status_grid = Gtk.Grid()
        status_grid.set_column_spacing(8)
        status_grid.set_row_spacing(4)

        # CPU temp
        cpu_icon = Gtk.Image.new_from_icon_name("cpu-symbolic")
        cpu_icon.set_opacity(0.7)
        status_grid.attach(cpu_icon, 0, 0, 1, 1)
        self.sidebar_cpu_label = Gtk.Label(label="--°C")
        self.sidebar_cpu_label.set_xalign(0)
        self.sidebar_cpu_label.add_css_class("caption")
        status_grid.attach(self.sidebar_cpu_label, 1, 0, 1, 1)

        # Battery
        battery_icon = Gtk.Image.new_from_icon_name("battery-symbolic")
        battery_icon.set_opacity(0.7)
        status_grid.attach(battery_icon, 2, 0, 1, 1)
        self.sidebar_battery_label = Gtk.Label(label="--%")
        self.sidebar_battery_label.set_xalign(0)
        self.sidebar_battery_label.add_css_class("caption")
        status_grid.attach(self.sidebar_battery_label, 3, 0, 1, 1)

        # Profile indicator
        profile_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic")
        profile_icon.set_opacity(0.7)
        status_grid.attach(profile_icon, 0, 1, 1, 1)
        self.sidebar_profile_label = Gtk.Label(label="Balanced")
        self.sidebar_profile_label.set_xalign(0)
        self.sidebar_profile_label.add_css_class("caption")
        status_grid.attach(self.sidebar_profile_label, 1, 1, 3, 1)

        box.append(status_grid)
        return box

    def on_nav_row_selected(self, listbox, row):
        """Handle navigation row selection"""
        if row:
            self.view_stack.set_visible_child_name(row.section_id)

    def create_dashboard_page(self):
        """Create the dashboard/home page with system overview"""
        page = Adw.PreferencesPage()
        page.set_title("Dashboard")
        page.set_icon_name("go-home-symbolic")

        # System overview group
        overview_group = Adw.PreferencesGroup()
        overview_group.set_title("System Overview")
        overview_group.set_description("Quick view of your system status")

        # Current power profile
        self.dash_power_row = Adw.ActionRow()
        self.dash_power_row.set_title("Power Profile")
        self.dash_power_row.set_subtitle("Loading...")
        power_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic")
        self.dash_power_row.add_prefix(power_icon)
        overview_group.add(self.dash_power_row)

        # Current refresh rate
        self.dash_refresh_row = Adw.ActionRow()
        self.dash_refresh_row.set_title("Display Refresh Rate")
        self.dash_refresh_row.set_subtitle("Loading...")
        display_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        self.dash_refresh_row.add_prefix(display_icon)
        overview_group.add(self.dash_refresh_row)

        # TDP status
        self.dash_tdp_row = Adw.ActionRow()
        self.dash_tdp_row.set_title("TDP")
        self.dash_tdp_row.set_subtitle("Loading...")
        tdp_icon = Gtk.Image.new_from_icon_name("power-profile-performance-symbolic")
        self.dash_tdp_row.add_prefix(tdp_icon)
        overview_group.add(self.dash_tdp_row)

        page.add(overview_group)

        # Temperatures group
        temp_group = Adw.PreferencesGroup()
        temp_group.set_title("Temperatures")

        # CPU temperature with progress bar
        cpu_row = Adw.ActionRow()
        cpu_row.set_title("CPU Temperature")
        cpu_icon = Gtk.Image.new_from_icon_name("cpu-symbolic")
        cpu_row.add_prefix(cpu_icon)

        cpu_temp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        cpu_temp_box.set_valign(Gtk.Align.CENTER)
        self.dash_cpu_temp_label = Gtk.Label(label="--°C")
        self.dash_cpu_temp_label.add_css_class("title-4")
        cpu_temp_box.append(self.dash_cpu_temp_label)
        self.dash_cpu_temp_bar = Gtk.ProgressBar()
        self.dash_cpu_temp_bar.set_size_request(120, -1)
        cpu_temp_box.append(self.dash_cpu_temp_bar)
        cpu_row.add_suffix(cpu_temp_box)
        temp_group.add(cpu_row)

        # GPU temperature with progress bar
        gpu_row = Adw.ActionRow()
        gpu_row.set_title("GPU Temperature")
        gpu_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        gpu_row.add_prefix(gpu_icon)

        gpu_temp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        gpu_temp_box.set_valign(Gtk.Align.CENTER)
        self.dash_gpu_temp_label = Gtk.Label(label="--°C")
        self.dash_gpu_temp_label.add_css_class("title-4")
        gpu_temp_box.append(self.dash_gpu_temp_label)
        self.dash_gpu_temp_bar = Gtk.ProgressBar()
        self.dash_gpu_temp_bar.set_size_request(120, -1)
        gpu_temp_box.append(self.dash_gpu_temp_bar)
        gpu_row.add_suffix(gpu_temp_box)
        temp_group.add(gpu_row)

        page.add(temp_group)

        # Power source group
        power_group = Adw.PreferencesGroup()
        power_group.set_title("Power")

        # Battery row with level bar
        battery_row = Adw.ActionRow()
        battery_row.set_title("Battery")
        self.dash_battery_icon = Gtk.Image.new_from_icon_name("battery-symbolic")
        battery_row.add_prefix(self.dash_battery_icon)

        battery_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        battery_box.set_valign(Gtk.Align.CENTER)
        self.dash_battery_label = Gtk.Label(label="--%")
        self.dash_battery_label.add_css_class("title-4")
        battery_box.append(self.dash_battery_label)
        self.dash_battery_bar = Gtk.LevelBar()
        self.dash_battery_bar.set_min_value(0)
        self.dash_battery_bar.set_max_value(100)
        self.dash_battery_bar.set_size_request(120, -1)
        battery_box.append(self.dash_battery_bar)
        battery_row.add_suffix(battery_box)
        power_group.add(battery_row)

        # Power source
        self.dash_power_source_row = Adw.ActionRow()
        self.dash_power_source_row.set_title("Power Source")
        self.dash_power_source_row.set_subtitle("Checking...")
        source_icon = Gtk.Image.new_from_icon_name("ac-adapter-symbolic")
        self.dash_power_source_row.add_prefix(source_icon)
        power_group.add(self.dash_power_source_row)

        page.add(power_group)

        # Session Statistics group (if available)
        if HAS_SESSION_STATS:
            stats_group = Adw.PreferencesGroup()
            stats_group.set_title("Session Statistics")
            stats_group.set_description("Current session tracking")

            # Session duration
            duration_row = Adw.ActionRow()
            duration_row.set_title("Session Duration")
            duration_icon = Gtk.Image.new_from_icon_name(
                "preferences-system-time-symbolic"
            )
            duration_row.add_prefix(duration_icon)
            self.stats_duration_label = Gtk.Label(label="0m")
            self.stats_duration_label.add_css_class("title-4")
            duration_row.add_suffix(self.stats_duration_label)
            stats_group.add(duration_row)

            # Max CPU temp
            max_cpu_row = Adw.ActionRow()
            max_cpu_row.set_title("Peak CPU Temperature")
            max_icon = Gtk.Image.new_from_icon_name("temperature-symbolic")
            max_cpu_row.add_prefix(max_icon)
            self.stats_max_cpu_label = Gtk.Label(label="--°C")
            self.stats_max_cpu_label.add_css_class("title-4")
            max_cpu_row.add_suffix(self.stats_max_cpu_label)
            stats_group.add(max_cpu_row)

            # Average CPU temp
            avg_cpu_row = Adw.ActionRow()
            avg_cpu_row.set_title("Average CPU Temperature")
            avg_icon = Gtk.Image.new_from_icon_name("view-continuous-symbolic")
            avg_cpu_row.add_prefix(avg_icon)
            self.stats_avg_cpu_label = Gtk.Label(label="--°C")
            self.stats_avg_cpu_label.add_css_class("title-4")
            avg_cpu_row.add_suffix(self.stats_avg_cpu_label)
            stats_group.add(avg_cpu_row)

            # View details button
            details_row = Adw.ActionRow()
            details_row.set_title("Session Details")
            details_row.set_subtitle("View full session statistics")
            details_icon = Gtk.Image.new_from_icon_name("view-reveal-symbolic")
            details_row.add_prefix(details_icon)

            details_btn = Gtk.Button(label="View")
            details_btn.set_valign(Gtk.Align.CENTER)
            details_btn.connect("clicked", self.show_session_details)
            details_row.add_suffix(details_btn)
            details_row.set_activatable_widget(details_btn)
            stats_group.add(details_row)

            page.add(stats_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "dashboard")

    def setup_shortcuts(self):
        """Add a few useful keyboard shortcuts (Ctrl+Q, F5)."""
        try:
            controller = Gtk.ShortcutController()
            controller.set_scope(Gtk.ShortcutScope.MANAGED)
            # Quit with Ctrl+Q
            controller.add_shortcut(
                Gtk.Shortcut.new(
                    Gtk.ShortcutTrigger.parse_string("<Control>q"),
                    Gtk.CallbackAction.new(lambda *_: self.get_application().quit()),
                )
            )
            # Refresh status with F5
            controller.add_shortcut(
                Gtk.Shortcut.new(
                    Gtk.ShortcutTrigger.parse_string("F5"),
                    Gtk.CallbackAction.new(lambda *_: self.refresh_status()),
                )
            )
            self.add_controller(controller)
        except Exception as e:
            print(f"Shortcut setup failed: {e}")

    def create_monitor_page(self):
        """Create the comprehensive system monitoring page"""
        page = Adw.PreferencesPage()
        page.set_title("System Monitor")
        page.set_icon_name("utilities-system-monitor-symbolic")

        # Initialize system monitor
        if HAS_SYSTEM_MONITOR:
            self.sys_monitor = get_monitor()
        else:
            self.sys_monitor = None

        if not self.sys_monitor:
            # Show error if module not available
            error_group = Adw.PreferencesGroup()
            error_group.set_title("System Monitor")
            error_row = Adw.ActionRow()
            error_row.set_title("Module Not Available")
            error_row.set_subtitle("Install system_monitor.py to enable this feature")
            warn_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            error_row.add_prefix(warn_icon)
            error_group.add(error_row)
            page.add(error_group)

            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            scrolled.set_child(page)
            self.view_stack.add_named(scrolled, "monitor")
            return

        # === System Overview Group ===
        overview_group = Adw.PreferencesGroup()
        overview_group.set_title("System Overview")

        overview = self.sys_monitor.get_system_overview()

        # Hostname
        host_row = Adw.ActionRow()
        host_row.set_title("Hostname")
        host_row.set_subtitle(overview.hostname)
        host_icon = Gtk.Image.new_from_icon_name("computer-symbolic")
        host_row.add_prefix(host_icon)
        overview_group.add(host_row)

        # OS
        os_row = Adw.ActionRow()
        os_row.set_title("Operating System")
        os_row.set_subtitle(f"{overview.os_name} {overview.os_version}")
        os_icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic")
        os_row.add_prefix(os_icon)
        overview_group.add(os_row)

        # Kernel
        kernel_row = Adw.ActionRow()
        kernel_row.set_title("Kernel")
        kernel_row.set_subtitle(overview.kernel)
        kernel_icon = Gtk.Image.new_from_icon_name("system-run-symbolic")
        kernel_row.add_prefix(kernel_icon)
        overview_group.add(kernel_row)

        # Uptime
        self.mon_uptime_row = Adw.ActionRow()
        self.mon_uptime_row.set_title("Uptime")
        self.mon_uptime_row.set_subtitle(overview.uptime_str)
        uptime_icon = Gtk.Image.new_from_icon_name("preferences-system-time-symbolic")
        self.mon_uptime_row.add_prefix(uptime_icon)
        overview_group.add(self.mon_uptime_row)

        page.add(overview_group)

        # === CPU Group ===
        cpu_group = Adw.PreferencesGroup()
        cpu_group.set_title("CPU")
        cpu_group.set_description("Processor usage and information")

        # CPU Model
        cpu = self.sys_monitor.get_cpu_stats()
        model_row = Adw.ActionRow()
        model_row.set_title("Processor")
        model_row.set_subtitle(cpu.model_name)
        model_icon = Gtk.Image.new_from_icon_name("computer-symbolic")
        model_row.add_prefix(model_icon)

        cores_label = Gtk.Label(label=f"{cpu.core_count}C/{cpu.thread_count}T")
        cores_label.add_css_class("info-badge")
        model_row.add_suffix(cores_label)
        cpu_group.add(model_row)

        # CPU Usage with level bar
        self.mon_cpu_usage_row = Adw.ActionRow()
        self.mon_cpu_usage_row.set_title("CPU Usage")
        self.mon_cpu_usage_row.set_subtitle("0%")
        cpu_icon = Gtk.Image.new_from_icon_name("utilities-system-monitor-symbolic")
        self.mon_cpu_usage_row.add_prefix(cpu_icon)

        self.mon_cpu_usage_bar = Gtk.LevelBar()
        self.mon_cpu_usage_bar.set_min_value(0)
        self.mon_cpu_usage_bar.set_max_value(100)
        self.mon_cpu_usage_bar.set_value(0)
        self.mon_cpu_usage_bar.set_size_request(150, 8)
        self.mon_cpu_usage_bar.set_valign(Gtk.Align.CENTER)
        self.mon_cpu_usage_row.add_suffix(self.mon_cpu_usage_bar)
        cpu_group.add(self.mon_cpu_usage_row)

        # CPU Frequency
        self.mon_cpu_freq_row = Adw.ActionRow()
        self.mon_cpu_freq_row.set_title("Frequency")
        self.mon_cpu_freq_row.set_subtitle(f"{cpu.current_freq_mhz:.0f} MHz")
        freq_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic")
        self.mon_cpu_freq_row.add_prefix(freq_icon)

        freq_range_label = Gtk.Label(
            label=f"{cpu.min_freq_mhz:.0f}-{cpu.max_freq_mhz:.0f} MHz"
        )
        freq_range_label.add_css_class("dim-label")
        self.mon_cpu_freq_row.add_suffix(freq_range_label)
        cpu_group.add(self.mon_cpu_freq_row)

        # Load Average
        self.mon_load_row = Adw.ActionRow()
        self.mon_load_row.set_title("Load Average")
        self.mon_load_row.set_subtitle(
            f"{cpu.load_1min:.2f}, {cpu.load_5min:.2f}, {cpu.load_15min:.2f}"
        )
        load_icon = Gtk.Image.new_from_icon_name("view-continuous-symbolic")
        self.mon_load_row.add_prefix(load_icon)
        cpu_group.add(self.mon_load_row)

        # Per-core usage (expander)
        self.mon_cores_expander = Adw.ExpanderRow()
        self.mon_cores_expander.set_title("Per-Core Usage")
        self.mon_cores_expander.set_subtitle("Click to expand")
        cores_icon = Gtk.Image.new_from_icon_name("application-x-firmware-symbolic")
        self.mon_cores_expander.add_prefix(cores_icon)

        self.mon_core_bars = []
        for i in range(cpu.thread_count):
            core_row = Adw.ActionRow()
            core_row.set_title(f"Core {i}")

            core_bar = Gtk.LevelBar()
            core_bar.set_min_value(0)
            core_bar.set_max_value(100)
            core_bar.set_value(0)
            core_bar.set_size_request(120, 6)
            core_bar.set_valign(Gtk.Align.CENTER)
            core_row.add_suffix(core_bar)

            core_label = Gtk.Label(label="0%")
            core_label.set_width_chars(5)
            core_row.add_suffix(core_label)

            self.mon_cores_expander.add_row(core_row)
            self.mon_core_bars.append((core_bar, core_label))

        cpu_group.add(self.mon_cores_expander)
        page.add(cpu_group)

        # === Memory Group ===
        mem_group = Adw.PreferencesGroup()
        mem_group.set_title("Memory")
        mem_group.set_description("RAM and swap usage")

        # RAM Usage
        self.mon_ram_row = Adw.ActionRow()
        self.mon_ram_row.set_title("RAM Usage")
        self.mon_ram_row.set_subtitle("-- / -- MB")
        ram_icon = Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
        self.mon_ram_row.add_prefix(ram_icon)

        self.mon_ram_bar = Gtk.LevelBar()
        self.mon_ram_bar.set_min_value(0)
        self.mon_ram_bar.set_max_value(100)
        self.mon_ram_bar.set_value(0)
        self.mon_ram_bar.set_size_request(150, 8)
        self.mon_ram_bar.set_valign(Gtk.Align.CENTER)
        self.mon_ram_row.add_suffix(self.mon_ram_bar)
        mem_group.add(self.mon_ram_row)

        # Available memory
        self.mon_ram_available_row = Adw.ActionRow()
        self.mon_ram_available_row.set_title("Available")
        self.mon_ram_available_row.set_subtitle("-- MB")
        avail_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        self.mon_ram_available_row.add_prefix(avail_icon)
        mem_group.add(self.mon_ram_available_row)

        # Cached/Buffers
        self.mon_ram_cached_row = Adw.ActionRow()
        self.mon_ram_cached_row.set_title("Cached / Buffers")
        self.mon_ram_cached_row.set_subtitle("-- MB / -- MB")
        cached_icon = Gtk.Image.new_from_icon_name("folder-download-symbolic")
        self.mon_ram_cached_row.add_prefix(cached_icon)
        mem_group.add(self.mon_ram_cached_row)

        # Swap Usage
        self.mon_swap_row = Adw.ActionRow()
        self.mon_swap_row.set_title("Swap Usage")
        self.mon_swap_row.set_subtitle("-- / -- MB")
        swap_icon = Gtk.Image.new_from_icon_name("drive-multidisk-symbolic")
        self.mon_swap_row.add_prefix(swap_icon)

        self.mon_swap_bar = Gtk.LevelBar()
        self.mon_swap_bar.set_min_value(0)
        self.mon_swap_bar.set_max_value(100)
        self.mon_swap_bar.set_value(0)
        self.mon_swap_bar.set_size_request(150, 8)
        self.mon_swap_bar.set_valign(Gtk.Align.CENTER)
        self.mon_swap_row.add_suffix(self.mon_swap_bar)
        mem_group.add(self.mon_swap_row)

        page.add(mem_group)

        # === Disk Group ===
        disk_group = Adw.PreferencesGroup()
        disk_group.set_title("Storage")
        disk_group.set_description("Disk usage and partitions")

        self.mon_disk_rows = []
        disks = self.sys_monitor.get_disk_stats()

        for disk in disks:
            if disk.total_gb < 0.1:  # Skip tiny partitions
                continue

            row = Adw.ActionRow()
            row.set_title(disk.mountpoint)
            row.set_subtitle(
                f"{disk.used_gb:.1f} / {disk.total_gb:.1f} GB ({disk.usage_percent:.1f}%)"
            )

            disk_icon = Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
            row.add_prefix(disk_icon)

            disk_bar = Gtk.LevelBar()
            disk_bar.set_min_value(0)
            disk_bar.set_max_value(100)
            disk_bar.set_value(disk.usage_percent)
            disk_bar.set_size_request(120, 8)
            disk_bar.set_valign(Gtk.Align.CENTER)
            row.add_suffix(disk_bar)

            # Filesystem type badge
            fs_label = Gtk.Label(label=disk.filesystem.upper())
            fs_label.add_css_class("dim-label")
            row.add_suffix(fs_label)

            disk_group.add(row)
            self.mon_disk_rows.append((row, disk_bar, disk.mountpoint))

        page.add(disk_group)

        # === Network Group ===
        net_group = Adw.PreferencesGroup()
        net_group.set_title("Network")
        net_group.set_description("Network interfaces and traffic")

        self.mon_net_rows = {}
        interfaces = self.sys_monitor.get_network_stats()

        for iface in interfaces:
            expander = Adw.ExpanderRow()
            expander.set_title(iface.interface)
            status = "Connected" if iface.is_up else "Disconnected"
            expander.set_subtitle(f"{status} • {iface.ip_address or 'No IP'}")

            if iface.is_up:
                net_icon = Gtk.Image.new_from_icon_name("network-wired-symbolic")
            else:
                net_icon = Gtk.Image.new_from_icon_name("network-offline-symbolic")
            expander.add_prefix(net_icon)

            # Status badge
            status_badge = Gtk.Label(label="UP" if iface.is_up else "DOWN")
            if iface.is_up:
                status_badge.add_css_class("success-badge")
            else:
                status_badge.add_css_class("error-badge")
            expander.add_suffix(status_badge)

            # Download row
            dl_row = Adw.ActionRow()
            dl_row.set_title("Download")
            dl_row.set_subtitle(self.sys_monitor.format_bytes(iface.bytes_recv))
            dl_icon = Gtk.Image.new_from_icon_name("go-down-symbolic")
            dl_row.add_prefix(dl_icon)
            dl_rate_label = Gtk.Label(
                label=self.sys_monitor.format_bytes_rate(iface.recv_rate)
            )
            dl_rate_label.add_css_class("info-badge")
            dl_row.add_suffix(dl_rate_label)
            expander.add_row(dl_row)

            # Upload row
            ul_row = Adw.ActionRow()
            ul_row.set_title("Upload")
            ul_row.set_subtitle(self.sys_monitor.format_bytes(iface.bytes_sent))
            ul_icon = Gtk.Image.new_from_icon_name("go-up-symbolic")
            ul_row.add_prefix(ul_icon)
            ul_rate_label = Gtk.Label(
                label=self.sys_monitor.format_bytes_rate(iface.send_rate)
            )
            ul_rate_label.add_css_class("warning-badge")
            ul_row.add_suffix(ul_rate_label)
            expander.add_row(ul_row)

            # MAC address row
            mac_row = Adw.ActionRow()
            mac_row.set_title("MAC Address")
            mac_row.set_subtitle(iface.mac_address or "Unknown")
            expander.add_row(mac_row)

            net_group.add(expander)
            self.mon_net_rows[iface.interface] = {
                "expander": expander,
                "dl_row": dl_row,
                "ul_row": ul_row,
                "dl_rate": dl_rate_label,
                "ul_rate": ul_rate_label,
                "status_badge": status_badge,
                "icon": net_icon,
            }

        page.add(net_group)

        # === Top Processes Group ===
        proc_group = Adw.PreferencesGroup()
        proc_group.set_title("Top Processes")
        proc_group.set_description("Processes sorted by CPU usage")

        self.mon_proc_rows = []
        processes = self.sys_monitor.get_top_processes(8, "cpu")

        for proc in processes:
            row = Adw.ActionRow()
            row.set_title(proc.name or proc.command[:30])
            row.set_subtitle(f"PID: {proc.pid} • User: {proc.user}")

            proc_icon = Gtk.Image.new_from_icon_name(
                "application-x-executable-symbolic"
            )
            row.add_prefix(proc_icon)

            # CPU usage
            cpu_label = Gtk.Label(label=f"CPU: {proc.cpu_percent:.1f}%")
            if proc.cpu_percent > 50:
                cpu_label.add_css_class("error-badge")
            elif proc.cpu_percent > 20:
                cpu_label.add_css_class("warning-badge")
            else:
                cpu_label.add_css_class("info-badge")
            row.add_suffix(cpu_label)

            # Memory usage
            mem_label = Gtk.Label(label=f"MEM: {proc.mem_percent:.1f}%")
            mem_label.add_css_class("dim-label")
            row.add_suffix(mem_label)

            proc_group.add(row)
            self.mon_proc_rows.append((row, cpu_label, mem_label, proc.pid))

        page.add(proc_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "monitor")

    def create_performance_page(self):
        """Create the performance/power profiles page"""
        page = Adw.PreferencesPage()
        page.set_title("Performance")
        page.set_icon_name("speedometer-symbolic")

        # Track profile rows and buttons for visual indicator updates
        self.power_profile_rows = {}
        self.power_profile_buttons = {}

        # Power profiles group
        profiles_group = Adw.PreferencesGroup()
        profiles_group.set_title("Power Profiles")
        profiles_group.set_description(
            "Select a performance profile to balance power and battery"
        )

        # Power profiles with icons and TDP info
        profiles = [
            (
                "emergency",
                "Emergency",
                "10W @ 30Hz",
                "Critical battery preservation",
                "battery-caution-symbolic",
            ),
            (
                "battery",
                "Battery Saver",
                "18W @ 30Hz",
                "Maximum battery life",
                "battery-full-symbolic",
            ),
            (
                "efficient",
                "Efficient",
                "30W @ 60Hz",
                "Balanced efficiency",
                "battery-good-symbolic",
            ),
            (
                "balanced",
                "Balanced",
                "40W @ 90Hz",
                "Default balanced mode",
                "power-profile-balanced-symbolic",
            ),
            (
                "performance",
                "Performance",
                "55W @ 120Hz",
                "High performance",
                "power-profile-performance-symbolic",
            ),
            (
                "gaming",
                "Gaming",
                "70W @ 180Hz",
                "Gaming optimized",
                "applications-games-symbolic",
            ),
            (
                "maximum",
                "Maximum",
                "90W @ 180Hz",
                "Absolute maximum power",
                "emblem-important-symbolic",
            ),
        ]

        # Detect current profile from system
        detected_profile = SystemUtils.get_current_power_profile()
        if detected_profile:
            profile_map = {
                "low-power": "battery",
                "balanced": "balanced",
                "performance": "performance",
                "quiet": "battery",
            }
            current_profile = profile_map.get(
                detected_profile, self.settings.get("current_power_profile", "balanced")
            )
        else:
            current_profile = self.settings.get("current_power_profile", "balanced")

        for profile_id, title, power_info, description, icon_name in profiles:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(f"{power_info} • {description}")

            # Profile icon
            icon = Gtk.Image.new_from_icon_name(icon_name)
            row.add_prefix(icon)

            # Active checkmark (hidden by default)
            check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            check_icon.add_css_class("success")
            check_icon.set_visible(profile_id == current_profile)
            row.add_prefix(check_icon)

            # Apply button
            button = Gtk.Button()
            button.set_valign(Gtk.Align.CENTER)

            if profile_id == current_profile:
                button.set_label("Active")
                button.add_css_class("suggested-action")
                button.set_sensitive(False)
            else:
                button.set_label("Apply")

            button.connect("clicked", self.on_power_profile_clicked, profile_id)
            row.add_suffix(button)

            self.power_profile_rows[profile_id] = (row, check_icon)
            self.power_profile_buttons[profile_id] = button

            profiles_group.add(row)

        page.add(profiles_group)

        # Current TDP info group
        tdp_group = Adw.PreferencesGroup()
        tdp_group.set_title("Current Settings")

        self.perf_tdp_row = Adw.ActionRow()
        self.perf_tdp_row.set_title("Active TDP")
        self.perf_tdp_row.set_subtitle("Checking...")
        tdp_icon = Gtk.Image.new_from_icon_name("power-profile-performance-symbolic")
        self.perf_tdp_row.add_prefix(tdp_icon)
        tdp_group.add(self.perf_tdp_row)

        page.add(tdp_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "performance")

    def create_gpu_page(self):
        """Create the GPU control and monitoring page"""
        page = Adw.PreferencesPage()
        page.set_title("GPU")
        page.set_icon_name("video-display-symbolic")

        # Initialize GPU controller
        if HAS_GPU_CONTROL:
            self.gpu_controller = get_gpu_controller()
        else:
            self.gpu_controller = None

        # === GPU Detection Group ===
        detect_group = Adw.PreferencesGroup()
        detect_group.set_title("Detected GPUs")
        detect_group.set_description("Graphics processors detected on this system")

        if self.gpu_controller:
            gpus = self.gpu_controller.get_all_gpus()
            if gpus:
                for gpu in gpus:
                    row = Adw.ActionRow()
                    row.set_title(gpu["name"])
                    row.set_subtitle(f"{gpu['vendor']} • {gpu['type'].capitalize()}")

                    # Use generic icon - vendor-specific icons may not be available
                    icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
                    row.add_prefix(icon)

                    # Type badge
                    type_label = Gtk.Label(label=gpu["type"].upper())
                    if gpu["type"] == "discrete":
                        type_label.add_css_class("warning-badge")
                    else:
                        type_label.add_css_class("info-badge")
                    row.add_suffix(type_label)

                    detect_group.add(row)
            else:
                no_gpu_row = Adw.ActionRow()
                no_gpu_row.set_title("No GPUs Detected")
                no_gpu_row.set_subtitle("Could not detect any graphics processors")
                detect_group.add(no_gpu_row)
        else:
            no_module_row = Adw.ActionRow()
            no_module_row.set_title("GPU Control Not Available")
            no_module_row.set_subtitle("Install gpu_control.py to enable GPU features")
            warn_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            no_module_row.add_prefix(warn_icon)
            detect_group.add(no_module_row)

        page.add(detect_group)

        # === GPU Switching Group (supergfxctl) ===
        if self.gpu_controller and self.gpu_controller.supergfxctl_available:
            switch_group = Adw.PreferencesGroup()
            switch_group.set_title("GPU Switching")
            switch_group.set_description(
                "Switch between integrated and discrete graphics"
            )

            status = self.gpu_controller.get_switching_status()

            # Current mode display
            mode_row = Adw.ActionRow()
            mode_row.set_title("Current Mode")
            if status.current_mode:
                mode_row.set_subtitle(status.current_mode.value)
            else:
                mode_row.set_subtitle("Unknown")
            mode_icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic")
            mode_row.add_prefix(mode_icon)
            self.gpu_mode_row = mode_row
            switch_group.add(mode_row)

            # dGPU power status
            power_row = Adw.ActionRow()
            power_row.set_title("dGPU Power Status")
            power_row.set_subtitle(status.power_status.value.capitalize())
            power_icon = Gtk.Image.new_from_icon_name("battery-symbolic")
            power_row.add_prefix(power_icon)

            # Power status badge
            power_badge = Gtk.Label(label=status.power_status.value.upper())
            if status.power_status == GpuPowerStatus.ACTIVE:
                power_badge.add_css_class("warning-badge")
            elif status.power_status == GpuPowerStatus.SUSPENDED:
                power_badge.add_css_class("success-badge")
            elif status.power_status == GpuPowerStatus.OFF:
                power_badge.add_css_class("info-badge")
            else:
                power_badge.add_css_class("dim-label")
            power_row.add_suffix(power_badge)
            self.gpu_power_row = power_row
            self.gpu_power_badge = power_badge
            switch_group.add(power_row)

            # dGPU vendor
            vendor_row = Adw.ActionRow()
            vendor_row.set_title("dGPU Vendor")
            vendor_row.set_subtitle(status.dgpu_vendor)
            vendor_icon = Gtk.Image.new_from_icon_name(
                "applications-multimedia-symbolic"
            )
            vendor_row.add_prefix(vendor_icon)
            switch_group.add(vendor_row)

            # Mode selection
            if status.supported_modes:
                mode_select_row = Adw.ComboRow()
                mode_select_row.set_title("Graphics Mode")
                mode_select_row.set_subtitle("Select which GPU configuration to use")
                select_icon = Gtk.Image.new_from_icon_name(
                    "preferences-system-symbolic"
                )
                mode_select_row.add_prefix(select_icon)

                mode_names = [m.value for m in status.supported_modes]
                mode_model = Gtk.StringList.new(mode_names)
                mode_select_row.set_model(mode_model)

                # Set current selection
                if (
                    status.current_mode
                    and status.current_mode in status.supported_modes
                ):
                    mode_select_row.set_selected(
                        status.supported_modes.index(status.current_mode)
                    )

                mode_select_row.connect("notify::selected", self.on_gpu_mode_changed)
                self.gpu_mode_select_row = mode_select_row
                self.gpu_supported_modes = status.supported_modes
                switch_group.add(mode_select_row)

            # Pending action warning
            if status.pending_action:
                action_row = Adw.ActionRow()
                action_row.set_title("Pending Action Required")
                action_row.set_subtitle(status.pending_action)
                action_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
                action_row.add_prefix(action_icon)
                action_row.add_css_class("warning")
                switch_group.add(action_row)

            page.add(switch_group)
        elif self.gpu_controller and not self.gpu_controller.supergfxctl_available:
            switch_group = Adw.PreferencesGroup()
            switch_group.set_title("GPU Switching")

            install_row = Adw.ActionRow()
            install_row.set_title("supergfxctl Not Installed")
            install_row.set_subtitle("Install supergfxctl for GPU switching support")
            warn_icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
            install_row.add_prefix(warn_icon)

            # Link button
            link_btn = Gtk.LinkButton(uri="https://gitlab.com/asus-linux/supergfxctl")
            link_btn.set_label("Get supergfxctl")
            link_btn.set_valign(Gtk.Align.CENTER)
            install_row.add_suffix(link_btn)

            switch_group.add(install_row)
            page.add(switch_group)

        # === Live GPU Stats Group ===
        stats_group = Adw.PreferencesGroup()
        stats_group.set_title("Live GPU Statistics")
        stats_group.set_description(
            "Real-time GPU monitoring (updates every 2 seconds)"
        )

        # GPU name row
        self.gpu_name_row = Adw.ActionRow()
        self.gpu_name_row.set_title("Active GPU")
        self.gpu_name_row.set_subtitle("Detecting...")
        gpu_name_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        self.gpu_name_row.add_prefix(gpu_name_icon)
        stats_group.add(self.gpu_name_row)

        # GPU clock row
        self.gpu_clock_row = Adw.ActionRow()
        self.gpu_clock_row.set_title("GPU Clock")
        self.gpu_clock_row.set_subtitle("-- MHz")
        clock_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic")
        self.gpu_clock_row.add_prefix(clock_icon)
        stats_group.add(self.gpu_clock_row)

        # Memory clock row
        self.gpu_mem_clock_row = Adw.ActionRow()
        self.gpu_mem_clock_row.set_title("Memory Clock")
        self.gpu_mem_clock_row.set_subtitle("-- MHz")
        mem_clock_icon = Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
        self.gpu_mem_clock_row.add_prefix(mem_clock_icon)
        stats_group.add(self.gpu_mem_clock_row)

        # GPU usage row with level bar
        self.gpu_usage_row = Adw.ActionRow()
        self.gpu_usage_row.set_title("GPU Usage")
        self.gpu_usage_row.set_subtitle("0%")
        usage_icon = Gtk.Image.new_from_icon_name("utilities-system-monitor-symbolic")
        self.gpu_usage_row.add_prefix(usage_icon)

        self.gpu_usage_bar = Gtk.LevelBar()
        self.gpu_usage_bar.set_min_value(0)
        self.gpu_usage_bar.set_max_value(100)
        self.gpu_usage_bar.set_value(0)
        self.gpu_usage_bar.set_size_request(120, 8)
        self.gpu_usage_bar.set_valign(Gtk.Align.CENTER)
        self.gpu_usage_row.add_suffix(self.gpu_usage_bar)
        stats_group.add(self.gpu_usage_row)

        # VRAM usage row with level bar
        self.gpu_vram_row = Adw.ActionRow()
        self.gpu_vram_row.set_title("VRAM Usage")
        self.gpu_vram_row.set_subtitle("-- / -- MB")
        vram_icon = Gtk.Image.new_from_icon_name("drive-multidisk-symbolic")
        self.gpu_vram_row.add_prefix(vram_icon)

        self.gpu_vram_bar = Gtk.LevelBar()
        self.gpu_vram_bar.set_min_value(0)
        self.gpu_vram_bar.set_max_value(100)
        self.gpu_vram_bar.set_value(0)
        self.gpu_vram_bar.set_size_request(120, 8)
        self.gpu_vram_bar.set_valign(Gtk.Align.CENTER)
        self.gpu_vram_row.add_suffix(self.gpu_vram_bar)
        stats_group.add(self.gpu_vram_row)

        # GPU temperature row
        self.gpu_temp_row = Adw.ActionRow()
        self.gpu_temp_row.set_title("GPU Temperature")
        self.gpu_temp_row.set_subtitle("--°C")
        temp_icon = Gtk.Image.new_from_icon_name("sensors-temperature-symbolic")
        self.gpu_temp_row.add_prefix(temp_icon)

        self.gpu_temp_label = Gtk.Label(label="--°C")
        self.gpu_temp_label.add_css_class("temp-cool")
        self.gpu_temp_row.add_suffix(self.gpu_temp_label)
        stats_group.add(self.gpu_temp_row)

        # Power draw row
        self.gpu_power_draw_row = Adw.ActionRow()
        self.gpu_power_draw_row.set_title("Power Draw")
        self.gpu_power_draw_row.set_subtitle("-- W")
        power_draw_icon = Gtk.Image.new_from_icon_name("battery-symbolic")
        self.gpu_power_draw_row.add_prefix(power_draw_icon)
        stats_group.add(self.gpu_power_draw_row)

        # Fan speed row (if available)
        self.gpu_fan_row = Adw.ActionRow()
        self.gpu_fan_row.set_title("GPU Fan")
        self.gpu_fan_row.set_subtitle("-- RPM")
        fan_icon = Gtk.Image.new_from_icon_name("fan-symbolic")
        self.gpu_fan_row.add_prefix(fan_icon)
        stats_group.add(self.gpu_fan_row)

        page.add(stats_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "gpu")

    def on_gpu_mode_changed(self, row, param):
        """Handle GPU mode change"""
        if not hasattr(self, "gpu_supported_modes") or not self.gpu_controller:
            return

        selected_idx = row.get_selected()
        if selected_idx < len(self.gpu_supported_modes):
            new_mode = self.gpu_supported_modes[selected_idx]
            success, message = self.gpu_controller.set_gpu_mode(new_mode)

            if success:
                self.show_toast(message)
                # Update the mode display
                if hasattr(self, "gpu_mode_row"):
                    self.gpu_mode_row.set_subtitle(new_mode.value)
            else:
                self.show_toast(f"Error: {message}")

    def create_display_page(self):
        """Create the display settings page"""
        page = Adw.PreferencesPage()
        page.set_title("Display")
        page.set_icon_name("video-display-symbolic")

        # Track refresh rate rows and buttons
        self.refresh_rate_rows = {}
        self.refresh_rate_buttons = {}

        # Refresh rate group
        refresh_group = Adw.PreferencesGroup()
        refresh_group.set_title("Refresh Rate")
        refresh_group.set_description(
            "Higher refresh rates provide smoother visuals but use more power"
        )

        # Refresh rate profiles with detailed info
        profiles = [
            (
                "30",
                "30 Hz",
                "Battery saving • Best for static content",
                "battery-full-symbolic",
            ),
            ("60", "60 Hz", "Standard • Good balance", "display-symbolic"),
            (
                "90",
                "90 Hz",
                "Smooth • Everyday use",
                "preferences-desktop-display-symbolic",
            ),
            (
                "120",
                "120 Hz",
                "High refresh • Gaming and productivity",
                "video-display-symbolic",
            ),
            (
                "180",
                "180 Hz",
                "Maximum • Competitive gaming",
                "applications-games-symbolic",
            ),
        ]

        # Get current refresh rate
        detected_rate = SystemUtils.get_current_refresh_rate()
        if detected_rate:
            current_rate = str(detected_rate)
        else:
            current_rate = str(self.settings.get("current_refresh_rate", "90"))

        for profile_id, title, description, icon_name in profiles:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(description)

            # Icon
            icon = Gtk.Image.new_from_icon_name(icon_name)
            row.add_prefix(icon)

            # Active checkmark
            check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            check_icon.add_css_class("success")
            check_icon.set_visible(profile_id == current_rate)
            row.add_prefix(check_icon)

            # Apply button
            button = Gtk.Button()
            button.set_valign(Gtk.Align.CENTER)

            if profile_id == current_rate:
                button.set_label("Active")
                button.add_css_class("suggested-action")
                button.set_sensitive(False)
            else:
                button.set_label("Apply")

            button.connect("clicked", self.on_refresh_rate_clicked, profile_id)
            row.add_suffix(button)

            self.refresh_rate_rows[profile_id] = (row, check_icon)
            self.refresh_rate_buttons[profile_id] = button

            refresh_group.add(row)

        page.add(refresh_group)

        # Display info group
        info_group = Adw.PreferencesGroup()
        info_group.set_title("Display Information")

        # Resolution info
        try:
            width, height = SystemUtils.get_display_resolution()
            resolution_text = f"{width}×{height}"
        except:
            resolution_text = "Unknown"

        res_row = Adw.ActionRow()
        res_row.set_title("Resolution")
        res_row.set_subtitle(resolution_text)
        res_icon = Gtk.Image.new_from_icon_name("preferences-desktop-display-symbolic")
        res_row.add_prefix(res_icon)
        info_group.add(res_row)

        # Display name
        display_row = Adw.ActionRow()
        display_row.set_title("Display")
        display_row.set_subtitle(SystemUtils.get_primary_display())
        disp_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        display_row.add_prefix(disp_icon)
        info_group.add(display_row)

        page.add(info_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "display")

    def create_cooling_page(self):
        """Create the cooling/fan control page"""
        page = Adw.PreferencesPage()
        page.set_title("Cooling")
        page.set_icon_name("fan-symbolic")

        # Temperature monitoring group
        temp_group = Adw.PreferencesGroup()
        temp_group.set_title("Temperatures")
        temp_group.set_description("Real-time temperature monitoring")

        # CPU temperature with visual indicator
        cpu_row = Adw.ActionRow()
        cpu_row.set_title("CPU Temperature")
        cpu_icon = Gtk.Image.new_from_icon_name("cpu-symbolic")
        cpu_row.add_prefix(cpu_icon)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        cpu_box.set_valign(Gtk.Align.CENTER)
        self.cool_cpu_temp_label = Gtk.Label(label="--°C")
        self.cool_cpu_temp_label.add_css_class("title-3")
        cpu_box.append(self.cool_cpu_temp_label)
        self.cool_cpu_temp_bar = Gtk.ProgressBar()
        self.cool_cpu_temp_bar.set_size_request(100, -1)
        self.cool_cpu_temp_bar.set_valign(Gtk.Align.CENTER)
        cpu_box.append(self.cool_cpu_temp_bar)
        cpu_row.add_suffix(cpu_box)
        temp_group.add(cpu_row)

        # GPU temperature
        gpu_row = Adw.ActionRow()
        gpu_row.set_title("GPU Temperature")
        gpu_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        gpu_row.add_prefix(gpu_icon)

        gpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        gpu_box.set_valign(Gtk.Align.CENTER)
        self.cool_gpu_temp_label = Gtk.Label(label="--°C")
        self.cool_gpu_temp_label.add_css_class("title-3")
        gpu_box.append(self.cool_gpu_temp_label)
        self.cool_gpu_temp_bar = Gtk.ProgressBar()
        self.cool_gpu_temp_bar.set_size_request(100, -1)
        self.cool_gpu_temp_bar.set_valign(Gtk.Align.CENTER)
        gpu_box.append(self.cool_gpu_temp_bar)
        gpu_row.add_suffix(gpu_box)
        temp_group.add(gpu_row)

        page.add(temp_group)

        # Fan control group (if supported)
        if HAS_FAN_CONTROL:
            try:
                fan = get_fan_controller()
                if fan.is_supported():
                    fan_group = Adw.PreferencesGroup()
                    fan_group.set_title("Fan Speed")
                    fan_group.set_description("Current fan status")

                    # Fan speed rows
                    self.fan_speed_rows = []
                    fans = fan.get_all_fan_speeds()
                    for i, fan_status in enumerate(fans):
                        fan_row = Adw.ActionRow()
                        fan_row.set_title(fan_status.name)
                        fan_icon = Gtk.Image.new_from_icon_name("fan-symbolic")
                        fan_row.add_prefix(fan_icon)

                        speed_label = Gtk.Label(label=f"{fan_status.rpm} RPM")
                        speed_label.add_css_class("title-4")
                        speed_label.add_css_class("fan-indicator")
                        fan_row.add_suffix(speed_label)

                        self.fan_speed_rows.append((fan_row, speed_label))
                        fan_group.add(fan_row)

                    page.add(fan_group)

                    # Fan curve control (if supported)
                    if fan.has_fan_curves():
                        curve_group = Adw.PreferencesGroup()
                        curve_group.set_title("Fan Curve")

                        curve_row = Adw.ActionRow()
                        curve_row.set_title("Custom Fan Curve")
                        curve_row.set_subtitle("Enable custom fan speed control")
                        curve_icon = Gtk.Image.new_from_icon_name(
                            "utilities-tweak-tool-symbolic"
                        )
                        curve_row.add_prefix(curve_icon)

                        self.fan_curve_switch = Gtk.Switch()
                        self.fan_curve_switch.set_valign(Gtk.Align.CENTER)
                        self.fan_curve_switch.connect(
                            "state-set", self.on_fan_curve_toggled
                        )
                        curve_row.add_suffix(self.fan_curve_switch)
                        curve_group.add(curve_row)

                        # Add Edit Fan Curve button with visual editor
                        if HAS_FAN_CURVE_EDITOR:
                            edit_row = Adw.ActionRow()
                            edit_row.set_title("Edit Fan Curve")
                            edit_row.set_subtitle(
                                "Visually customize your fan response curve"
                            )
                            edit_icon = Gtk.Image.new_from_icon_name(
                                "document-edit-symbolic"
                            )
                            edit_row.add_prefix(edit_icon)

                            edit_btn = Gtk.Button(label="Open Editor")
                            edit_btn.add_css_class("suggested-action")
                            edit_btn.set_valign(Gtk.Align.CENTER)
                            edit_btn.connect("clicked", self.on_open_fan_curve_editor)
                            edit_row.add_suffix(edit_btn)
                            edit_row.set_activatable_widget(edit_btn)
                            curve_group.add(edit_row)

                        page.add(curve_group)
            except Exception as e:
                print(f"Fan control setup failed: {e}")

        # Even without fan control, show a basic visual fan curve preview if editor is available
        if HAS_FAN_CURVE_EDITOR and not HAS_FAN_CONTROL:
            curve_preview_group = Adw.PreferencesGroup()
            curve_preview_group.set_title("Fan Curve Preview")
            curve_preview_group.set_description(
                "Visual fan curve editor (requires asusd for application)"
            )

            # Add mini fan curve widget
            curve_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            curve_box.set_margin_top(8)
            curve_box.set_margin_bottom(8)

            self.preview_curve_widget = FanCurveWidget()
            self.preview_curve_widget.set_size_request(320, 200)
            curve_box.append(self.preview_curve_widget)

            edit_btn = Gtk.Button(label="Open Full Editor")
            edit_btn.add_css_class("suggested-action")
            edit_btn.set_halign(Gtk.Align.CENTER)
            edit_btn.connect("clicked", self.on_open_fan_curve_editor)
            curve_box.append(edit_btn)

            # Wrap in a row
            preview_row = Adw.PreferencesRow()
            preview_row.set_child(curve_box)
            curve_preview_group.add(preview_row)

            page.add(curve_preview_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "cooling")

    def create_overclocking_page(self):
        """Create the CPU/GPU overclocking page"""
        page = Adw.PreferencesPage()
        page.set_title("Overclocking")
        page.set_icon_name("power-profile-performance-symbolic")

        if not HAS_OVERCLOCKING:
            # Show placeholder if module not available
            group = Adw.PreferencesGroup()
            group.set_title("Overclocking")
            group.set_description("Overclocking module not available")

            info_row = Adw.ActionRow()
            info_row.set_title("Module Not Found")
            info_row.set_subtitle(
                "Install overclocking_control.py to enable this feature"
            )
            warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            info_row.add_prefix(warning_icon)
            group.add(info_row)
            page.add(group)

            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            scrolled.set_child(page)
            self.view_stack.add_named(scrolled, "overclocking")
            return

        # Initialize overclocking controller
        self.oc_controller = OverclockingController()

        # === CPU Section ===
        cpu_group = Adw.PreferencesGroup()
        cpu_group.set_title("⚡ CPU Control")
        cpu_group.set_description("Manage CPU frequency, governor, and turbo boost")

        cpu_info = self.oc_controller.get_cpu_info()

        # CPU Model info
        cpu_model_row = Adw.ActionRow()
        cpu_model_row.set_title("CPU Model")
        cpu_model_row.set_subtitle(cpu_info.model or "Unknown")
        cpu_icon = Gtk.Image.new_from_icon_name("cpu-symbolic")
        cpu_model_row.add_prefix(cpu_icon)

        # Add cores/threads badge
        cores_label = Gtk.Label(label=f"{cpu_info.cores}C/{cpu_info.threads}T")
        cores_label.add_css_class("info-badge")
        cpu_model_row.add_suffix(cores_label)
        cpu_group.add(cpu_model_row)

        # Current frequency display
        self.oc_cpu_freq_row = Adw.ActionRow()
        self.oc_cpu_freq_row.set_title("Current Frequency")
        self.oc_cpu_freq_row.set_subtitle(
            f"{cpu_info.current_freq_mhz:.0f} MHz (max: {cpu_info.max_freq_mhz:.0f} MHz)"
        )
        freq_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic")
        self.oc_cpu_freq_row.add_prefix(freq_icon)
        cpu_group.add(self.oc_cpu_freq_row)

        # CPU Governor selection
        gov_row = Adw.ComboRow()
        gov_row.set_title("CPU Governor")
        gov_row.set_subtitle("Controls how the CPU scales frequency")
        gov_icon = Gtk.Image.new_from_icon_name("system-run-symbolic")
        gov_row.add_prefix(gov_icon)

        governors = self.oc_controller.get_available_governors()
        if governors:
            gov_model = Gtk.StringList.new(governors)
            gov_row.set_model(gov_model)

            # Set current governor
            if cpu_info.governor in governors:
                gov_row.set_selected(governors.index(cpu_info.governor))

            gov_row.connect("notify::selected", self.on_cpu_governor_changed)

        cpu_group.add(gov_row)
        self.oc_governor_row = gov_row

        # Turbo Boost toggle
        turbo_row = Adw.SwitchRow()
        turbo_row.set_title("Turbo Boost")
        turbo_row.set_subtitle(
            "Allow CPU to exceed base frequency when thermal headroom permits"
        )
        turbo_icon = Gtk.Image.new_from_icon_name("power-profile-performance-symbolic")
        turbo_row.add_prefix(turbo_icon)
        turbo_row.set_active(cpu_info.turbo_enabled)
        turbo_row.connect("notify::active", self.on_turbo_boost_changed)
        cpu_group.add(turbo_row)
        self.oc_turbo_row = turbo_row

        # Energy Performance Preference
        epp_prefs = self.oc_controller.get_available_energy_preferences()
        if epp_prefs:
            epp_row = Adw.ComboRow()
            epp_row.set_title("Energy Performance Preference")
            epp_row.set_subtitle("Balance between power saving and performance")
            epp_icon = Gtk.Image.new_from_icon_name("battery-symbolic")
            epp_row.add_prefix(epp_icon)

            epp_model = Gtk.StringList.new(epp_prefs)
            epp_row.set_model(epp_model)

            current_epp = self.oc_controller.get_energy_performance_preference()
            if current_epp and current_epp in epp_prefs:
                epp_row.set_selected(epp_prefs.index(current_epp))

            epp_row.connect("notify::selected", self.on_epp_changed)
            cpu_group.add(epp_row)
            self.oc_epp_row = epp_row

        page.add(cpu_group)

        # === RyzenAdj TDP Section (if available) ===
        if self.oc_controller.ryzenadj_available:
            tdp_group = Adw.PreferencesGroup()
            tdp_group.set_title("🔥 TDP Control (RyzenAdj)")
            tdp_group.set_description("Adjust power limits for AMD Ryzen APUs")

            # TDP Preset buttons
            preset_row = Adw.PreferencesRow()
            preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            preset_box.set_margin_top(16)
            preset_box.set_margin_bottom(16)
            preset_box.set_margin_start(16)
            preset_box.set_margin_end(16)
            preset_box.set_halign(Gtk.Align.CENTER)

            preset_colors = {
                "silent": "power-profile-power-saver-symbolic",
                "balanced": "power-profile-balanced-symbolic",
                "performance": "power-profile-performance-symbolic",
                "turbo": "emblem-system-symbolic",
            }

            for preset_name, preset_values in TDP_PRESETS.items():
                btn = Gtk.Button()
                btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                btn_icon = Gtk.Image.new_from_icon_name(
                    preset_colors.get(preset_name, "power-profile-balanced-symbolic")
                )
                btn_label = Gtk.Label(label=preset_name.title())
                btn_box.append(btn_icon)
                btn_box.append(btn_label)
                btn.set_child(btn_box)
                btn.add_css_class("pill")
                btn.set_tooltip_text(
                    f"STAPM: {preset_values['stapm']}W, Fast: {preset_values['fast']}W, Slow: {preset_values['slow']}W"
                )
                btn.connect("clicked", self.on_tdp_preset_clicked, preset_name)
                preset_box.append(btn)

            preset_row.set_child(preset_box)
            tdp_group.add(preset_row)

            # STAPM Limit slider
            stapm_row = Adw.ActionRow()
            stapm_row.set_title("STAPM Limit")
            stapm_row.set_subtitle("Sustained power limit (Watts)")
            stapm_icon = Gtk.Image.new_from_icon_name("power-profile-balanced-symbolic")
            stapm_row.add_prefix(stapm_icon)

            self.stapm_scale = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, 5, 65, 1
            )
            self.stapm_scale.set_hexpand(True)
            self.stapm_scale.set_size_request(200, -1)
            self.stapm_scale.set_value(25)
            self.stapm_scale.set_draw_value(True)
            self.stapm_scale.set_value_pos(Gtk.PositionType.RIGHT)
            stapm_row.add_suffix(self.stapm_scale)
            tdp_group.add(stapm_row)

            # Fast Limit slider
            fast_row = Adw.ActionRow()
            fast_row.set_title("Fast Limit")
            fast_row.set_subtitle("Short boost power limit (Watts)")
            fast_icon = Gtk.Image.new_from_icon_name(
                "power-profile-performance-symbolic"
            )
            fast_row.add_prefix(fast_icon)

            self.fast_scale = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, 5, 80, 1
            )
            self.fast_scale.set_hexpand(True)
            self.fast_scale.set_size_request(200, -1)
            self.fast_scale.set_value(35)
            self.fast_scale.set_draw_value(True)
            self.fast_scale.set_value_pos(Gtk.PositionType.RIGHT)
            fast_row.add_suffix(self.fast_scale)
            tdp_group.add(fast_row)

            # Slow Limit slider
            slow_row = Adw.ActionRow()
            slow_row.set_title("Slow Limit")
            slow_row.set_subtitle("Sustained thermal limit (Watts)")
            slow_icon = Gtk.Image.new_from_icon_name(
                "power-profile-power-saver-symbolic"
            )
            slow_row.add_prefix(slow_icon)

            self.slow_scale = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, 5, 65, 1
            )
            self.slow_scale.set_hexpand(True)
            self.slow_scale.set_size_request(200, -1)
            self.slow_scale.set_value(25)
            self.slow_scale.set_draw_value(True)
            self.slow_scale.set_value_pos(Gtk.PositionType.RIGHT)
            slow_row.add_suffix(self.slow_scale)
            tdp_group.add(slow_row)

            # Temperature Limit slider
            temp_row = Adw.ActionRow()
            temp_row.set_title("Temperature Limit")
            temp_row.set_subtitle("Maximum CPU temperature (°C)")
            temp_icon = Gtk.Image.new_from_icon_name("sensors-temperature-symbolic")
            temp_row.add_prefix(temp_icon)

            self.temp_limit_scale = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, 70, 105, 1
            )
            self.temp_limit_scale.set_hexpand(True)
            self.temp_limit_scale.set_size_request(200, -1)
            self.temp_limit_scale.set_value(95)
            self.temp_limit_scale.set_draw_value(True)
            self.temp_limit_scale.set_value_pos(Gtk.PositionType.RIGHT)
            temp_row.add_suffix(self.temp_limit_scale)
            tdp_group.add(temp_row)

            # Apply TDP button
            apply_tdp_row = Adw.ActionRow()
            apply_tdp_row.set_title("Apply TDP Settings")
            apply_tdp_row.set_subtitle("Apply the configured power limits")

            apply_btn = Gtk.Button(label="Apply")
            apply_btn.add_css_class("suggested-action")
            apply_btn.set_valign(Gtk.Align.CENTER)
            apply_btn.connect("clicked", self.on_apply_tdp_clicked)
            apply_tdp_row.add_suffix(apply_btn)
            tdp_group.add(apply_tdp_row)

            page.add(tdp_group)

        # === AMD GPU Section (if available) ===
        if self.oc_controller.amd_gpu_path:
            gpu_group = Adw.PreferencesGroup()
            gpu_group.set_title("🎮 AMD GPU Control")
            gpu_group.set_description("Manage GPU performance and power profiles")

            gpu_info = self.oc_controller.get_amd_gpu_info()

            if gpu_info:
                # GPU info row
                gpu_info_row = Adw.ActionRow()
                gpu_info_row.set_title("GPU")
                gpu_info_row.set_subtitle(gpu_info.name or "AMD GPU")
                gpu_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
                gpu_info_row.add_prefix(gpu_icon)

                if gpu_info.vram_mb:
                    vram_label = Gtk.Label(label=f"{gpu_info.vram_mb} MB VRAM")
                    vram_label.add_css_class("info-badge")
                    gpu_info_row.add_suffix(vram_label)
                gpu_group.add(gpu_info_row)

                # GPU clock and temp display
                self.oc_gpu_status_row = Adw.ActionRow()
                self.oc_gpu_status_row.set_title("GPU Status")
                self.oc_gpu_status_row.set_subtitle(
                    f"Clock: {gpu_info.current_gpu_clock_mhz} MHz | Temp: {gpu_info.gpu_temp_c}°C"
                )
                gpu_status_icon = Gtk.Image.new_from_icon_name("speedometer-symbolic")
                self.oc_gpu_status_row.add_prefix(gpu_status_icon)
                gpu_group.add(self.oc_gpu_status_row)

                # Performance Level selection
                perf_row = Adw.ComboRow()
                perf_row.set_title("Performance Level")
                perf_row.set_subtitle("Control GPU power management behavior")
                perf_icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic")
                perf_row.add_prefix(perf_icon)

                perf_levels = [
                    "auto",
                    "low",
                    "high",
                    "manual",
                    "profile_standard",
                    "profile_peak",
                ]
                perf_model = Gtk.StringList.new(perf_levels)
                perf_row.set_model(perf_model)

                if gpu_info.power_level in perf_levels:
                    perf_row.set_selected(perf_levels.index(gpu_info.power_level))

                perf_row.connect("notify::selected", self.on_gpu_perf_level_changed)
                gpu_group.add(perf_row)
                self.oc_gpu_perf_row = perf_row

                # Power Profile selection
                profiles = self.oc_controller.get_gpu_power_profiles()
                if profiles:
                    profile_row = Adw.ComboRow()
                    profile_row.set_title("Power Profile Mode")
                    profile_row.set_subtitle(
                        "Optimized settings for different workloads"
                    )
                    profile_icon = Gtk.Image.new_from_icon_name(
                        "applications-games-symbolic"
                    )
                    profile_row.add_prefix(profile_icon)

                    profile_names = [p[1] for p in profiles]
                    profile_model = Gtk.StringList.new(profile_names)
                    profile_row.set_model(profile_model)

                    # Find active profile
                    for i, (idx, name, is_active) in enumerate(profiles):
                        if is_active:
                            profile_row.set_selected(i)
                            break

                    profile_row.connect(
                        "notify::selected", self.on_gpu_power_profile_changed
                    )
                    gpu_group.add(profile_row)
                    self.oc_gpu_profile_row = profile_row
                    self.oc_gpu_profiles = profiles

                # Reset GPU clocks button
                reset_row = Adw.ActionRow()
                reset_row.set_title("Reset GPU Clocks")
                reset_row.set_subtitle("Reset GPU to default clock settings")

                reset_btn = Gtk.Button(label="Reset")
                reset_btn.add_css_class("destructive-action")
                reset_btn.set_valign(Gtk.Align.CENTER)
                reset_btn.connect("clicked", self.on_reset_gpu_clicked)
                reset_row.add_suffix(reset_btn)
                gpu_group.add(reset_row)

            page.add(gpu_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "overclocking")

    # === Overclocking Event Handlers ===

    def on_cpu_governor_changed(self, combo_row, _):
        """Handle CPU governor change"""
        if not HAS_OVERCLOCKING:
            return
        selected = combo_row.get_selected()
        governors = self.oc_controller.get_available_governors()
        if selected < len(governors):
            governor = governors[selected]
            if self.oc_controller.set_cpu_governor(governor):
                self.show_toast(f"CPU governor set to {governor}")
            else:
                self.show_toast("Failed to set CPU governor")

    def on_turbo_boost_changed(self, switch_row, _):
        """Handle turbo boost toggle"""
        if not HAS_OVERCLOCKING:
            return
        enabled = switch_row.get_active()
        if self.oc_controller.set_turbo_boost(enabled):
            self.show_toast(f"Turbo Boost {'enabled' if enabled else 'disabled'}")
        else:
            self.show_toast("Failed to change Turbo Boost setting")

    def on_epp_changed(self, combo_row, _):
        """Handle Energy Performance Preference change"""
        if not HAS_OVERCLOCKING:
            return
        selected = combo_row.get_selected()
        epp_prefs = self.oc_controller.get_available_energy_preferences()
        if selected < len(epp_prefs):
            pref = epp_prefs[selected]
            if self.oc_controller.set_energy_performance_preference(pref):
                self.show_toast(f"Energy preference set to {pref}")
            else:
                self.show_toast("Failed to set energy preference")

    def on_tdp_preset_clicked(self, button, preset_name):
        """Handle TDP preset button click"""
        if not HAS_OVERCLOCKING or preset_name not in TDP_PRESETS:
            return

        preset = TDP_PRESETS[preset_name]
        self.stapm_scale.set_value(preset["stapm"])
        self.fast_scale.set_value(preset["fast"])
        self.slow_scale.set_value(preset["slow"])

        # Apply immediately
        if self.oc_controller.set_ryzenadj_tdp(
            stapm_limit=preset["stapm"],
            fast_limit=preset["fast"],
            slow_limit=preset["slow"],
        ):
            self.show_toast(f"Applied {preset_name.title()} TDP preset")
        else:
            self.show_toast("Failed to apply TDP preset")

    def on_apply_tdp_clicked(self, button):
        """Handle Apply TDP button click"""
        if not HAS_OVERCLOCKING:
            return

        stapm = int(self.stapm_scale.get_value())
        fast = int(self.fast_scale.get_value())
        slow = int(self.slow_scale.get_value())
        temp = int(self.temp_limit_scale.get_value())

        success = True
        if not self.oc_controller.set_ryzenadj_tdp(
            stapm_limit=stapm, fast_limit=fast, slow_limit=slow
        ):
            success = False
        if not self.oc_controller.set_ryzenadj_temp_limit(temp):
            success = False

        if success:
            self.show_toast(
                f"Applied TDP: STAPM={stapm}W, Fast={fast}W, Slow={slow}W, Temp={temp}°C"
            )
        else:
            self.show_toast("Failed to apply some TDP settings")

    def on_gpu_perf_level_changed(self, combo_row, _):
        """Handle GPU performance level change"""
        if not HAS_OVERCLOCKING:
            return
        selected = combo_row.get_selected()
        levels = ["auto", "low", "high", "manual", "profile_standard", "profile_peak"]
        if selected < len(levels):
            level = levels[selected]
            if self.oc_controller.set_gpu_performance_level(level):
                self.show_toast(f"GPU performance level set to {level}")
            else:
                self.show_toast("Failed to set GPU performance level")

    def on_gpu_power_profile_changed(self, combo_row, _):
        """Handle GPU power profile change"""
        if not HAS_OVERCLOCKING or not hasattr(self, "oc_gpu_profiles"):
            return
        selected = combo_row.get_selected()
        if selected < len(self.oc_gpu_profiles):
            idx, name, _ = self.oc_gpu_profiles[selected]
            if self.oc_controller.set_gpu_power_profile(idx):
                self.show_toast(f"GPU power profile set to {name}")
            else:
                self.show_toast("Failed to set GPU power profile")

    def on_reset_gpu_clicked(self, button):
        """Handle reset GPU clocks button"""
        if not HAS_OVERCLOCKING:
            return
        if self.oc_controller.reset_gpu_clocks():
            self.show_toast("GPU clocks reset to default")
        else:
            self.show_toast("Failed to reset GPU clocks")

    def create_keyboard_page(self):
        """Create the keyboard backlight page"""
        page = Adw.PreferencesPage()
        page.set_title("Keyboard")
        page.set_icon_name("input-keyboard-symbolic")

        if not HAS_KEYBOARD_CONTROL:
            # Show unsupported message
            status_group = Adw.PreferencesGroup()
            unsupported_row = Adw.ActionRow()
            unsupported_row.set_title("Keyboard Control Unavailable")
            unsupported_row.set_subtitle("Keyboard backlight control module not found")
            warn_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            unsupported_row.add_prefix(warn_icon)
            status_group.add(unsupported_row)
            page.add(status_group)
        else:
            try:
                kbd = get_keyboard_controller()
                if not kbd.is_supported():
                    status_group = Adw.PreferencesGroup()
                    unsupported_row = Adw.ActionRow()
                    unsupported_row.set_title("Keyboard Backlight Not Detected")
                    unsupported_row.set_subtitle(
                        "No compatible keyboard backlight found"
                    )
                    warn_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
                    unsupported_row.add_prefix(warn_icon)
                    status_group.add(unsupported_row)
                    page.add(status_group)
                else:
                    # Brightness control group
                    brightness_group = Adw.PreferencesGroup()
                    brightness_group.set_title("Brightness")

                    current_brightness = kbd.get_brightness() or 0
                    max_brightness = kbd.get_max_brightness()

                    brightness_row = Adw.ActionRow()
                    brightness_row.set_title("Backlight Level")
                    brightness_row.set_subtitle(
                        f"Current: {current_brightness} / {max_brightness}"
                    )
                    bright_icon = Gtk.Image.new_from_icon_name(
                        "display-brightness-symbolic"
                    )
                    brightness_row.add_prefix(bright_icon)

                    # Brightness buttons
                    brightness_box = Gtk.Box(
                        orientation=Gtk.Orientation.HORIZONTAL, spacing=4
                    )
                    brightness_box.set_valign(Gtk.Align.CENTER)

                    self.kbd_brightness_buttons = []
                    for level in range(max_brightness + 1):
                        btn = Gtk.Button(label=str(level))
                        btn.set_size_request(40, -1)
                        if current_brightness == level:
                            btn.add_css_class("suggested-action")
                        btn.connect("clicked", self.on_kbd_brightness_clicked, level)
                        brightness_box.append(btn)
                        self.kbd_brightness_buttons.append(btn)

                    brightness_row.add_suffix(brightness_box)
                    brightness_group.add(brightness_row)

                    page.add(brightness_group)

                    # RGB color control (if supported)
                    if kbd.has_rgb():
                        color_group = Adw.PreferencesGroup()
                        color_group.set_title("RGB Lighting")
                        color_group.set_description(
                            "Customize keyboard backlight color"
                        )

                        # Color presets
                        presets_row = Adw.ActionRow()
                        presets_row.set_title("Color Presets")
                        color_icon = Gtk.Image.new_from_icon_name(
                            "applications-graphics-symbolic"
                        )
                        presets_row.add_prefix(color_icon)

                        color_box = Gtk.Box(
                            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
                        )
                        color_box.set_valign(Gtk.Align.CENTER)

                        colors = [
                            ("red", "#e01b24", "Red"),
                            ("green", "#33d17a", "Green"),
                            ("blue", "#3584e4", "Blue"),
                            ("white", "#ffffff", "White"),
                            ("cyan", "#00ffff", "Cyan"),
                            ("purple", "#9141ac", "Purple"),
                            ("orange", "#ff7800", "Orange"),
                        ]

                        for color_name, hex_color, tooltip in colors:
                            btn = Gtk.Button()
                            btn.set_size_request(36, 36)
                            btn.set_tooltip_text(tooltip)
                            # Add colored background via CSS
                            btn_css = Gtk.CssProvider()
                            btn_css.load_from_data(
                                f"""
                                button {{
                                    background-color: {hex_color};
                                    border-radius: 6px;
                                    min-width: 32px;
                                    min-height: 32px;
                                }}
                            """.encode()
                            )
                            btn.get_style_context().add_provider(
                                btn_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                            )
                            btn.connect(
                                "clicked", self.on_kbd_color_clicked, color_name
                            )
                            color_box.append(btn)

                        presets_row.add_suffix(color_box)
                        color_group.add(presets_row)

                        # Custom color picker
                        custom_row = Adw.ActionRow()
                        custom_row.set_title("Custom Color")
                        custom_row.set_subtitle("Choose any color")
                        picker_icon = Gtk.Image.new_from_icon_name(
                            "color-select-symbolic"
                        )
                        custom_row.add_prefix(picker_icon)

                        color_button = Gtk.ColorButton()
                        color_button.set_valign(Gtk.Align.CENTER)
                        color_button.connect("color-set", self.on_custom_color_set)
                        custom_row.add_suffix(color_button)
                        color_group.add(custom_row)

                        page.add(color_group)
            except Exception as e:
                print(f"Keyboard control setup failed: {e}")
                status_group = Adw.PreferencesGroup()
                error_row = Adw.ActionRow()
                error_row.set_title("Error Loading Keyboard Control")
                error_row.set_subtitle(str(e))
                status_group.add(error_row)
                page.add(status_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "keyboard")

    def create_battery_page(self):
        """Create the battery management page"""
        page = Adw.PreferencesPage()
        page.set_title("Battery")
        page.set_icon_name("battery-symbolic")

        if not HAS_BATTERY_CONTROL:
            # Show unsupported message
            status_group = Adw.PreferencesGroup()
            unsupported_row = Adw.ActionRow()
            unsupported_row.set_title("Battery Control Unavailable")
            unsupported_row.set_subtitle("Battery control module not found")
            warn_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            unsupported_row.add_prefix(warn_icon)
            status_group.add(unsupported_row)
            page.add(status_group)
        else:
            try:
                battery = get_battery_controller()
                if not battery.is_supported():
                    status_group = Adw.PreferencesGroup()
                    unsupported_row = Adw.ActionRow()
                    unsupported_row.set_title("Battery Control Not Supported")
                    unsupported_row.set_subtitle(
                        "Your device may not support charge limit control"
                    )
                    warn_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
                    unsupported_row.add_prefix(warn_icon)
                    status_group.add(unsupported_row)
                    page.add(status_group)
                else:
                    # Battery status group
                    status_group = Adw.PreferencesGroup()
                    status_group.set_title("Battery Status")

                    battery_info = battery.get_battery_info()

                    # Current level with visual indicator
                    level_row = Adw.ActionRow()
                    level_row.set_title("Current Level")
                    level_icon = Gtk.Image.new_from_icon_name("battery-symbolic")
                    level_row.add_prefix(level_icon)

                    level_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                    level_box.set_valign(Gtk.Align.CENTER)
                    capacity = battery_info.get("capacity", 0)
                    self.batt_level_label = Gtk.Label(label=f"{capacity}%")
                    self.batt_level_label.add_css_class("title-3")
                    level_box.append(self.batt_level_label)
                    self.batt_level_bar = Gtk.LevelBar()
                    self.batt_level_bar.set_min_value(0)
                    self.batt_level_bar.set_max_value(100)
                    self.batt_level_bar.set_value(capacity)
                    self.batt_level_bar.set_size_request(120, -1)
                    level_box.append(self.batt_level_bar)
                    level_row.add_suffix(level_box)
                    status_group.add(level_row)

                    # Charging status
                    status_row = Adw.ActionRow()
                    status_row.set_title("Status")
                    status = battery_info.get("status", "Unknown")
                    status_row.set_subtitle(status)
                    charge_icon = Gtk.Image.new_from_icon_name(
                        "battery-full-charging-symbolic"
                        if status == "Charging"
                        else "battery-symbolic"
                    )
                    status_row.add_prefix(charge_icon)
                    status_group.add(status_row)

                    # Battery health (if available)
                    if "health" in battery_info:
                        health_row = Adw.ActionRow()
                        health_row.set_title("Battery Health")
                        health_row.set_subtitle(f"{battery_info['health']}%")
                        health_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                        health_row.add_prefix(health_icon)
                        status_group.add(health_row)

                    page.add(status_group)

                    # Charge limit control group
                    limit_group = Adw.PreferencesGroup()
                    limit_group.set_title("Charge Limit")
                    limit_group.set_description(
                        "Limit maximum charge to extend battery lifespan"
                    )

                    current_limit = battery_info.get("charge_limit", 100)

                    # Charge limit row with buttons
                    limit_row = Adw.ActionRow()
                    limit_row.set_title("Maximum Charge")
                    limit_row.set_subtitle(f"Currently set to {current_limit}%")
                    limit_icon = Gtk.Image.new_from_icon_name(
                        "battery-caution-symbolic"
                    )
                    limit_row.add_prefix(limit_icon)

                    limit_box = Gtk.Box(
                        orientation=Gtk.Orientation.HORIZONTAL, spacing=8
                    )
                    limit_box.set_valign(Gtk.Align.CENTER)

                    self.charge_limit_buttons = []
                    presets = [
                        ("60%", 60, "Best for longevity"),
                        ("80%", 80, "Recommended"),
                        ("100%", 100, "Full charge"),
                    ]

                    for label, value, tooltip in presets:
                        btn = Gtk.Button(label=label)
                        btn.set_tooltip_text(tooltip)
                        if current_limit == value:
                            btn.add_css_class("suggested-action")
                        btn.connect("clicked", self.on_charge_limit_clicked, value)
                        limit_box.append(btn)
                        self.charge_limit_buttons.append((btn, value))

                    limit_row.add_suffix(limit_box)
                    limit_group.add(limit_row)

                    page.add(limit_group)
            except Exception as e:
                print(f"Battery page setup failed: {e}")
                status_group = Adw.PreferencesGroup()
                error_row = Adw.ActionRow()
                error_row.set_title("Error Loading Battery Info")
                error_row.set_subtitle(str(e))
                status_group.add(error_row)
                page.add(status_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "battery")

    def create_automation_page(self):
        """Create the automation settings page"""
        page = Adw.PreferencesPage()
        page.set_title("Automation")
        page.set_icon_name("system-run-symbolic")

        # Auto-profile switching group
        profile_group = Adw.PreferencesGroup()
        profile_group.set_title("Automatic Profile Switching")
        profile_group.set_description(
            "Automatically switch profiles based on power state"
        )

        # Enable/disable auto-switching
        enable_row = Adw.SwitchRow()
        enable_row.set_title("Enable Auto-Switching")
        enable_row.set_subtitle(
            "Automatically change profile when plugging/unplugging AC"
        )
        enable_row.set_active(self.load_config().get("auto_profile_enabled", False))
        enable_row.connect("notify::active", self.on_auto_profile_enabled_changed)
        self.auto_profile_switch = enable_row
        profile_group.add(enable_row)

        # AC profile selector
        ac_row = Adw.ComboRow()
        ac_row.set_title("Profile on AC Power")
        ac_row.set_subtitle("Profile to apply when connected to power")

        # Create profile list for dropdown
        profile_names = Gtk.StringList.new(
            [profile["name"] for profile in Config.POWER_PROFILES.values()]
        )
        ac_row.set_model(profile_names)

        # Set default selection
        profile_ids = list(Config.POWER_PROFILES.keys())
        ac_default = self.load_config().get("auto_profile_ac", "performance")
        if ac_default in profile_ids:
            ac_row.set_selected(profile_ids.index(ac_default))

        ac_row.connect("notify::selected", self.on_auto_ac_profile_changed)
        self.auto_ac_combo = ac_row
        profile_group.add(ac_row)

        # Battery profile selector
        bat_row = Adw.ComboRow()
        bat_row.set_title("Profile on Battery")
        bat_row.set_subtitle("Profile to apply when on battery power")
        bat_row.set_model(profile_names)

        bat_default = self.load_config().get("auto_profile_battery", "efficient")
        if bat_default in profile_ids:
            bat_row.set_selected(profile_ids.index(bat_default))

        bat_row.connect("notify::selected", self.on_auto_battery_profile_changed)
        self.auto_battery_combo = bat_row
        profile_group.add(bat_row)

        page.add(profile_group)

        # Refresh rate automation group
        refresh_group = Adw.PreferencesGroup()
        refresh_group.set_title("Display Refresh Rate")
        refresh_group.set_description(
            "Automatically adjust refresh rate based on power state"
        )

        # Enable refresh rate auto-switching
        refresh_enable_row = Adw.SwitchRow()
        refresh_enable_row.set_title("Auto-Adjust Refresh Rate")
        refresh_enable_row.set_subtitle("Lower refresh rate on battery to save power")
        refresh_enable_row.set_active(
            self.load_config().get("auto_refresh_enabled", False)
        )
        refresh_enable_row.connect(
            "notify::active", self.on_auto_refresh_enabled_changed
        )
        self.auto_refresh_switch = refresh_enable_row
        refresh_group.add(refresh_enable_row)

        # AC refresh rate
        ac_refresh_row = Adw.ComboRow()
        ac_refresh_row.set_title("Refresh Rate on AC")
        refresh_rates = Gtk.StringList.new(
            ["30 Hz", "60 Hz", "90 Hz", "120 Hz", "180 Hz"]
        )
        ac_refresh_row.set_model(refresh_rates)

        ac_refresh_default = self.load_config().get("auto_refresh_ac", 120)
        rate_map = {30: 0, 60: 1, 90: 2, 120: 3, 180: 4}
        if ac_refresh_default in rate_map:
            ac_refresh_row.set_selected(rate_map[ac_refresh_default])

        ac_refresh_row.connect("notify::selected", self.on_auto_ac_refresh_changed)
        self.auto_ac_refresh_combo = ac_refresh_row
        refresh_group.add(ac_refresh_row)

        # Battery refresh rate
        bat_refresh_row = Adw.ComboRow()
        bat_refresh_row.set_title("Refresh Rate on Battery")
        bat_refresh_row.set_model(refresh_rates)

        bat_refresh_default = self.load_config().get("auto_refresh_battery", 60)
        if bat_refresh_default in rate_map:
            bat_refresh_row.set_selected(rate_map[bat_refresh_default])

        bat_refresh_row.connect(
            "notify::selected", self.on_auto_battery_refresh_changed
        )
        self.auto_battery_refresh_combo = bat_refresh_row
        refresh_group.add(bat_refresh_row)

        page.add(refresh_group)

        # Temperature-based automation
        temp_group = Adw.PreferencesGroup()
        temp_group.set_title("Temperature Protection")
        temp_group.set_description(
            "Automatically reduce power when temperature is high"
        )

        # Enable temperature throttling
        temp_enable_row = Adw.SwitchRow()
        temp_enable_row.set_title("Temperature Throttling")
        temp_enable_row.set_subtitle(
            "Reduce TDP when CPU temperature exceeds threshold"
        )
        temp_enable_row.set_active(
            self.load_config().get("temp_throttle_enabled", True)
        )
        temp_enable_row.connect("notify::active", self.on_temp_throttle_enabled_changed)
        self.temp_throttle_switch = temp_enable_row
        temp_group.add(temp_enable_row)

        # Temperature threshold
        temp_threshold_row = Adw.SpinRow.new_with_range(70, 100, 5)
        temp_threshold_row.set_title("Temperature Threshold")
        temp_threshold_row.set_subtitle(
            "Throttle when CPU exceeds this temperature (°C)"
        )
        temp_threshold_row.set_value(self.load_config().get("temp_threshold", 85))
        temp_threshold_row.connect("notify::value", self.on_temp_threshold_changed)
        self.temp_threshold_spin = temp_threshold_row
        temp_group.add(temp_threshold_row)

        page.add(temp_group)

        # Startup settings
        startup_group = Adw.PreferencesGroup()
        startup_group.set_title("Startup")
        startup_group.set_description("Configure application startup behavior")

        # Start minimized
        minimize_row = Adw.SwitchRow()
        minimize_row.set_title("Start Minimized to Tray")
        minimize_row.set_subtitle("Start the application minimized to system tray")
        minimize_row.set_active(self.load_config().get("start_minimized", False))
        minimize_row.connect("notify::active", self.on_start_minimized_changed)
        startup_group.add(minimize_row)

        # Apply last profile on startup
        last_profile_row = Adw.SwitchRow()
        last_profile_row.set_title("Remember Last Profile")
        last_profile_row.set_subtitle("Apply the last used profile on startup")
        last_profile_row.set_active(self.load_config().get("remember_profile", True))
        last_profile_row.connect("notify::active", self.on_remember_profile_changed)
        startup_group.add(last_profile_row)

        page.add(startup_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "automation")

    def create_system_info_page(self):
        """Create the system information page"""
        page = Adw.PreferencesPage()
        page.set_title("System Info")
        page.set_icon_name("computer-symbolic")

        # Device info group
        device_group = Adw.PreferencesGroup()
        device_group.set_title("Device Information")

        # Get laptop model info
        model_info = SystemUtils.detect_laptop_model()
        if model_info:
            if model_info.get("vendor"):
                vendor_row = Adw.ActionRow()
                vendor_row.set_title("Manufacturer")
                vendor_row.set_subtitle(model_info["vendor"])
                vendor_row.add_prefix(
                    Gtk.Image.new_from_icon_name("emblem-system-symbolic")
                )
                device_group.add(vendor_row)

            if model_info.get("product"):
                product_row = Adw.ActionRow()
                product_row.set_title("Model")
                product_row.set_subtitle(model_info["product"])
                product_row.add_prefix(
                    Gtk.Image.new_from_icon_name("computer-laptop-symbolic")
                )
                device_group.add(product_row)

            if model_info.get("board"):
                board_row = Adw.ActionRow()
                board_row.set_title("Board")
                board_row.set_subtitle(model_info["board"])
                board_row.add_prefix(
                    Gtk.Image.new_from_icon_name("application-x-firmware-symbolic")
                )
                device_group.add(board_row)

        page.add(device_group)

        # Operating System group
        os_group = Adw.PreferencesGroup()
        os_group.set_title("Operating System")

        os_info = SystemUtils.get_os_info()

        os_row = Adw.ActionRow()
        os_row.set_title("Distribution")
        os_row.set_subtitle(os_info.get("name", "Unknown"))
        os_row.add_prefix(Gtk.Image.new_from_icon_name("distributor-logo-symbolic"))
        os_group.add(os_row)

        kernel_row = Adw.ActionRow()
        kernel_row.set_title("Kernel")
        kernel_row.set_subtitle(os_info.get("kernel", "Unknown"))
        kernel_row.add_prefix(
            Gtk.Image.new_from_icon_name("utilities-terminal-symbolic")
        )
        os_group.add(kernel_row)

        desktop_row = Adw.ActionRow()
        desktop_row.set_title("Desktop Environment")
        desktop_row.set_subtitle(os_info.get("desktop", "Unknown"))
        desktop_row.add_prefix(
            Gtk.Image.new_from_icon_name("preferences-desktop-symbolic")
        )
        os_group.add(desktop_row)

        uptime_row = Adw.ActionRow()
        uptime_row.set_title("System Uptime")
        uptime_row.set_subtitle(os_info.get("uptime", "Unknown"))
        uptime_row.add_prefix(
            Gtk.Image.new_from_icon_name("preferences-system-time-symbolic")
        )
        self.system_uptime_row = uptime_row
        os_group.add(uptime_row)

        page.add(os_group)

        # CPU group
        cpu_group = Adw.PreferencesGroup()
        cpu_group.set_title("Processor")

        cpu_info = SystemUtils.get_cpu_info()

        cpu_model_row = Adw.ActionRow()
        cpu_model_row.set_title("CPU Model")
        cpu_model_row.set_subtitle(cpu_info.get("model", "Unknown"))
        cpu_model_row.add_prefix(Gtk.Image.new_from_icon_name("cpu-symbolic"))
        cpu_group.add(cpu_model_row)

        cores_row = Adw.ActionRow()
        cores_row.set_title("CPU Cores")
        cores = cpu_info.get("cores", "0")
        threads = cpu_info.get("threads", "0")
        cores_row.set_subtitle(f"{cores} Cores / {threads} Threads")
        cores_row.add_prefix(Gtk.Image.new_from_icon_name("view-grid-symbolic"))
        cpu_group.add(cores_row)

        freq_row = Adw.ActionRow()
        freq_row.set_title("Max Frequency")
        freq_row.set_subtitle(cpu_info.get("max_freq", "Unknown"))
        freq_row.add_prefix(Gtk.Image.new_from_icon_name("speedometer-symbolic"))
        cpu_group.add(freq_row)

        arch_row = Adw.ActionRow()
        arch_row.set_title("Architecture")
        arch_row.set_subtitle(cpu_info.get("architecture", "Unknown"))
        arch_row.add_prefix(Gtk.Image.new_from_icon_name("chip-symbolic"))
        cpu_group.add(arch_row)

        page.add(cpu_group)

        # GPU group
        gpu_group = Adw.PreferencesGroup()
        gpu_group.set_title("Graphics")

        gpus = SystemUtils.get_gpu_info()
        for i, gpu in enumerate(gpus):
            gpu_row = Adw.ActionRow()
            gpu_row.set_title(f"GPU {i + 1}" if len(gpus) > 1 else "Graphics Card")
            gpu_row.set_subtitle(
                f"{gpu.get('name', 'Unknown')} ({gpu.get('type', 'Unknown')})"
            )
            gpu_row.add_prefix(Gtk.Image.new_from_icon_name("video-display-symbolic"))
            gpu_group.add(gpu_row)

        page.add(gpu_group)

        # Memory group
        memory_group = Adw.PreferencesGroup()
        memory_group.set_title("Memory")

        mem_info = SystemUtils.get_memory_info()

        total_row = Adw.ActionRow()
        total_row.set_title("Total RAM")
        total_row.set_subtitle(mem_info.get("total", "Unknown"))
        total_row.add_prefix(Gtk.Image.new_from_icon_name("memory-symbolic"))
        memory_group.add(total_row)

        usage_row = Adw.ActionRow()
        usage_row.set_title("Memory Usage")
        used = mem_info.get("used", "0 GB")
        percent = mem_info.get("percent_used", "0%")
        usage_row.set_subtitle(f"{used} ({percent})")
        usage_row.add_prefix(
            Gtk.Image.new_from_icon_name("utilities-system-monitor-symbolic")
        )
        self.system_memory_row = usage_row
        memory_group.add(usage_row)

        page.add(memory_group)

        # Storage group
        storage_group = Adw.PreferencesGroup()
        storage_group.set_title("Storage")

        storage_devices = SystemUtils.get_storage_info()
        for device in storage_devices[:3]:  # Limit to first 3 devices
            storage_row = Adw.ActionRow()
            mount = device.get("mount_point", "/")
            storage_row.set_title(f"Partition: {mount}")
            size = device.get("size", "Unknown")
            used = device.get("used", "Unknown")
            percent = device.get("percent_used", "0%")
            storage_row.set_subtitle(f"{used} / {size} ({percent})")
            storage_row.add_prefix(
                Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
            )
            storage_group.add(storage_row)

        page.add(storage_group)

        # BIOS Features group (if supported)
        features_group = Adw.PreferencesGroup()
        features_group.set_title("BIOS Features")
        features_group.set_description("Hardware features controlled by BIOS")

        # Panel Overdrive
        panel_od = SystemUtils.get_panel_overdrive_status()
        if panel_od is not None:
            od_row = Adw.SwitchRow()
            od_row.set_title("Panel Overdrive")
            od_row.set_subtitle("Reduce display ghosting (may increase power usage)")
            od_row.set_active(panel_od)
            od_row.connect("notify::active", self.on_panel_overdrive_changed)
            features_group.add(od_row)

        # Boot Sound
        boot_sound = SystemUtils.get_boot_sound_status()
        if boot_sound is not None:
            sound_row = Adw.SwitchRow()
            sound_row.set_title("Boot Sound")
            sound_row.set_subtitle("Play POST sound on startup")
            sound_row.set_active(boot_sound)
            sound_row.connect("notify::active", self.on_boot_sound_changed)
            features_group.add(sound_row)

        # Only add features group if it has children
        if panel_od is not None or boot_sound is not None:
            page.add(features_group)

        # Export/Import group
        backup_group = Adw.PreferencesGroup()
        backup_group.set_title("Settings Backup")
        backup_group.set_description("Export and import your configuration")

        export_row = Adw.ActionRow()
        export_row.set_title("Export Settings")
        export_row.set_subtitle("Save current configuration to a file")
        export_row.add_prefix(Gtk.Image.new_from_icon_name("document-save-symbolic"))

        export_btn = Gtk.Button(label="Export")
        export_btn.set_valign(Gtk.Align.CENTER)
        export_btn.connect("clicked", self.on_export_settings)
        export_row.add_suffix(export_btn)
        export_row.set_activatable_widget(export_btn)
        backup_group.add(export_row)

        import_row = Adw.ActionRow()
        import_row.set_title("Import Settings")
        import_row.set_subtitle("Load configuration from a file")
        import_row.add_prefix(Gtk.Image.new_from_icon_name("document-open-symbolic"))

        import_btn = Gtk.Button(label="Import")
        import_btn.set_valign(Gtk.Align.CENTER)
        import_btn.connect("clicked", self.on_import_settings)
        import_row.add_suffix(import_btn)
        import_row.set_activatable_widget(import_btn)
        backup_group.add(import_row)

        page.add(backup_group)

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(page)

        self.view_stack.add_named(scrolled, "system")

    def update_power_profile_indicator(self, active_profile_id):
        """Update visual indicators to show the currently active power profile"""
        if not hasattr(self, "power_profile_rows"):
            return
        for profile_id, (row, check_icon) in self.power_profile_rows.items():
            button = self.power_profile_buttons[profile_id]

            if profile_id == active_profile_id:
                check_icon.set_visible(True)
                button.set_label("Active")
                button.add_css_class("suggested-action")
                button.set_sensitive(False)
            else:
                check_icon.set_visible(False)
                button.set_label("Apply")
                button.remove_css_class("suggested-action")
                button.set_sensitive(True)

    def update_refresh_rate_indicator(self, active_rate_id):
        """Update visual indicators to show the currently active refresh rate"""
        if not hasattr(self, "refresh_rate_rows"):
            return
        for rate_id, (row, check_icon) in self.refresh_rate_rows.items():
            button = self.refresh_rate_buttons[rate_id]

            if rate_id == active_rate_id:
                check_icon.set_visible(True)
                button.set_label("Active")
                button.add_css_class("suggested-action")
                button.set_sensitive(False)
            else:
                check_icon.set_visible(False)
                button.set_label("Apply")
                button.remove_css_class("suggested-action")
                button.set_sensitive(True)

    def on_charge_limit_clicked(self, button, limit):
        """Handle charge limit button click"""
        if not HAS_BATTERY_CONTROL:
            return

        battery = get_battery_controller()
        success, message = battery.set_charge_limit(limit)

        if success:
            self.show_toast(f"Charge limit set to {limit}%")
            # Update button states
            if hasattr(self, "charge_limit_buttons"):
                for btn, value in self.charge_limit_buttons:
                    if value == limit:
                        btn.add_css_class("suggested-action")
                    else:
                        btn.remove_css_class("suggested-action")
        else:
            self.show_toast(f"Failed: {message}")

    def on_fan_curve_toggled(self, switch, state):
        """Handle fan curve toggle"""
        if not HAS_FAN_CONTROL:
            return False

        fan = get_fan_controller()
        success, message = fan.enable_custom_fan_curve(state)

        if success:
            self.show_toast(message)
        else:
            self.show_toast(f"Failed: {message}")
            return True  # Prevent state change
        return False

    def on_open_fan_curve_editor(self, button):
        """Open the visual fan curve editor dialog"""
        if not HAS_FAN_CURVE_EDITOR:
            self.show_toast("Fan curve editor not available")
            return

        dialog = FanCurveEditorDialog(
            fan_name="CPU Fan", on_apply=self.on_fan_curve_applied
        )
        dialog.present(self)

    def on_fan_curve_applied(self, fan_name: str, curve_data: list):
        """Handle fan curve being applied from the editor"""
        print(f"Fan curve applied for {fan_name}: {curve_data}")

        # Save curve to config
        self.save_fan_curve(fan_name, curve_data)

        # Try to apply via fan control if available
        if HAS_FAN_CONTROL:
            fan = get_fan_controller()
            if hasattr(fan, "set_fan_curve"):
                success, message = fan.set_fan_curve(curve_data)
                if success:
                    self.show_toast(f"Fan curve applied for {fan_name}")
                else:
                    self.show_toast(f"Curve saved (apply via asusd): {message}")
            else:
                self.show_toast(
                    f"Fan curve saved for {fan_name} (requires asusd to apply)"
                )
        else:
            self.show_toast(f"Fan curve saved for {fan_name}")

        # Update preview widget if present
        if hasattr(self, "preview_curve_widget"):
            self.preview_curve_widget.set_curve_data(curve_data)

    def save_fan_curve(self, fan_name: str, curve_data: list):
        """Save fan curve to config file"""
        config = self.load_config()
        if "fan_curves" not in config:
            config["fan_curves"] = {}
        config["fan_curves"][fan_name] = curve_data
        self.save_config(config)

    def on_kbd_brightness_clicked(self, button, level):
        """Handle keyboard brightness button click"""
        if not HAS_KEYBOARD_CONTROL:
            return

        kbd = get_keyboard_controller()
        success, message = kbd.set_brightness(level)

        if success:
            self.show_toast(f"Keyboard brightness set to {level}")
            # Update button states
            if hasattr(self, "kbd_brightness_buttons"):
                for i, btn in enumerate(self.kbd_brightness_buttons):
                    if i == level:
                        btn.add_css_class("suggested-action")
                    else:
                        btn.remove_css_class("suggested-action")
        else:
            self.show_toast(f"Failed: {message}")

    def on_kbd_color_clicked(self, button, color):
        """Handle keyboard color button click"""
        if not HAS_KEYBOARD_CONTROL:
            return

        kbd = get_keyboard_controller()
        success, message = kbd.set_preset_color(color)

        if success:
            self.show_toast(f"Keyboard color set to {color}")
        else:
            self.show_toast(f"Failed: {message}")

    def on_custom_color_set(self, button):
        """Handle custom color picker selection"""
        if not HAS_KEYBOARD_CONTROL:
            return

        rgba = button.get_rgba()
        r = int(rgba.red * 255)
        g = int(rgba.green * 255)
        b = int(rgba.blue * 255)

        kbd = get_keyboard_controller()
        success, message = kbd.set_color(r, g, b)

        if success:
            self.show_toast(f"Keyboard color set to RGB({r}, {g}, {b})")
        else:
            self.show_toast(f"Failed: {message}")

    def show_toast(self, message):
        """Show a toast notification"""
        toast = Adw.Toast.new(message)
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

    def load_config(self) -> dict:
        """Load application configuration from file"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                return {}
        return {}

    def save_config(self, config: dict):
        """Save application configuration to file"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")

    # Automation settings handlers
    def on_auto_profile_enabled_changed(self, switch, param):
        """Handle auto profile switching toggle"""
        config = self.load_config()
        config["auto_profile_enabled"] = switch.get_active()
        self.save_config(config)

        if switch.get_active():
            self.show_toast("Auto profile switching enabled")
            # Trigger initial check
            self.check_power_state_and_switch()
        else:
            self.show_toast("Auto profile switching disabled")

    def on_auto_ac_profile_changed(self, combo, param):
        """Handle AC profile selection change"""
        profile_ids = list(Config.POWER_PROFILES.keys())
        selected = combo.get_selected()
        if selected < len(profile_ids):
            config = self.load_config()
            config["auto_profile_ac"] = profile_ids[selected]
            self.save_config(config)

    def on_auto_battery_profile_changed(self, combo, param):
        """Handle battery profile selection change"""
        profile_ids = list(Config.POWER_PROFILES.keys())
        selected = combo.get_selected()
        if selected < len(profile_ids):
            config = self.load_config()
            config["auto_profile_battery"] = profile_ids[selected]
            self.save_config(config)

    def on_auto_refresh_enabled_changed(self, switch, param):
        """Handle auto refresh rate toggle"""
        config = self.load_config()
        config["auto_refresh_enabled"] = switch.get_active()
        self.save_config(config)

        if switch.get_active():
            self.show_toast("Auto refresh rate switching enabled")
        else:
            self.show_toast("Auto refresh rate switching disabled")

    def on_auto_ac_refresh_changed(self, combo, param):
        """Handle AC refresh rate selection change"""
        rates = [30, 60, 90, 120, 180]
        selected = combo.get_selected()
        if selected < len(rates):
            config = self.load_config()
            config["auto_refresh_ac"] = rates[selected]
            self.save_config(config)

    def on_auto_battery_refresh_changed(self, combo, param):
        """Handle battery refresh rate selection change"""
        rates = [30, 60, 90, 120, 180]
        selected = combo.get_selected()
        if selected < len(rates):
            config = self.load_config()
            config["auto_refresh_battery"] = rates[selected]
            self.save_config(config)

    def on_temp_throttle_enabled_changed(self, switch, param):
        """Handle temperature throttling toggle"""
        config = self.load_config()
        config["temp_throttle_enabled"] = switch.get_active()
        self.save_config(config)

        if switch.get_active():
            self.show_toast("Temperature throttling enabled")
        else:
            self.show_toast("Temperature throttling disabled")

    def on_temp_threshold_changed(self, spin, param):
        """Handle temperature threshold change"""
        config = self.load_config()
        config["temp_threshold"] = int(spin.get_value())
        self.save_config(config)

    def on_start_minimized_changed(self, switch, param):
        """Handle start minimized toggle"""
        config = self.load_config()
        config["start_minimized"] = switch.get_active()
        self.save_config(config)

    def on_remember_profile_changed(self, switch, param):
        """Handle remember profile toggle"""
        config = self.load_config()
        config["remember_profile"] = switch.get_active()
        self.save_config(config)

    def on_panel_overdrive_changed(self, switch, param):
        """Handle panel overdrive toggle"""
        enabled = switch.get_active()
        success, message = SystemUtils.set_panel_overdrive(enabled)
        if success:
            self.show_toast(message)
        else:
            self.show_toast(f"Failed: {message}")
            # Revert switch state
            switch.set_active(not enabled)

    def on_boot_sound_changed(self, switch, param):
        """Handle boot sound toggle"""
        enabled = switch.get_active()
        success, message = SystemUtils.set_boot_sound(enabled)
        if success:
            self.show_toast(message)
        else:
            self.show_toast(f"Failed: {message}")
            # Revert switch state
            switch.set_active(not enabled)

    def on_export_settings(self, button):
        """Export settings to a file"""
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export Settings")
        dialog.set_initial_name("linux-armoury-settings.json")

        # Set up file filter
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_json)
        dialog.set_filters(filters)
        dialog.set_default_filter(filter_json)

        dialog.save(self, None, self.on_export_response)

    def on_export_response(self, dialog, result):
        """Handle export file dialog response"""
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                config = self.load_config()

                # Add app settings too
                export_data = {
                    "config": config,
                    "settings": self.settings,
                    "version": Config.VERSION,
                }

                with open(path, "w") as f:
                    json.dump(export_data, f, indent=2)

                self.show_toast(f"Settings exported to {os.path.basename(path)}")
        except GLib.Error as e:
            if e.code != Gtk.DialogError.DISMISSED:
                self.show_toast(f"Export failed: {e.message}")

    def on_import_settings(self, button):
        """Import settings from a file"""
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Import Settings")

        # Set up file filter
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_pattern("*.json")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_json)
        dialog.set_filters(filters)
        dialog.set_default_filter(filter_json)

        dialog.open(self, None, self.on_import_response)

    def on_import_response(self, dialog, result):
        """Handle import file dialog response"""
        try:
            file = dialog.open_finish(result)
            if file:
                path = file.get_path()

                with open(path, "r") as f:
                    import_data = json.load(f)

                # Import config
                if "config" in import_data:
                    self.save_config(import_data["config"])

                # Import settings
                if "settings" in import_data:
                    self.settings.update(import_data["settings"])
                    self.get_application().save_settings()

                self.show_toast(f"Settings imported from {os.path.basename(path)}")
                self.show_toast("Restart the app for changes to take effect")
        except GLib.Error as e:
            if e.code != Gtk.DialogError.DISMISSED:
                self.show_toast(f"Import failed: {e.message}")
        except (json.JSONDecodeError, IOError) as e:
            self.show_toast(f"Invalid settings file: {e}")

    def show_session_details(self, button):
        """Show detailed session statistics in a dialog"""
        if not HAS_SESSION_STATS:
            self.show_toast("Session statistics not available")
            return

        stats = get_session_stats()
        summary = stats.get_summary()

        # Create dialog
        dialog = Adw.Dialog()
        dialog.set_title("Session Statistics")
        dialog.set_content_width(450)
        dialog.set_content_height(500)

        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        header.set_show_start_title_buttons(True)
        main_box.append(header)

        # Content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)

        # Session info
        session_label = Gtk.Label()
        session_label.set_markup(
            f"<b>Session started:</b> {summary.get('session_start', 'N/A')}"
        )
        session_label.set_halign(Gtk.Align.START)
        content_box.append(session_label)

        duration_label = Gtk.Label()
        duration_label.set_markup(
            f"<b>Duration:</b> {summary.get('session_duration', 'N/A')}"
        )
        duration_label.set_halign(Gtk.Align.START)
        content_box.append(duration_label)

        # CPU stats
        cpu_frame = Gtk.Frame()
        cpu_frame.set_label("CPU Temperature")
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        cpu_box.set_margin_top(8)
        cpu_box.set_margin_bottom(8)
        cpu_box.set_margin_start(12)
        cpu_box.set_margin_end(12)

        cpu_data = summary.get("cpu", {})
        max_cpu = Gtk.Label(label=f"Maximum: {cpu_data.get('max_temp', 'N/A')}°C")
        max_cpu.set_halign(Gtk.Align.START)
        avg_cpu = Gtk.Label(label=f"Average: {cpu_data.get('avg_temp', 'N/A')}°C")
        avg_cpu.set_halign(Gtk.Align.START)
        cpu_box.append(max_cpu)
        cpu_box.append(avg_cpu)
        cpu_frame.set_child(cpu_box)
        content_box.append(cpu_frame)

        # GPU stats
        gpu_data = summary.get("gpu", {})
        if gpu_data.get("max_temp"):
            gpu_frame = Gtk.Frame()
            gpu_frame.set_label("GPU Temperature")
            gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            gpu_box.set_margin_top(8)
            gpu_box.set_margin_bottom(8)
            gpu_box.set_margin_start(12)
            gpu_box.set_margin_end(12)

            max_gpu = Gtk.Label(label=f"Maximum: {gpu_data.get('max_temp', 'N/A')}°C")
            max_gpu.set_halign(Gtk.Align.START)
            avg_gpu = Gtk.Label(label=f"Average: {gpu_data.get('avg_temp', 'N/A')}°C")
            avg_gpu.set_halign(Gtk.Align.START)
            gpu_box.append(max_gpu)
            gpu_box.append(avg_gpu)
            gpu_frame.set_child(gpu_box)
            content_box.append(gpu_frame)

        # Battery stats
        battery_data = summary.get("battery", {})
        bat_frame = Gtk.Frame()
        bat_frame.set_label("Battery")
        bat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bat_box.set_margin_top(8)
        bat_box.set_margin_bottom(8)
        bat_box.set_margin_start(12)
        bat_box.set_margin_end(12)

        initial = battery_data.get("initial")
        drain = battery_data.get("drain")
        if initial is not None:
            initial_label = Gtk.Label(label=f"Initial level: {initial}%")
            initial_label.set_halign(Gtk.Align.START)
            bat_box.append(initial_label)
        if drain is not None:
            drain_label = Gtk.Label(label=f"Battery used: {drain}%")
            drain_label.set_halign(Gtk.Align.START)
            bat_box.append(drain_label)

        time_ac = battery_data.get("time_on_ac_min", 0)
        time_bat = battery_data.get("time_on_battery_min", 0)
        ac_label = Gtk.Label(label=f"Time on AC: {time_ac:.1f} min")
        ac_label.set_halign(Gtk.Align.START)
        bat_label = Gtk.Label(label=f"Time on battery: {time_bat:.1f} min")
        bat_label.set_halign(Gtk.Align.START)
        bat_box.append(ac_label)
        bat_box.append(bat_label)

        bat_frame.set_child(bat_box)
        content_box.append(bat_frame)

        # Profile usage
        profiles = summary.get("profiles", {})
        if profiles:
            profile_frame = Gtk.Frame()
            profile_frame.set_label("Profile Usage")
            profile_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            profile_box.set_margin_top(8)
            profile_box.set_margin_bottom(8)
            profile_box.set_margin_start(12)
            profile_box.set_margin_end(12)

            for profile, seconds in profiles.items():
                mins = seconds / 60
                p_label = Gtk.Label(label=f"{profile.capitalize()}: {mins:.1f} min")
                p_label.set_halign(Gtk.Align.START)
                profile_box.append(p_label)

            profile_frame.set_child(profile_box)
            content_box.append(profile_frame)

        # Button to save session
        save_btn = Gtk.Button(label="Save Session Log")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", lambda b: self.save_session_log(dialog))
        save_btn.set_halign(Gtk.Align.CENTER)
        save_btn.set_margin_top(16)
        content_box.append(save_btn)

        main_box.append(content_box)
        dialog.set_child(main_box)
        dialog.present(self)

    def save_session_log(self, dialog):
        """Save the current session log"""
        if not HAS_SESSION_STATS:
            return

        stats = get_session_stats()
        filepath = stats.save_session()

        if filepath:
            self.show_toast(f"Session saved to {os.path.basename(filepath)}")
        else:
            self.show_toast("Failed to save session")

    def check_power_state_and_switch(self):
        """Check current power state and switch profile if needed"""
        config = self.load_config()
        if not config.get("auto_profile_enabled", False):
            return

        # Check if on AC or battery
        try:
            with open("/sys/class/power_supply/AC0/online", "r") as f:
                on_ac = f.read().strip() == "1"
        except FileNotFoundError:
            # Try alternative path
            try:
                with open("/sys/class/power_supply/ACAD/online", "r") as f:
                    on_ac = f.read().strip() == "1"
            except FileNotFoundError:
                return  # Can't determine power state

        # Only switch if state changed
        if self.last_ac_state != on_ac:
            self.last_ac_state = on_ac

            if on_ac:
                profile = config.get("auto_profile_ac", "performance")
            else:
                profile = config.get("auto_profile_battery", "efficient")

            # Apply the profile
            if profile in Config.POWER_PROFILES:
                profile_config = Config.POWER_PROFILES[profile]
                tdp = profile_config.get("tdp")
                if tdp:
                    SystemUtils.set_tdp(tdp)
                    self.show_toast(f"Auto-switched to {profile_config['name']}")

            # Also handle refresh rate if enabled
            if config.get("auto_refresh_enabled", False):
                if on_ac:
                    rate = config.get("auto_refresh_ac", 120)
                else:
                    rate = config.get("auto_refresh_battery", 60)
                SystemUtils.set_refresh_rate(rate)

    def setup_actions(self):
        """Setup window and application actions"""
        # Theme actions
        light_action = Gio.SimpleAction.new("theme-light", None)
        light_action.connect("activate", lambda a, p: self.change_theme("light"))
        self.add_action(light_action)

        dark_action = Gio.SimpleAction.new("theme-dark", None)
        dark_action.connect("activate", lambda a, p: self.change_theme("dark"))
        self.add_action(dark_action)

        auto_action = Gio.SimpleAction.new("theme-auto", None)
        auto_action.connect("activate", lambda a, p: self.change_theme("auto"))
        self.add_action(auto_action)

        # Preferences action
        pref_action = Gio.SimpleAction.new("preferences", None)
        pref_action.connect("activate", self.show_preferences)
        self.add_action(pref_action)

        # Shortcuts action
        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.show_shortcuts)
        self.add_action(shortcuts_action)

        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.show_about)
        self.add_action(about_action)

    def change_theme(self, theme):
        """Change application theme"""
        self.apply_theme(theme)
        self.settings["theme"] = theme
        self.get_application().save_settings()

    def on_power_profile_clicked(self, button, profile):
        """Handle power profile button click"""
        # Validate profile against known profiles to prevent injection
        valid_profiles = [
            "emergency",
            "battery",
            "efficient",
            "balanced",
            "performance",
            "gaming",
            "maximum",
        ]
        if profile not in valid_profiles:
            self.show_error_dialog(f"Invalid profile: {profile}")
            return

        try:
            # Check if pwrcfg exists first
            if not SystemUtils.check_command_exists("pwrcfg"):
                self.show_error_dialog(
                    "pwrcfg command not found.\n\n"
                    "Linux Armoury requires the GZ302-Linux-Setup tools for power management.\n\n"
                    "Quick install:\n"
                    "1) curl -L https://raw.githubusercontent.com/th3cavalry/GZ302-Linux-Setup/main/gz302-main.sh -o gz302-main.sh\n"
                    "2) chmod +x gz302-main.sh\n"
                    "3) sudo ./gz302-main.sh\n\n"
                    "More info: https://github.com/th3cavalry/GZ302-Linux-Setup"
                )
                return

            # Run pwrcfg command with validated profile (no shell=True)
            result = subprocess.run(
                ["pkexec", "pwrcfg", profile],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.settings["current_power_profile"] = profile
                self.get_application().save_settings()
                # Update visual indicator for active profile
                self.update_power_profile_indicator(profile)
                self.show_success_dialog(f"Power profile set to {profile}")
                # Notify
                app = self.get_application()
                if hasattr(app, "notify"):
                    app.notify(
                        "Power Profile Changed",
                        f"Applied '{profile}' profile successfully",
                    )
                self.refresh_status()
            else:
                self.show_error_dialog(f"Failed to set power profile: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.show_error_dialog("Command timed out")
        except Exception as e:
            self.show_error_dialog(f"Error: {str(e)}")

    def on_refresh_rate_clicked(self, button, rate):
        """Handle refresh rate button click"""
        # Validate rate against known rates
        valid_rates = ["30", "60", "90", "120", "180"]
        if str(rate) not in valid_rates:
            self.show_error_dialog(f"Invalid refresh rate: {rate}")
            return

        try:
            # Use unified set_refresh_rate method (handles X11 and Wayland)
            success, message = SystemUtils.set_refresh_rate(int(rate))

            if success:
                self.settings["current_refresh_rate"] = rate
                self.get_application().save_settings()
                # Update visual indicator for active refresh rate
                self.update_refresh_rate_indicator(str(rate))
                self.show_success_dialog(message)
                # Notify
                app = self.get_application()
                if hasattr(app, "notify"):
                    app.notify("Refresh Rate Changed", f"Display set to {rate} Hz")
                self.refresh_status()
            else:
                self.show_error_dialog(message)
        except Exception as e:
            self.show_error_dialog(f"Error: {str(e)}")

    def refresh_status(self):
        """Refresh the status information across all pages"""
        # Get current values - detect from system when possible
        detected_profile = SystemUtils.get_current_power_profile()
        if detected_profile:
            # Map platform_profile to our profile names
            profile_map = {
                "low-power": "battery",
                "balanced": "balanced",
                "performance": "performance",
                "quiet": "battery",
            }
            current_profile = profile_map.get(detected_profile, detected_profile)
            # Sync with settings
            self.settings["current_power_profile"] = current_profile
        else:
            current_profile = self.settings.get("current_power_profile", "balanced")

        detected_rate = SystemUtils.get_current_refresh_rate()
        tdp = SystemUtils.get_current_tdp()
        cpu_temp = SystemUtils.get_cpu_temperature()
        gpu_temp = SystemUtils.get_gpu_temperature()
        on_ac = SystemUtils.is_on_ac_power()
        battery = SystemUtils.get_battery_percentage()

        # --- Update Dashboard Page ---
        # Power profile
        if hasattr(self, "dash_power_row"):
            self.dash_power_row.set_subtitle(current_profile.capitalize())

        # Refresh rate
        if hasattr(self, "dash_refresh_row"):
            if detected_rate:
                self.dash_refresh_row.set_subtitle(f"{detected_rate} Hz")
            else:
                current_rate = self.settings.get("current_refresh_rate", "90")
                self.dash_refresh_row.set_subtitle(f"{current_rate} Hz")

        # TDP
        if hasattr(self, "dash_tdp_row"):
            if tdp:
                self.dash_tdp_row.set_subtitle(f"{tdp} W")
            else:
                self.dash_tdp_row.set_subtitle("Available via power profiles")

        # CPU temperature with color coding
        if hasattr(self, "dash_cpu_temp_label") and cpu_temp:
            self.dash_cpu_temp_label.set_text(f"{cpu_temp:.0f}°C")
            # Temperature progress bar (0-100°C scale)
            temp_fraction = min(cpu_temp / 100.0, 1.0)
            self.dash_cpu_temp_bar.set_fraction(temp_fraction)
            # Color coding
            self.dash_cpu_temp_label.remove_css_class("temp-cool")
            self.dash_cpu_temp_label.remove_css_class("temp-warm")
            self.dash_cpu_temp_label.remove_css_class("temp-hot")
            self.dash_cpu_temp_label.remove_css_class("temp-critical")
            if cpu_temp < 50:
                self.dash_cpu_temp_label.add_css_class("temp-cool")
            elif cpu_temp < 70:
                self.dash_cpu_temp_label.add_css_class("temp-warm")
            elif cpu_temp < 85:
                self.dash_cpu_temp_label.add_css_class("temp-hot")
            else:
                self.dash_cpu_temp_label.add_css_class("temp-critical")

        # GPU temperature
        if hasattr(self, "dash_gpu_temp_label") and gpu_temp:
            self.dash_gpu_temp_label.set_text(f"{gpu_temp:.0f}°C")
            temp_fraction = min(gpu_temp / 100.0, 1.0)
            self.dash_gpu_temp_bar.set_fraction(temp_fraction)

        # Battery level
        if hasattr(self, "dash_battery_label") and battery is not None:
            self.dash_battery_label.set_text(f"{battery}%")
            self.dash_battery_bar.set_value(battery)
            # Update icon based on charging status
            if on_ac:
                self.dash_battery_icon.set_from_icon_name(
                    "battery-full-charging-symbolic"
                )
            elif battery < 20:
                self.dash_battery_icon.set_from_icon_name("battery-caution-symbolic")
            elif battery < 50:
                self.dash_battery_icon.set_from_icon_name("battery-low-symbolic")
            else:
                self.dash_battery_icon.set_from_icon_name("battery-full-symbolic")

        # Power source
        if hasattr(self, "dash_power_source_row"):
            power_source = "AC Power (Charging)" if on_ac else "Battery Power"
            self.dash_power_source_row.set_subtitle(power_source)

        # --- Update Sidebar Status ---
        if hasattr(self, "sidebar_cpu_label") and cpu_temp:
            self.sidebar_cpu_label.set_text(f"{cpu_temp:.0f}°C")
        if hasattr(self, "sidebar_battery_label") and battery is not None:
            self.sidebar_battery_label.set_text(f"{battery}%")
        if hasattr(self, "sidebar_profile_label"):
            self.sidebar_profile_label.set_text(current_profile.capitalize())

        # --- Update Performance Page ---
        if hasattr(self, "perf_tdp_row"):
            if tdp:
                self.perf_tdp_row.set_subtitle(
                    f"{tdp} W • Profile: {current_profile.capitalize()}"
                )
            else:
                self.perf_tdp_row.set_subtitle(
                    f"Profile: {current_profile.capitalize()}"
                )

        # --- Update Cooling Page ---
        if hasattr(self, "cool_cpu_temp_label") and cpu_temp:
            self.cool_cpu_temp_label.set_text(f"{cpu_temp:.0f}°C")
            self.cool_cpu_temp_bar.set_fraction(min(cpu_temp / 100.0, 1.0))
        if hasattr(self, "cool_gpu_temp_label") and gpu_temp:
            self.cool_gpu_temp_label.set_text(f"{gpu_temp:.0f}°C")
            self.cool_gpu_temp_bar.set_fraction(min(gpu_temp / 100.0, 1.0))

        # Update fan speeds if available
        if HAS_FAN_CONTROL and hasattr(self, "fan_speed_rows"):
            try:
                fan = get_fan_controller()
                fans = fan.get_all_fan_speeds()
                for i, (row, label) in enumerate(self.fan_speed_rows):
                    if i < len(fans):
                        label.set_text(f"{fans[i].rpm} RPM")
            except Exception:
                pass

        # --- Update GPU Page ---
        if HAS_GPU_CONTROL and hasattr(self, "gpu_controller") and self.gpu_controller:
            try:
                stats = self.gpu_controller.get_live_stats()

                # Update GPU name
                if hasattr(self, "gpu_name_row"):
                    self.gpu_name_row.set_subtitle(f"{stats.gpu_name} ({stats.vendor})")

                # Update GPU clock
                if hasattr(self, "gpu_clock_row"):
                    if stats.gpu_clock_max_mhz > 0:
                        self.gpu_clock_row.set_subtitle(
                            f"{stats.gpu_clock_mhz} / {stats.gpu_clock_max_mhz} MHz"
                        )
                    else:
                        self.gpu_clock_row.set_subtitle(f"{stats.gpu_clock_mhz} MHz")

                # Update memory clock
                if hasattr(self, "gpu_mem_clock_row"):
                    if stats.mem_clock_max_mhz > 0:
                        self.gpu_mem_clock_row.set_subtitle(
                            f"{stats.mem_clock_mhz} / {stats.mem_clock_max_mhz} MHz"
                        )
                    else:
                        self.gpu_mem_clock_row.set_subtitle(
                            f"{stats.mem_clock_mhz} MHz"
                        )

                # Update GPU usage
                if hasattr(self, "gpu_usage_row"):
                    self.gpu_usage_row.set_subtitle(f"{stats.gpu_usage_percent}%")
                    self.gpu_usage_bar.set_value(stats.gpu_usage_percent)

                # Update VRAM usage
                if hasattr(self, "gpu_vram_row"):
                    if stats.vram_total_mb > 0:
                        self.gpu_vram_row.set_subtitle(
                            f"{stats.vram_used_mb} / {stats.vram_total_mb} MB ({stats.mem_usage_percent}%)"
                        )
                        self.gpu_vram_bar.set_value(stats.mem_usage_percent)
                    else:
                        self.gpu_vram_row.set_subtitle("N/A")

                # Update GPU temperature with color coding
                if hasattr(self, "gpu_temp_row") and stats.gpu_temp_c > 0:
                    self.gpu_temp_row.set_subtitle(f"{stats.gpu_temp_c}°C")
                    self.gpu_temp_label.set_text(f"{stats.gpu_temp_c}°C")
                    # Color coding
                    self.gpu_temp_label.remove_css_class("temp-cool")
                    self.gpu_temp_label.remove_css_class("temp-warm")
                    self.gpu_temp_label.remove_css_class("temp-hot")
                    self.gpu_temp_label.remove_css_class("temp-critical")
                    if stats.gpu_temp_c < 50:
                        self.gpu_temp_label.add_css_class("temp-cool")
                    elif stats.gpu_temp_c < 70:
                        self.gpu_temp_label.add_css_class("temp-warm")
                    elif stats.gpu_temp_c < 85:
                        self.gpu_temp_label.add_css_class("temp-hot")
                    else:
                        self.gpu_temp_label.add_css_class("temp-critical")

                # Update power draw
                if hasattr(self, "gpu_power_draw_row"):
                    if stats.power_limit_w > 0:
                        self.gpu_power_draw_row.set_subtitle(
                            f"{stats.power_draw_w:.1f} / {stats.power_limit_w:.0f} W"
                        )
                    else:
                        self.gpu_power_draw_row.set_subtitle(
                            f"{stats.power_draw_w:.1f} W"
                        )

                # Update fan speed
                if hasattr(self, "gpu_fan_row"):
                    if stats.fan_speed_rpm > 0:
                        self.gpu_fan_row.set_subtitle(
                            f"{stats.fan_speed_rpm} RPM ({stats.fan_speed_percent}%)"
                        )
                    else:
                        self.gpu_fan_row.set_subtitle("N/A or Passive")

                # Update GPU switching status
                if (
                    hasattr(self, "gpu_power_row")
                    and self.gpu_controller.supergfxctl_available
                ):
                    switch_status = self.gpu_controller.get_switching_status()
                    self.gpu_power_row.set_subtitle(
                        switch_status.power_status.value.capitalize()
                    )
                    # Update badge
                    if hasattr(self, "gpu_power_badge"):
                        self.gpu_power_badge.set_label(
                            switch_status.power_status.value.upper()
                        )
                        self.gpu_power_badge.remove_css_class("warning-badge")
                        self.gpu_power_badge.remove_css_class("success-badge")
                        self.gpu_power_badge.remove_css_class("info-badge")
                        self.gpu_power_badge.remove_css_class("dim-label")
                        if switch_status.power_status == GpuPowerStatus.ACTIVE:
                            self.gpu_power_badge.add_css_class("warning-badge")
                        elif switch_status.power_status == GpuPowerStatus.SUSPENDED:
                            self.gpu_power_badge.add_css_class("success-badge")
                        elif switch_status.power_status == GpuPowerStatus.OFF:
                            self.gpu_power_badge.add_css_class("info-badge")
                        else:
                            self.gpu_power_badge.add_css_class("dim-label")
            except Exception as e:
                print(f"Error updating GPU stats: {e}")

        # --- Update Monitor Page ---
        if HAS_SYSTEM_MONITOR and hasattr(self, "sys_monitor") and self.sys_monitor:
            try:
                # CPU Stats
                cpu_stats = self.sys_monitor.get_cpu_stats()

                if hasattr(self, "mon_cpu_usage_row"):
                    self.mon_cpu_usage_row.set_subtitle(
                        f"{cpu_stats.usage_percent:.1f}%"
                    )
                    self.mon_cpu_usage_bar.set_value(cpu_stats.usage_percent)

                if hasattr(self, "mon_cpu_freq_row"):
                    self.mon_cpu_freq_row.set_subtitle(
                        f"{cpu_stats.current_freq_mhz:.0f} MHz"
                    )

                if hasattr(self, "mon_load_row"):
                    self.mon_load_row.set_subtitle(
                        f"{cpu_stats.load_1min:.2f}, {cpu_stats.load_5min:.2f}, {cpu_stats.load_15min:.2f}"
                    )

                # Per-core usage
                if hasattr(self, "mon_core_bars") and cpu_stats.core_usage:
                    for i, (bar, label) in enumerate(self.mon_core_bars):
                        if i < len(cpu_stats.core_usage):
                            usage = cpu_stats.core_usage[i]
                            bar.set_value(usage)
                            label.set_text(f"{usage:.0f}%")

                # Memory Stats
                mem_stats = self.sys_monitor.get_memory_stats()

                if hasattr(self, "mon_ram_row"):
                    self.mon_ram_row.set_subtitle(
                        f"{mem_stats.used_mb:,} / {mem_stats.total_mb:,} MB ({mem_stats.usage_percent:.1f}%)"
                    )
                    self.mon_ram_bar.set_value(mem_stats.usage_percent)

                if hasattr(self, "mon_ram_available_row"):
                    self.mon_ram_available_row.set_subtitle(
                        f"{mem_stats.available_mb:,} MB"
                    )

                if hasattr(self, "mon_ram_cached_row"):
                    self.mon_ram_cached_row.set_subtitle(
                        f"{mem_stats.cached_mb:,} MB / {mem_stats.buffers_mb:,} MB"
                    )

                if hasattr(self, "mon_swap_row"):
                    if mem_stats.swap_total_mb > 0:
                        self.mon_swap_row.set_subtitle(
                            f"{mem_stats.swap_used_mb:,} / {mem_stats.swap_total_mb:,} MB ({mem_stats.swap_usage_percent:.1f}%)"
                        )
                        self.mon_swap_bar.set_value(mem_stats.swap_usage_percent)
                    else:
                        self.mon_swap_row.set_subtitle("No swap configured")
                        self.mon_swap_bar.set_value(0)

                # Network Stats
                if hasattr(self, "mon_net_rows"):
                    net_stats = self.sys_monitor.get_network_stats()
                    for iface in net_stats:
                        if iface.interface in self.mon_net_rows:
                            rows = self.mon_net_rows[iface.interface]
                            rows["dl_row"].set_subtitle(
                                self.sys_monitor.format_bytes(iface.bytes_recv)
                            )
                            rows["ul_row"].set_subtitle(
                                self.sys_monitor.format_bytes(iface.bytes_sent)
                            )
                            rows["dl_rate"].set_text(
                                self.sys_monitor.format_bytes_rate(iface.recv_rate)
                            )
                            rows["ul_rate"].set_text(
                                self.sys_monitor.format_bytes_rate(iface.send_rate)
                            )

                            # Update status
                            status = "Connected" if iface.is_up else "Disconnected"
                            rows["expander"].set_subtitle(
                                f"{status} • {iface.ip_address or 'No IP'}"
                            )
                            rows["status_badge"].set_text(
                                "UP" if iface.is_up else "DOWN"
                            )

                # Uptime
                if hasattr(self, "mon_uptime_row"):
                    overview = self.sys_monitor.get_system_overview()
                    self.mon_uptime_row.set_subtitle(overview.uptime_str)

            except Exception as e:
                print(f"Error updating monitor stats: {e}")

        # Auto-profile switching on AC/Battery change
        config = self.load_config()
        if config.get("auto_profile_enabled", False):
            if self.last_ac_state is not None and self.last_ac_state != on_ac:
                # Power source changed
                if on_ac:
                    target_profile = config.get("auto_profile_ac", "performance")
                else:
                    target_profile = config.get("auto_profile_battery", "efficient")

                self.apply_auto_profile(target_profile, on_ac)

                # Also switch refresh rate if enabled
                if config.get("auto_refresh_enabled", False):
                    if on_ac:
                        rate = config.get("auto_refresh_ac", 120)
                    else:
                        rate = config.get("auto_refresh_battery", 60)
                    SystemUtils.set_refresh_rate(rate)
                    self.show_toast(f"Display set to {rate} Hz")

            self.last_ac_state = on_ac

        # Temperature throttling
        if config.get("temp_throttle_enabled", True) and cpu_temp:
            threshold = config.get("temp_threshold", 85)
            if cpu_temp >= threshold:
                # Throttle by switching to a lower power profile
                current = self.settings.get("current_power_profile", "balanced")
                if current in ["performance", "gaming", "maximum"]:
                    self.apply_auto_profile("balanced", on_ac)
                    self.show_toast(
                        f"⚠️ Temp throttling: {cpu_temp:.0f}°C → Balanced profile"
                    )

        # Session statistics tracking
        if HAS_SESSION_STATS:
            stats = get_session_stats()
            stats.add_sample(
                cpu_temp=cpu_temp,
                gpu_temp=gpu_temp,
                battery=battery,
                on_ac=on_ac,
                profile=current_profile,
            )

            # Update session stats display if visible
            if hasattr(self, "stats_duration_label"):
                self.stats_duration_label.set_text(stats.get_session_duration())
            if hasattr(self, "stats_max_cpu_label") and cpu_temp:
                summary = stats.get_summary()
                self.stats_max_cpu_label.set_text(f"{summary['cpu']['max_temp']}°C")
                self.stats_avg_cpu_label.set_text(f"{summary['cpu']['avg_temp']}°C")

        # Return True to keep the timeout active
        return True

    def apply_auto_profile(self, profile: str, on_ac: bool):
        """Apply profile automatically (called by auto-switching)"""
        # Validate profile against known profiles
        valid_profiles = [
            "emergency",
            "battery",
            "efficient",
            "balanced",
            "performance",
            "gaming",
            "maximum",
        ]
        if profile not in valid_profiles:
            print(f"Invalid auto-profile: {profile}")
            return

        if not SystemUtils.check_command_exists("pwrcfg"):
            print("pwrcfg not available for auto-profile switching")
            return

        try:
            result = subprocess.run(
                ["pkexec", "pwrcfg", profile],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.settings["current_power_profile"] = profile
                self.get_application().save_settings()
                # Notify user
                app = self.get_application()
                if hasattr(app, "notify"):
                    power_source = "AC Power" if on_ac else "Battery"
                    app.notify(
                        "Auto Profile Switch",
                        f"Switched to '{profile}' profile ({power_source})",
                    )
        except Exception as e:
            print(f"Auto-profile switch failed: {e}")

    def show_success_toast(self, message: str, timeout: int = 3):
        """Show a success toast notification (non-blocking)"""
        toast = Adw.Toast.new(f"✓ {message}")
        toast.set_timeout(timeout)
        self.toast_overlay.add_toast(toast)

    def show_error_toast(self, message: str, timeout: int = 5):
        """Show an error toast notification (non-blocking)"""
        toast = Adw.Toast.new(f"✗ {message}")
        toast.set_timeout(timeout)
        toast.set_priority(Adw.ToastPriority.HIGH)
        self.toast_overlay.add_toast(toast)

    def show_success_dialog(self, message):
        """Show success message - uses toast for quick feedback"""
        self.show_success_toast(message)

    def show_error_dialog(self, message):
        """Show error message - uses dialog for important errors"""
        # For long error messages, use a dialog; for short ones, use toast
        if len(message) > 100:
            dialog = Adw.MessageDialog.new(self)
            dialog.set_heading("Error")
            dialog.set_body(message)
            dialog.add_response("ok", "OK")
            dialog.set_default_response("ok")
            dialog.set_close_response("ok")
            dialog.present()
        else:
            self.show_error_toast(message)

    def show_preferences(self, action, param):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self)
        dialog.present()

    def show_shortcuts(self, action, param):
        """Show keyboard shortcuts dialog"""
        shortcuts = Gtk.ShortcutsWindow(transient_for=self, modal=True)

        # Shortcuts section
        section = Gtk.ShortcutsSection(section_name="shortcuts", title="Shortcuts")
        section.set_visible(True)

        # General shortcuts group
        general_group = Gtk.ShortcutsGroup(title="General")
        general_group.set_visible(True)

        shortcuts_list = [
            ("<Control>q", "Quit Application"),
            ("F5", "Refresh Status"),
        ]

        for accel, title in shortcuts_list:
            shortcut = Gtk.ShortcutsShortcut(accelerator=accel, title=title)
            shortcut.set_visible(True)
            general_group.append(shortcut)

        section.append(general_group)
        shortcuts.append(section)
        shortcuts.present()

    def show_about(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Linux Armoury",
            application_icon="applications-system-symbolic",
            developer_name="th3cavalry",
            version=getattr(Config, "VERSION", "1.0.0"),
            developers=["th3cavalry"],
            copyright="© 2025 th3cavalry",
            website="https://github.com/th3cavalry/Linux-Armoury",
            issue_url="https://github.com/th3cavalry/Linux-Armoury/issues",
            license_type=Gtk.License.GPL_3_0,
            comments="A modern control center for ASUS ROG laptops on Linux.\n\nInspired by ROG Control Center and G-Helper.",
        )
        # Add credits
        about.add_credit_section(
            "Powered By",
            [
                "asusctl/asusd",
                "supergfxctl",
                "GTK4/libadwaita",
            ],
        )
        about.present()


class PreferencesDialog(Adw.PreferencesWindow):
    """Preferences dialog window"""

    def __init__(self, parent):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Preferences")

        # General preferences page
        page = Adw.PreferencesPage()
        page.set_title("General")
        page.set_icon_name("preferences-system")

        # Startup group
        startup_group = Adw.PreferencesGroup()
        startup_group.set_title("Startup")

        # Autostart switch
        autostart_row = Adw.ActionRow()
        autostart_row.set_title("Start on Boot")
        autostart_row.set_subtitle("Launch Linux Armoury when system starts")

        autostart_switch = Gtk.Switch()
        autostart_switch.set_valign(Gtk.Align.CENTER)
        autostart_switch.set_active(parent.settings.get("autostart", False))
        autostart_switch.connect("notify::active", self.on_autostart_toggled, parent)
        autostart_row.add_suffix(autostart_switch)

        startup_group.add(autostart_row)
        page.add(startup_group)

        # Behavior group
        behavior_group = Adw.PreferencesGroup()
        behavior_group.set_title("Behavior")

        # Minimize to tray switch
        minimize_row = Adw.ActionRow()
        minimize_row.set_title("Minimize to System Tray")
        minimize_row.set_subtitle("Keep running in background when window is closed")

        minimize_switch = Gtk.Switch()
        minimize_switch.set_valign(Gtk.Align.CENTER)
        minimize_switch.set_active(parent.settings.get("minimize_to_tray", True))
        minimize_switch.connect("notify::active", self.on_minimize_toggled, parent)
        minimize_row.add_suffix(minimize_switch)

        behavior_group.add(minimize_row)

        # Auto-profile switching
        auto_profile_row = Adw.ActionRow()
        auto_profile_row.set_title("Auto Profile Switching")
        auto_profile_row.set_subtitle(
            "Automatically switch profiles on AC/Battery change"
        )

        auto_profile_switch = Gtk.Switch()
        auto_profile_switch.set_valign(Gtk.Align.CENTER)
        auto_profile_switch.set_active(
            parent.settings.get("auto_profile_switch", False)
        )
        auto_profile_switch.connect(
            "notify::active", self.on_auto_profile_toggled, parent
        )
        auto_profile_row.add_suffix(auto_profile_switch)

        behavior_group.add(auto_profile_row)
        page.add(behavior_group)

        self.add(page)

    def on_autostart_toggled(self, switch, param, parent):
        """Handle autostart toggle"""
        enabled = switch.get_active()
        parent.settings["autostart"] = enabled
        parent.get_application().save_settings()
        self.update_autostart(enabled)

    def on_minimize_toggled(self, switch, param, parent):
        """Handle minimize to tray toggle"""
        enabled = switch.get_active()
        parent.settings["minimize_to_tray"] = enabled
        parent.get_application().save_settings()

    def on_auto_profile_toggled(self, switch, param, parent):
        """Handle auto profile switching toggle"""
        enabled = switch.get_active()
        parent.settings["auto_profile_switch"] = enabled
        parent.get_application().save_settings()

    def update_autostart(self, enabled):
        """Update autostart desktop file"""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        autostart_file = os.path.join(autostart_dir, "linux-armoury.desktop")

        if enabled:
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Linux Armoury
Comment=ASUS GZ302EA Control Center
Exec={sys.argv[0]}
Icon=applications-system
Terminal=false
Categories=System;Settings;
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
            with open(autostart_file, "w") as f:
                f.write(desktop_content)
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Linux Armoury - ROG Control Center")
    parser.add_argument(
        "--minimized", "-m", action="store_true", help="Start minimized to system tray"
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"Linux Armoury {Config.VERSION}"
    )

    # Parse known args to avoid conflicts with GTK args
    args, unknown = parser.parse_known_args()

    # Create app and set startup preference
    app = LinuxArmouryApp()
    if args.minimized:
        app.settings["start_minimized"] = True

    # Run with remaining args for GTK
    return app.run([sys.argv[0]] + unknown)


if __name__ == "__main__":
    sys.exit(main())
