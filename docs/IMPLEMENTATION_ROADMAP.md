# Linux Armoury - Implementation Roadmap

## Quick Summary

**Current Status**: Feature-complete gaming control center (Grade: B+)
**Goal**: Production-ready, premium system management tool (Grade: A+)
**Timeline**: 4 phases over 2-4 weeks

---

## Phase 1: Foundation Polish (2-3 days)
**Goal**: Improve stability, user experience, and code quality

### 1.1 Settings Persistence ⭐⭐⭐
**Impact**: High | **Effort**: Low | **Priority**: P0

**Files to create/modify**:
- `src/linux_armoury/config_manager.py` (new)
- `src/linux_armoury/gui.py` (modify)

**Implementation**:
```python
# config_manager.py
import json
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "linux-armoury"
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_settings(self):
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return self.get_defaults()

    def save_settings(self, settings):
        self.config_file.write_text(json.dumps(settings, indent=2))

    def get_defaults(self):
        return {
            "auto_profile_switching": False,
            "last_tdp_profile": "Balanced",
            "rgb_brightness": 50,
            "rgb_color": "#ff0066",
            "battery_charge_limit": 80,
            "fan_curve": "Balanced",
            "window_size": [1000, 650],
            "startup_section": "Dashboard"
        }
```

**Testing**:
```bash
# Test config save/load
python -c "
from src.linux_armoury.config_manager import ConfigManager
cm = ConfigManager()
cm.save_settings({'test': 'value'})
print(cm.load_settings())
"
```

**Benefits**:
- Settings persist across restarts
- Better user experience
- Foundation for profiles system

---

### 1.2 Logging Framework ⭐⭐⭐
**Impact**: Medium | **Effort**: Low | **Priority**: P0

**Files to modify**:
- `src/linux_armoury/gui.py`
- All module files in `src/linux_armoury/modules/`

**Implementation**:
```python
# Add to gui.py
import logging
from pathlib import Path

def setup_logging():
    log_dir = Path.home() / ".config" / "linux-armoury"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "linux-armoury.log"),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger('LinuxArmoury')

# In App.__init__:
self.logger = setup_logging()
self.logger.info("Linux Armoury started")
```

**Replace print statements**:
```bash
# Find all print statements in modules
grep -r "print(" src/linux_armoury/ | wc -l
```

**Benefits**:
- Professional debugging
- User troubleshooting easier
- Better error tracking

---

### 1.3 Toast Notifications ⭐⭐⭐
**Impact**: High | **Effort**: Medium | **Priority**: P1

**Files to create**:
- `src/linux_armoury/widgets/toast.py` (new)

**Implementation**:
```python
# toast.py
import customtkinter as ctk
from typing import Literal

class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, message: str, type: Literal["success", "error", "info", "warning"] = "info"):
        super().__init__(master, corner_radius=8)

        # Color scheme
        colors = {
            "success": ("#10b981", "#065f46"),
            "error": ("#ef4444", "#991b1b"),
            "info": ("#3b82f6", "#1e3a8a"),
            "warning": ("#f59e0b", "#92400e")
        }

        bg, text = colors[type]
        self.configure(fg_color=bg)

        # Icon
        icons = {"success": "✓", "error": "✗", "info": "ℹ", "warning": "⚠"}
        icon_label = ctk.CTkLabel(self, text=icons[type], font=("Arial", 18, "bold"), text_color=text)
        icon_label.pack(side="left", padx=(10, 5))

        # Message
        msg_label = ctk.CTkLabel(self, text=message, font=("Arial", 12), text_color=text)
        msg_label.pack(side="left", padx=(5, 10), pady=10)

        # Auto-dismiss after 5 seconds
        self.after(5000, self.dismiss)

    def show(self):
        # Position at top-right
        self.place(relx=0.98, rely=0.02, anchor="ne")

        # Slide in animation
        self.attributes("-alpha", 0.0)
        self.fade_in()

    def fade_in(self, alpha=0.0):
        alpha += 0.1
        if alpha <= 1.0:
            self.attributes("-alpha", alpha)
            self.after(30, lambda: self.fade_in(alpha))

    def dismiss(self):
        self.fade_out()

    def fade_out(self, alpha=1.0):
        alpha -= 0.1
        if alpha >= 0:
            self.attributes("-alpha", alpha)
            self.after(30, lambda: self.fade_out(alpha))
        else:
            self.destroy()

# Usage in gui.py
def show_toast(self, message, type="info"):
    toast = ToastNotification(self, message, type)
    toast.show()

# Example calls:
# self.show_toast("TDP profile changed to Gaming", "success")
# self.show_toast("Failed to set GPU mode", "error")
```

