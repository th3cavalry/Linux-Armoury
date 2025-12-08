# Linux Armoury - Enhancements Integration Guide

## Overview

This guide explains how to integrate all the new enhancement features into the existing Linux Armoury GUI.

## What Has Been Created

### 1. Core Modules

#### `src/linux_armoury/config_manager.py`
- **Purpose**: Persistent settings storage
- **Features**:
  - Saves/loads user preferences to `~/.config/linux-armoury/settings.json`
  - Exports/imports configuration
  - Default values for all settings
  - Automatic merging of new settings with saved config

#### `src/linux_armoury/profile_manager.py`
- **Purpose**: System profile management
- **Features**:
  - 6 built-in profiles (Gaming, Balanced, Work, Battery Saver, Silent, Turbo)
  - Custom profile save/load/delete
  - Profile export/import
  - One-click apply all settings

#### `src/linux_armoury/enhancements.py`
- **Purpose**: Integration layer for all enhancements
- **Features**:
  - `EnhancedAppMixin` class for easy integration
  - Logging setup function
  - Keyboard shortcuts
  - Window geometry save/restore
  - Profile and graph creation helpers

### 2. Widget Modules

#### `src/linux_armoury/widgets/toast.py`
- **Classes**: `ToastNotification`, `ToastManager`
- **Purpose**: In-app notifications
- **Features**:
  - 4 types: success (green), error (red), info (blue), warning (orange)
  - Auto-dismiss after 5 seconds (configurable)
  - Stacking support (max 5 toasts)
  - Fade in/out animations

#### `src/linux_armoury/widgets/monitoring_graph.py`
- **Classes**: `LiveMonitoringGraph`, `MultiGraphPanel`
- **Purpose**: Real-time data visualization
- **Features**:
  - Live matplotlib graphs
  - 60-second history (configurable)
  - Min/Avg/Max statistics
  - Fill-under-curve visualization
  - Multi-graph panel support

### 3. Documentation

#### `ENHANCEMENT_RECOMMENDATIONS.md`
- Complete feature descriptions
- Implementation details with code examples
- Priority rankings
- Benefits analysis

#### `IMPLEMENTATION_ROADMAP.md`
- 4-phase implementation plan
- Time estimates
- Testing procedures
- Success criteria

#### `IMPROVEMENT_SUMMARY.md`
- Executive summary
- Before/after comparisons
- Top 10 improvements
- Timeline recommendations

## Integration Steps

### Step 1: Modify gui.py Imports

Add at the top of `src/linux_armoury/gui.py`:

```python
# Add to existing imports
from .enhancements import EnhancedAppMixin, setup_logging, show_keyboard_shortcuts_dialog
from .widgets import ToastManager, LiveMonitoringGraph, MultiGraphPanel
from .config_manager import ConfigManager
from .profile_manager import ProfileManager
```

### Step 2: Modify App Class

Change the App class definition:

```python
# OLD:
class App(ctk.CTk):

# NEW:
class App(ctk.CTk, EnhancedAppMixin):
```

### Step 3: Add Enhancement Initialization

In `App.__init__()`, add after existing initialization:

```python
def __init__(self):
    super().__init__()

    # ... existing initialization code ...

    # Initialize enhancements (ADD THIS)
    self.init_enhancements()  # From EnhancedAppMixin

    # ... rest of initialization ...
```

### Step 4: Replace Progress Bars with Graphs (Optional)

In `show_dashboard()` method, replace progress bars:

```python
# OLD:
cpu_bar = ctk.CTkProgressBar(...)

# NEW:
# Create graphs panel
self.graphs_panel = self.create_monitoring_graphs(main_content)
if self.graphs_panel:
    self.graphs_panel.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
```

### Step 5: Update Monitoring Loop

In `update_loop()` method, update graphs:

```python
def update_loop(self):
    while self.running:
        try:
            # ... existing monitoring code ...

            # Update graphs if they exist
            if hasattr(self, 'graphs_panel') and self.graphs_panel:
                self.graphs_panel.update({
                    'cpu': cpu_percent,
                    'gpu': gpu_percent
                })

            # ... rest of loop ...
        except Exception as e:
            self.logger.error(f"Update loop error: {e}")

        time.sleep(2)
```

### Step 6: Replace Print Statements with Logging

Find all `print()` calls and replace:

```python
# OLD:
print(f"TDP set to {watts}W")

# NEW:
self.logger.info(f"TDP set to {watts}W")
self.show_toast(f"TDP set to {watts}W", "success")
```

### Step 7: Add Profile Selector to Dashboard

In `show_dashboard()`, add:

```python
# Add profile selector
profile_selector = self.create_profile_selector(main_content)
if profile_selector:
    profile_selector.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
```

### Step 8: Add Keyboard Shortcuts to Settings

In `show_settings()`, add a button:

