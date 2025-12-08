# GUI Refactor Progress - G-Helper/Armoury Crate Inspired

## Design Philosophy
Creating a gaming control center inspired by ASUS ROG Armoury Crate and G-Helper, with:
- Clean, modern dark interface with ROG pink accent (#ff0066)
- Functional hardware controls, not just mockup UI
- Real-time system monitoring with live data
- Integration with existing backend modules (asusctl, keyboard control, fan control, etc.)

## ✅ Completed Features

### 1. Core GUI Framework
- [x] CustomTkinter framework implementation
- [x] Dark color scheme (#0d0d0d sidebar, #1a1a1a main, #242424 cards)
- [x] ROG pink accent color (#ff0066) for highlights
- [x] Sidebar navigation with 6 sections
- [x] Responsive grid layout with cards

### 2. Navigation Sections
- [x] Dashboard - Main overview with quick actions
- [x] Aura RGB - Keyboard lighting control
- [x] Performance - CPU/GPU tuning
- [x] Fans - Fan curve editor (placeholder)
- [x] Battery - Charge limit settings
- [x] Settings - App preferences

### 3. System Monitoring (Real Data!)
- [x] SystemMonitor integration from modules/system_monitor.py
- [x] Real CPU usage percentage (updated every 2 seconds)
- [x] CPU temperature from hwmon/thermal zones
- [x] GPU temperature (NVIDIA and AMD detection)
- [x] Progress bars with color coding (pink for CPU, green for GPU)
- [x] Background monitoring thread

### 4. Performance Mode Control (Real Functionality!)
- [x] AsusdClient integration from modules/asusd_client.py
- [x] Three performance modes: Silent/Balanced/Turbo
- [x] Maps to ThrottlePolicy enum (QUIET/BALANCED/PERFORMANCE)
- [x] Gets current mode from asusctl on startup
- [x] Sets throttle policy when mode button clicked
- [x] Visual feedback with accent color for selected mode
- [x] Graceful degradation when asusd not available

### 5. UI Components
- [x] PerformanceCard component with mode switching
- [x] SystemMonitorCard with CPU/GPU stats display
- [x] Quick Actions card with common controls
- [x] Smooth hover effects and transitions
- [x] Consistent corner radius (8px) and spacing

## 🚧 In Progress / Planned Features

### 1. Aura RGB Control (Backend exists, needs UI connection)
- [ ] Connect to KeyboardController from modules/keyboard_control.py
- [ ] Implement 13 AuraEffect options (Static, Breathing, Rainbow, etc.)
- [ ] Add color picker using RGB preset colors
- [ ] Brightness slider connected to sysfs
- [ ] Real-time effect preview

### 2. GPU Mode Switching (Backend exists)
- [ ] Connect to gpu_control module
- [ ] Implement GpuMode selector (Hybrid/Integrated/Dedicated/Optimized)
- [ ] Show current GPU mode and power consumption
- [ ] Warning dialogs for modes requiring reboot
- [ ] Visual indicator for active GPU

### 3. Fan Curve Editor (Backend exists)
- [ ] Connect to fan_control module
- [ ] Create interactive fan curve graph with matplotlib
- [ ] Allow editing temperature threshold points
- [ ] Show current fan RPM in real-time
- [ ] Apply/Revert buttons with confirmation

### 4. Battery Settings (Backend exists)
- [ ] Connect to battery_control module
- [ ] Implement charge limit slider (60-100%)
- [ ] Show current battery health
- [ ] Display estimated cycles
- [ ] Battery conservation mode toggle

### 5. Advanced Performance Tuning
- [ ] Connect to overclocking_control module
- [ ] CPU voltage offset slider
- [ ] GPU voltage offset slider
- [ ] Frequency limit controls
- [ ] Safety warnings and confirmations
- [ ] Stress test integration

### 6. Enhanced System Monitoring
- [ ] Add RAM usage stats (MemoryStats from system_monitor)
- [ ] Disk I/O monitoring
- [ ] Network bandwidth graphs
- [ ] Per-core CPU usage display
- [ ] Historical graphs (last 60 seconds)

### 7. Display Controls
- [ ] Refresh rate selector (60Hz/120Hz/144Hz/165Hz)
- [ ] Panel overdrive toggle
- [ ] G-Sync/FreeSync status
- [ ] Display backend detection (X11/Wayland)

### 8. Additional Features
- [ ] Anime Matrix control (if hardware detected)
- [ ] Custom profiles (save/load)
- [ ] System tray integration
- [ ] Startup with system option
- [ ] Keyboard shortcuts
- [ ] Export/import settings

## 🎨 Design Details

### Color Palette
```
Background Dark:    #0d0d0d (sidebar)
Background Main:    #1a1a1a (main area)
Background Card:    #242424 (cards/panels)
Background Hover:   #2d2d2d (hover states)
Accent (ROG Pink):  #ff0066 (primary actions)
Accent Hover:       #cc0052 (hover accent)
Text Primary:       #ffffff (titles)
Text Secondary:     #b3b3b3 (labels)
Success (Green):    #00ff88 (GPU, positive)
Warning (Orange):   #ffaa00 (alerts)
```

### Typography
- Titles: Segoe UI, 24pt, Bold
- Subtitles: Segoe UI, 16pt, Bold
- Body: Segoe UI, 12pt, Regular
- Labels: Segoe UI, 10pt, Regular

### Layout
- Sidebar: 200px fixed width
- Main content: 20px padding
- Card spacing: 10px
- Corner radius: 8px
- Button height: 35-40px

## 📊 Code Statistics

### Current Implementation
- **gui.py**: ~600 lines (complete rewrite from 5305-line GTK version)
- **Backend modules integrated**: 2/9 (system_monitor, asusd_client)
- **Backend modules available**: 9 total
  - ✅ system_monitor.py - Integrated
  - ✅ asusd_client.py - Integrated
  - ⏳ keyboard_control.py - Ready to integrate
  - ⏳ fan_control.py - Ready to integrate
  - ⏳ gpu_control.py - Ready to integrate
  - ⏳ battery_control.py - Ready to integrate
  - ⏳ overclocking_control.py - Ready to integrate
  - ⏳ hardware_detection.py - Can be used for feature detection
  - ⏳ session_stats.py - Can be used for usage statistics

### Test Results
- ✅ GUI launches without errors
- ✅ System monitoring displays real CPU usage
- ✅ Temperature sensors detected and displayed
- ✅ Performance mode switching works (when asusd available)
- ✅ Graceful degradation in demo mode
- ✅ Background monitoring thread stable (2s refresh)

## 🔄 Next Steps Priority

1. **Aura RGB Integration** - Most requested feature, backend ready
2. **GPU Mode Switching** - Important for gaming laptops
3. **Fan Curve Editor** - Essential for thermal management
4. **Battery Charge Limit** - Simple to implement, high value
5. **Enhanced Monitoring** - Add RAM/Disk/Network stats
6. **Overclocking UI** - For advanced users

## 🐛 Known Issues

1. GPU usage percentage currently shows 0% (need proper GPU monitoring)
2. Demo mode uses random data (intended for systems without asusctl)
3. No error notifications in UI (errors only printed to console)
4. Quick Actions buttons are placeholders (need implementation)

## 📝 Notes

- Designed for 1000x650 window (optimized for 1080p displays)
- Runs at 30 FPS for smooth UI (2s monitoring refresh)
- Threaded monitoring prevents UI blocking
- All D-Bus operations are wrapped in try/except for stability
- Module imports use HAS_MODULES flag for graceful degradation

## 🎯 Goal: Full Feature Parity with G-Helper

G-Helper features to implement:
- [x] Performance modes (Silent/Balanced/Turbo) ✅
- [ ] GPU modes (Eco/Standard/Ultimate/Optimized)
- [ ] Custom fan curves
- [ ] RGB keyboard control with 13 effects
- [ ] Battery charge limits
- [ ] CPU/GPU monitoring
- [ ] Panel overdrive toggle
- [ ] Refresh rate selector
- [ ] Power/TDP display
- [ ] ASUS mouse settings (if detected)
- [ ] Anime Matrix control (if hardware detected)