**Benefits**:
- Visual feedback for actions
- Professional UX
- No modal dialogs blocking workflow

---

### 1.4 Keyboard Shortcuts ⭐⭐
**Impact**: Medium | **Effort**: Low | **Priority**: P1

**Files to modify**:
- `src/linux_armoury/gui.py`

**Implementation**:
```python
# In App.__init__, add:
def setup_keybindings(self):
    # Navigation shortcuts
    self.bind("<Control-1>", lambda e: self.show_dashboard())
    self.bind("<Control-2>", lambda e: self.show_aura())
    self.bind("<Control-3>", lambda e: self.show_performance())
    self.bind("<Control-4>", lambda e: self.show_battery())
    self.bind("<Control-5>", lambda e: self.show_fans())
    self.bind("<Control-6>", lambda e: self.show_settings())

    # Quick actions
    self.bind("<Control-q>", lambda e: self.quit())
    self.bind("<Control-r>", lambda e: self.refresh_stats())
    self.bind("<F5>", lambda e: self.refresh_stats())

    # Profile shortcuts
    self.bind("<Alt-1>", lambda e: self.set_tdp_profile("Silent"))
    self.bind("<Alt-2>", lambda e: self.set_tdp_profile("Balanced"))
    self.bind("<Alt-3>", lambda e: self.set_tdp_profile("Gaming"))
```

**Documentation**:
Create help dialog showing shortcuts

**Benefits**:
- Power user efficiency
- Professional application feel
- Faster workflow

---

## Phase 2: Visual Excellence (3-5 days)
**Goal**: Add real-time graphs, improve aesthetics, add system tray

### 2.1 Real-Time Monitoring Graphs ⭐⭐⭐
**Impact**: High | **Effort**: High | **Priority**: P0

**Files to create/modify**:
- `src/linux_armoury/widgets/monitoring_graph.py` (new)
- `src/linux_armoury/gui.py` (modify SystemMonitorCard)

**Implementation**:
```python
# monitoring_graph.py
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import numpy as np

class LiveMonitoringGraph(ctk.CTkFrame):
    def __init__(self, master, title: str, max_points: int = 60):
        super().__init__(master, fg_color="#2a2a2a", corner_radius=8)

        self.max_points = max_points
        self.data = deque([0] * max_points, maxlen=max_points)

        # Title
        title_label = ctk.CTkLabel(self, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(10, 5))

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 2.5), facecolor='#2a2a2a', dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a1a1a')

        # Style
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#444444')
        self.ax.spines['bottom'].set_color('#444444')
        self.ax.tick_params(colors='#888888', labelsize=8)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, max_points)
        self.ax.grid(True, alpha=0.2, color='#444444')

        # Initial line
        self.line, = self.ax.plot([], [], color='#ff0066', linewidth=2)

        # Embed in CustomTkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Current value label
        self.value_label = ctk.CTkLabel(self, text="0%", font=("Arial", 12, "bold"), text_color="#ff0066")
        self.value_label.pack(pady=(0, 10))

    def update_data(self, value: float):
        self.data.append(value)

        # Update line
        x = np.arange(len(self.data))
        self.line.set_data(x, list(self.data))

        # Update label
        self.value_label.configure(text=f"{value:.1f}%")

        # Redraw
        self.canvas.draw_idle()
```