```python
shortcuts_btn = ctk.CTkButton(
    settings_frame,
    text="⌨️ View Keyboard Shortcuts",
    command=lambda: show_keyboard_shortcuts_dialog(self),
    fg_color="#ff0066",
    hover_color="#cc0052"
)
shortcuts_btn.pack(pady=10)
```

## Testing

### Test 1: Settings Persistence
```bash
1. Launch application
2. Change window size
3. Change settings
4. Close application
5. Relaunch - settings should be restored
6. Check: ~/.config/linux-armoury/settings.json exists
```

### Test 2: Toast Notifications
```bash
1. Change any setting (TDP, GPU mode, etc.)
2. Should see colored toast notification
3. Toast should auto-dismiss after 5 seconds
4. Multiple toasts should stack vertically
```

### Test 3: Real-Time Graphs
```bash
1. Go to Dashboard
2. Should see live CPU/GPU graphs
3. Graphs should update every 2 seconds
4. Should show last 60 seconds of data
5. Min/Avg/Max stats should display
```

### Test 4: Keyboard Shortcuts
```bash
1. Press Ctrl+1 through Ctrl+6 - navigate sections
2. Press Alt+1 through Alt+4 - switch profiles
3. Press F5 - refresh stats
4. Press Ctrl+Q - quit application
```

### Test 5: Profile Manager
```bash
1. Go to Dashboard
2. Click profile buttons (Silent, Balanced, Gaming, etc.)
3. Should see toast confirmation
4. All settings should change (TDP, GPU, fans, RGB, battery)
5. Profile should be saved for next launch
```

### Test 6: Logging
```bash
1. Launch application
2. Perform various actions
3. Check: ~/.config/linux-armoury/linux-armoury.log
4. Should contain timestamped entries
5. Info, warnings, and errors should be logged
```

## Advanced Usage

### Create Custom Profile

```python
from src.linux_armoury.profile_manager import SystemProfile

# Create custom profile
custom = SystemProfile(
    name="My Custom",
    tdp_watts=55,
    gpu_mode="Hybrid",
    fan_curve="Custom",
    rgb_brightness=75,
    rgb_effect="Rainbow",
    battery_limit=85,
    description="My personal configuration"
)

# Save it
app.profile_manager.save_custom_profile(custom)
```

### Export/Import Configuration

```python
# Export current config
from pathlib import Path
app.config.export_config(Path("~/my-linux-armoury-config.json"))

# Import config
app.config.import_config(Path("~/my-linux-armoury-config.json"))
```

### Create Additional Graphs

```python
# Add temperature graph
temp_config = {
    "name": "temp",
    "title": "CPU Temperature",
    "color": "#ffaa00",
    "unit": "°C",
    "min_val": 30,
    "max_val": 100,
    "max_points": 60
}

# Add to graphs_panel configuration
```

## Troubleshooting

### Issue: Toasts not appearing
**Solution**: Check that toast_manager is initialized in `init_enhancements()`

### Issue: Graphs not updating
**Solution**: Verify graphs_panel exists and update_loop() calls graphs_panel.update()

### Issue: Settings not persisting
**Solution**: Check ~/.config/linux-armoury/ permissions and settings.json exists

### Issue: Keyboard shortcuts not working
**Solution**: Ensure `_setup_keyboard_shortcuts()` is called and methods exist (show_dashboard, etc.)

### Issue: Profiles not applying
**Solution**: Check that hardware controllers exist (gpu_controller, fan_controller, etc.)

## File Summary

```
src/linux_armoury/
├── config_manager.py          # Settings persistence
├── profile_manager.py          # Profile management
├── enhancements.py             # Integration layer
└── widgets/
    ├── __init__.py
    ├── toast.py                # Toast notifications
    └── monitoring_graph.py     # Real-time graphs

docs/ (project root)
├── ENHANCEMENT_RECOMMENDATIONS.md   # Detailed feature docs
├── IMPLEMENTATION_ROADMAP.md        # Phase-by-phase guide
├── IMPROVEMENT_SUMMARY.md           # Executive summary
└── ENHANCEMENTS_INTEGRATION_GUIDE.md  # This file
```

## Next Steps

1. **Immediate**: Test config_manager and profile_manager standalone
2. **Phase 1**: Integrate EnhancedAppMixin into gui.py
3. **Phase 2**: Add toast notifications to all actions
4. **Phase 3**: Replace progress bars with real-time graphs
5. **Phase 4**: Add remaining features (tray, fan editor, etc.)

## Support

All enhancement modules include comprehensive logging. Check:
- `~/.config/linux-armoury/linux-armoury.log` for detailed logs
- Console output for real-time status
- `self.logger.error()` calls for error messages

## Conclusion

These enhancements transform Linux Armoury from a functional tool to a professional-grade application. Follow the integration steps systematically, testing each phase before moving to the next.

**Estimated Integration Time**: 2-4 hours for Phase 1 features (config, logging, toast, shortcuts)