**Integration into Dashboard**:
```python
# In show_dashboard():
cpu_graph = LiveMonitoringGraph(main_content, "CPU Usage")
cpu_graph.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

gpu_graph = LiveMonitoringGraph(main_content, "GPU Usage")
gpu_graph.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# In update_loop():
cpu_graph.update_data(cpu_percent)
gpu_graph.update_data(gpu_percent)
```

**Benefits**:
- Professional monitoring visualization
- Easier to spot trends and issues
- More informative than progress bars

---

### 2.2 System Tray Integration ⭐⭐⭐
**Impact**: High | **Effort**: Medium | **Priority**: P1

**Dependencies**:
```bash
pip install pystray
```

**Files to create**:
- `src/linux_armoury/tray_manager.py` (new)

**Implementation**:
```python
# tray_manager.py
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

class TrayManager:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.current_profile = "Balanced"

    def create_icon_image(self):
        # Create simple icon
        img = Image.new('RGB', (64, 64), color='#ff0066')
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "LA", fill='white')
        return img

    def create_menu(self):
        return Menu(
            MenuItem("Show Dashboard", self.show_app),
            Menu.SEPARATOR,
            MenuItem("Quick Profiles", Menu(
                MenuItem("Silent (25W)", lambda: self.set_profile("Silent")),
                MenuItem("Balanced (40W)", lambda: self.set_profile("Balanced")),
                MenuItem("Gaming (70W)", lambda: self.set_profile("Gaming")),
                MenuItem("Turbo (90W)", lambda: self.set_profile("Turbo"))
            )),
            Menu.SEPARATOR,
            MenuItem(f"Current: {self.current_profile}", None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Exit", self.quit_app)
        )

    def start(self):
        self.icon = Icon(
            "Linux Armoury",
            self.create_icon_image(),
            "Linux Armoury",
            menu=self.create_menu()
        )
        self.icon.run_detached()

    def show_app(self):
        self.app.deiconify()
        self.app.lift()

    def set_profile(self, profile):
        self.app.set_tdp_profile_by_name(profile)
        self.current_profile = profile
        self.icon.menu = self.create_menu()  # Update menu

    def quit_app(self):
        self.icon.stop()
        self.app.quit()
```

**Integration**:
```python
# In gui.py App.__init__:
self.tray = TrayManager(self)
self.tray.start()

# Override window close to minimize to tray
self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

def minimize_to_tray(self):
    self.withdraw()  # Hide window
```

**Benefits**:
- Background monitoring
- Quick profile switching
- Standard desktop integration

---

### 2.3 Profile Presets System ⭐⭐⭐
**Impact**: High | **Effort**: Medium | **Priority**: P1

**Files to create**:
- `src/linux_armoury/profile_manager.py` (new)

**Implementation**:
```python
# profile_manager.py
from dataclasses import dataclass
from typing import Optional
import json
from pathlib import Path

@dataclass
class SystemProfile:
    name: str
    tdp_watts: int
    gpu_mode: str
    fan_curve: str
    rgb_brightness: int
    rgb_effect: str
    battery_limit: int
    refresh_rate: Optional[int] = None

class ProfileManager:
    BUILTIN_PROFILES = {
        "Gaming": SystemProfile(
            name="Gaming",
            tdp_watts=70,
            gpu_mode="Ultimate",
            fan_curve="Performance",
            rgb_brightness=100,
            rgb_effect="Rainbow",
            battery_limit=100,
            refresh_rate=165
        ),
        "Work": SystemProfile(
            name="Work",
            tdp_watts=40,
            gpu_mode="Hybrid",
            fan_curve="Balanced",
            rgb_brightness=50,
            rgb_effect="Static",
            battery_limit=80,
            refresh_rate=60
        ),
        "Battery": SystemProfile(
            name="Battery",
            tdp_watts=18,
            gpu_mode="Eco",
            fan_curve="Quiet",
            rgb_brightness=0,
            rgb_effect="Off",
            battery_limit=80,
            refresh_rate=60
        ),
        "Silent": SystemProfile(
            name="Silent",
            tdp_watts=30,
            gpu_mode="Hybrid",
            fan_curve="Silent",
            rgb_brightness=20,
            rgb_effect="Breathe",
            battery_limit=80,
            refresh_rate=60
        )
    }

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "linux-armoury" / "profiles"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def apply_profile(self, profile: SystemProfile, app):
        """Apply all settings from a profile"""
        # TDP
        app.set_tdp(profile.tdp_watts)

        # GPU mode
        if hasattr(app, 'gpu_controller'):
            app.gpu_controller.set_mode(profile.gpu_mode)

        # Fan curve
        if hasattr(app, 'fan_controller'):
            app.fan_controller.set_curve(profile.fan_curve)

        # RGB
        if hasattr(app, 'keyboard_controller'):
            app.keyboard_controller.set_brightness(profile.rgb_brightness)
            app.keyboard_controller.set_effect(profile.rgb_effect)

        # Battery
        if hasattr(app, 'battery_controller'):
            app.battery_controller.set_charge_limit(profile.battery_limit)

        # Show notification
        app.show_toast(f"Profile '{profile.name}' applied", "success")

    def save_custom_profile(self, name: str, profile: SystemProfile):
        file_path = self.config_dir / f"{name}.json"
        file_path.write_text(json.dumps(profile.__dict__, indent=2))

    def load_custom_profile(self, name: str) -> Optional[SystemProfile]:
        file_path = self.config_dir / f"{name}.json"
        if file_path.exists():
            data = json.loads(file_path.read_text())
            return SystemProfile(**data)
        return None

    def list_all_profiles(self):
        builtin = list(self.BUILTIN_PROFILES.keys())
        custom = [f.stem for f in self.config_dir.glob("*.json")]
        return {"builtin": builtin, "custom": custom}
```

**UI Addition to Dashboard**:
```python
# In show_dashboard():
profiles_card = ctk.CTkFrame(main_content, fg_color="#2a2a2a", corner_radius=8)
profiles_card.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

title = ctk.CTkLabel(profiles_card, text="🎮 Quick Profiles", font=("Arial", 16, "bold"))
title.pack(pady=(15, 10))

btn_frame = ctk.CTkFrame(profiles_card, fg_color="transparent")
btn_frame.pack(fill="x", padx=20, pady=(0, 15))

for i, (name, profile) in enumerate(self.profile_manager.BUILTIN_PROFILES.items()):
    btn = ctk.CTkButton(
        btn_frame,
        text=f"{name}\n{profile.tdp_watts}W",
        command=lambda p=profile: self.profile_manager.apply_profile(p, self)
    )
    btn.grid(row=0, column=i, padx=5, sticky="ew")
```

**Benefits**:
- One-click system configuration
- Consistent settings
- Easy to share profiles

---

## Phase 3: Hardware Mastery (5-7 days)
**Goal**: Complete hardware integration, RGB effects, fan curves

### 3.1 asusctl RGB Effects ⭐⭐⭐
**Impact**: High | **Effort**: High | **Priority**: P0

**Research needed**: asusctl D-Bus API documentation

**Files to modify**:
- `src/linux_armoury/modules/keyboard_control.py`

**Implementation outline**:
```python
# keyboard_control.py additions
import dbus

class AuraEffectsController:
    EFFECTS = [
        "Static", "Breathe", "Strobe", "Rainbow", "Star",
        "Rain", "Highlight", "Laser", "Ripple", "Pulse",
        "Comet", "Flash", "Mix"
    ]

    def __init__(self):
        try:
            self.bus = dbus.SystemBus()
            self.aura = self.bus.get_object(
                'xyz.ljones.Asusd',
                '/xyz/ljones/Asusd/Led'
            )
            self.interface = dbus.Interface(
                self.aura,
                'xyz.ljones.Asusd.Led'
            )
            self.available = True
        except:
            self.available = False

    def set_effect(self, effect_name: str, speed: int = 2, colors: list = None):
        if not self.available:
            return False

        try:
            # Call D-Bus method to set effect
            self.interface.SetKeyboardEffect(effect_name, speed, colors or [])
            return True
        except Exception as e:
            print(f"Failed to set effect: {e}")
            return False
```

**Testing**:
```bash
# Test D-Bus availability
busctl --system tree xyz.ljones.Asusd

# Test method calls
busctl --system call xyz.ljones.Asusd /xyz/ljones/Asusd/Led xyz.ljones.Asusd.Led SetKeyboardEffect
```

---

### 3.2 Interactive Fan Curve Editor ⭐⭐
**Impact**: Medium | **Effort**: High | **Priority**: P2

**Files to create**:
- `src/linux_armoury/widgets/fan_curve_editor.py` (new)

**Implementation**: Draggable matplotlib canvas with 8 control points

---

### 3.3 Power Usage Monitor ⭐⭐
**Impact**: Medium | **Effort**: Low | **Priority**: P1

**Files to modify**:
- `src/linux_armoury/modules/battery_control.py`

**Implementation**:
```python
def get_power_consumption():
    """Get current power draw in watts"""
    try:
        power_now_path = Path("/sys/class/power_supply/BAT0/power_now")
        if power_now_path.exists():
            microwatts = int(power_now_path.read_text().strip())
            return microwatts / 1_000_000  # Convert to watts
    except:
        pass
    return None

def estimate_battery_life(power_watts, battery_percent, battery_capacity_wh):
    """Estimate remaining runtime"""
    if power_watts and power_watts > 0:
        remaining_wh = (battery_percent / 100) * battery_capacity_wh
        hours = remaining_wh / power_watts
        return hours
    return None
```

---

## Phase 4: Advanced Features (7-14 days)
**Goal**: Automation, game detection, benchmarking

### 4.1 Scheduler/Automation ⭐⭐⭐
**Impact**: High | **Effort**: High | **Priority**: P1

**Files to create**:
- `src/linux_armoury/scheduler.py` (new)

**Features**:
- Time-based profile switching
- Battery level triggers
- Process-based triggers

---

### 4.2 Game Detection ⭐⭐⭐
**Impact**: High | **Effort**: Medium | **Priority**: P1

**Implementation**:
```python
class GameDetector:
    GAME_PROCESSES = [
        "steam", "steamwebhelper", "gameoverlayui",
        "lutris", "heroic", "legendary",
        "wine", "wine64", "proton",
        "dxvk", "vkd3d"
    ]

    def detect_game_running(self):
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in self.GAME_PROCESSES:
                return True
        return False
```

---

### 4.3 Performance Benchmarking ⭐⭐
**Impact**: Medium | **Effort**: High | **Priority**: P2

**Features**:
- CPU stress test (stress-ng integration)
- GPU benchmark
- Thermal testing
- Generate reports

---

## Summary

**Immediate Priorities (Week 1)**:
1. Settings persistence ✅
2. Logging framework ✅
3. Toast notifications ✅
4. Real-time graphs ✅

**High-Value Next (Week 2)**:
1. System tray ✅
2. Profile presets ✅
3. RGB effects ✅
4. Keyboard shortcuts ✅

**Advanced (Weeks 3-4)**:
1. Game detection ✅
2. Scheduler ✅
3. Power monitoring ✅
4. Benchmarking ✅

**Estimated Total Time**: 2-4 weeks
**Recommended Approach**: Implement Phase 1 first for immediate value, then iterate through phases
