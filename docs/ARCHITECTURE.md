# Architecture Documentation

## System Architecture

Linux Armoury follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  (GTK4 + libadwaita - Modern GNOME Interface)               │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer                          │
│  (Python 3 - Business Logic & State Management)             │
├─────────────────────────────────────────────────────────────┤
│                  Integration Layer                           │
│  (PolicyKit, DBus, System Commands)                         │
├─────────────────────────────────────────────────────────────┤
│                   System Layer                               │
│  (asusctl, ppd, pwrcfg, xrandr, Hardware Control)           │
└─────────────────────────────────────────────────────────────┘
```

## Component Diagram

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Main Window     │────▶│  Preferences     │     │  System Tray     │
│  (MainWindow)    │     │  (PrefsDialog)   │     │  (SystemTray)    │
└────────┬─────────┘     └──────────────────┘     └────────┬─────────┘
         │                                                   │
         │                                                   │
         ▼                                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              Application Controller (LinuxArmouryApp)            │
│  - Manages application lifecycle                                 │
│  - Handles settings persistence                                  │
│  - Coordinates UI and backend                                    │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ├─────────────┐
         │             │
         ▼             ▼
┌─────────────┐  ┌─────────────────┐
│  Settings   │  │  Command        │
│  Manager    │  │  Executor       │
│             │  │  (PolicyKit)    │
└─────────────┘  └────────┬────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  System Commands │
                 │  - pwrcfg        │
                 │  - xrandr        │
                 └──────────────────┘
```

## File Structure

```
Linux-Armoury/
├── linux-armoury-gui.py    # Main application entry point
│   ├── LinuxArmouryApp     # Application controller
│   ├── MainWindow          # Main UI window
│   └── PreferencesDialog   # Preferences window
│
├── tray_icon.py            # System tray integration
│   └── SystemTrayIcon      # Tray icon manager
│
├── demo.py                 # Demo/test mode
│
├── install.sh              # Installation script
│
├── linux-armoury.desktop   # Desktop entry file
│
└── Documentation/
    ├── README.md
    ├── QUICKSTART.md
    ├── BEAST_MODE.md
    ├── CONTRIBUTING.md
    ├── FAQ.md
    ├── TESTING.md
    ├── UI_OVERVIEW.md
    └── ARCHITECTURE.md (this file)
```

## Data Flow

### Power Profile Application

```
User Action (Click "Apply")
    ↓
MainWindow.on_power_profile_clicked(profile)
    ↓
PolicyKit Authentication
    ↓
subprocess.run(["pkexec", "pwrcfg", profile])
    ↓
System Command Execution
    ↓
Settings Update (self.settings[profile] = value)
    ↓
Save to Config (app.save_settings())
    ↓
UI Update (self.refresh_status())
    ↓
Success Dialog Display
```

### Theme Switching

```
User Selects Theme
    ↓
MainWindow.change_theme(theme)
    ↓
Adw.StyleManager.set_color_scheme(scheme)
    ↓
UI Updates (GTK handles rendering)
    ↓
Settings Update (self.settings["theme"] = theme)
    ↓
Save to Config
```

### Settings Persistence

```
Application Start
    ↓
LinuxArmouryApp.__init__()
    ↓
load_settings()
    ↓
Read ~/.config/linux-armoury/settings.json
    ↓
Apply to UI (theme, last profile, etc.)

---

Settings Change
    ↓
Update self.settings dictionary
    ↓
app.save_settings()
    ↓
Write to ~/.config/linux-armoury/settings.json
```

## Class Hierarchy

```
LinuxArmouryApp (Adw.Application)
    │
    ├── manages ──▶ MainWindow (Adw.ApplicationWindow)
    │                   │
    │                   ├── contains ──▶ HeaderBar
    │                   ├── contains ──▶ Status Section
    │                   ├── contains ──▶ Power Profiles Section
    │                   └── contains ──▶ Refresh Rate Section
    │
    ├── shows ────▶ PreferencesDialog (Adw.PreferencesWindow)
    │
    └── uses ─────▶ SystemTrayIcon (optional)
```

## State Management

### Application State

```python
{
    "theme": "auto" | "light" | "dark",
    "autostart": true | false,
    "minimize_to_tray": true | false,
    "current_power_profile": "balanced",
    "current_refresh_rate": "90"
}
```

Stored in: `~/.config/linux-armoury/settings.json`

### UI State

- Window size and position (handled by window manager)
- Current selected profile (visual only, not persisted)
- Dialog open/closed states (transient)

## Security Model

### Privilege Separation

```
User Space (No Privileges)
    │
    ├── GUI Application (linux-armoury)
    │   └── User can browse, select options
    │
    ↓ [PolicyKit Authentication]
    │
System Space (Root Privileges)
    │
    └── System Commands (asusctl, ppd, pwrcfg, xrandr)
        └── Executed with elevated privileges
```

### PolicyKit Flow

1. User clicks "Apply"
1. Application invokes `pkexec`
1. PolicyKit shows authentication dialog
1. User enters password
1. PolicyKit validates credentials
1. If valid, executes command as root
1. Result returned to application

### Security Features

- **No stored credentials** - Password handled by PolicyKit
- **Minimal privilege** - Only specific commands elevated
- **User confirmation** - Password required for each action
- **Sandboxed execution** - Commands run in isolated context
- **Audit trail** - PolicyKit logs all privileged operations

## Integration Points

### Hardware Abstraction Layer

```
Linux Armoury
    ↓
SystemUtils (Hardware Abstraction)
    ↓
    ├── Detects available backend (asusctl, ppd, pwrcfg)
    ├── Maps generic profiles to backend-specific profiles
    └── Executes appropriate command
```

### Display Management

```
Linux Armoury
    ↓
calls xrandr
    ↓
    └── Sets display mode and refresh rate
        └── xrandr --output eDP-1 --mode 2560x1600 --rate <hz>
```

### System Tray (Optional)

```
Linux Armoury
    ↓
uses libayatana-appindicator (if available)
    ↓
    └── Creates system tray icon
        └── Provides quick access menu
```

## Configuration Management

### Config Directory Structure

```
~/.config/linux-armoury/
├── settings.json         # Application settings
└── (future expansions)
```

### Config File Format

```json
{
  "theme": "auto",
  "autostart": false,
  "minimize_to_tray": true,
  "current_power_profile": "balanced",
  "current_refresh_rate": "balanced"
}
```

### Autostart Configuration

Desktop file location: `~/.config/autostart/linux-armoury.desktop`

Created when "Start on Boot" is enabled in preferences.

## Error Handling

### Error Categories

1. **Missing Dependencies**

   - GTK4/libadwaita not installed
   - Python missing required modules
   - PolicyKit not available

1. **Command Execution Errors**

   - pwrcfg not found
   - xrandr fails
   - Permission denied
   - Timeout

1. **Configuration Errors**

   - Cannot read/write settings
   - Invalid JSON
   - Corrupt config file

### Error Handling Strategy

```python
try:
    # Execute command
    result = subprocess.run(...)

    if result.returncode == 0:
        # Success path
        show_success_dialog()
    else:
        # Command failed
        show_error_dialog(result.stderr)

except subprocess.TimeoutExpired:
    # Command timed out
    show_error_dialog("Command timed out")

except Exception as e:
    # Unexpected error
    show_error_dialog(f"Error: {str(e)}")
```

## Performance Considerations

### Resource Usage

- **Memory**: 40-80 MB typical
- **CPU**: \<1% idle, 2-5% during animations
- **Disk**: \<1 MB (settings only)
- **Network**: None (fully offline)

### Optimization Strategies

1. **Lazy Loading** - Load UI components on demand
1. **Efficient Updates** - Only refresh changed UI elements
1. **Async Operations** - Use timeouts for commands
1. **Minimal Polling** - No background polling, event-driven

## Extension Points

Future extensions can be added through:

### Custom Profiles

```python
# New module: custom_profiles.py
class CustomProfileManager:
    def create_profile(name, tdp, refresh_rate)
    def edit_profile(profile_id, settings)
    def delete_profile(profile_id)
```

### Temperature Monitoring

```python
# New module: temperature_monitor.py
class TemperatureMonitor:
    def get_cpu_temp()
    def get_gpu_temp()
    def get_fan_speed()
```

### Auto Profile Switching

```python
# New module: auto_switcher.py
class AutoProfileSwitcher:
    def detect_ac_power()
    def detect_running_apps()
    def apply_appropriate_profile()
```

## Testing Architecture

### Unit Testing (Future)

```python
# tests/test_settings.py
def test_load_settings()
def test_save_settings()
def test_default_settings()

# tests/test_ui.py
def test_window_creation()
def test_theme_switching()
def test_profile_selection()
```

### Integration Testing

See [TESTING.md](TESTING.md) for manual testing procedures.

### Demo Mode

`demo.py` provides non-privileged testing:

- Patches system calls
- Simulates command execution
- Allows UI testing without root

## Deployment

### Installation Methods

1. **Automated** - `install.sh` script
1. **Manual** - Copy files to system directories
1. **Package** - Future: .deb, .rpm, AUR packages

### System Integration

- Binary: `/usr/local/bin/linux-armoury`
- Desktop file: `/usr/share/applications/linux-armoury.desktop`
- User config: `~/.config/linux-armoury/`
- Autostart: `~/.config/autostart/` (optional)

## Future Architecture Enhancements

### Planned Improvements

1. **DBus Service**

   - Background daemon for system integration
   - GUI as client to daemon
   - Better privilege separation

1. **Plugin System**

   - External modules for extended features
   - Community-contributed profiles
   - Hardware-specific optimizations

1. **Wayland Native**

   - Layer shell for better tray integration
   - Native Wayland protocols
   - Compositor-specific features

1. **Multi-Device Support**

   - Profile per laptop model
   - Auto-detection of hardware
   - Model-specific optimizations

## Dependencies Graph

```
linux-armoury
    ├── Python 3.8+
    │   └── Standard Library
    │       ├── subprocess
    │       ├── json
    │       └── os
    │
    ├── PyGObject
    │   ├── gi.repository.Gtk 4.0
    │   ├── gi.repository.Adw 1.0
    │   └── gi.repository.Gio
    │
    ├── System Tools
    │   ├── PolicyKit (pkexec)
    │   ├── xrandr
    │   └── pwrcfg (may be provided by model-specific helper scripts)
    │
    └── Optional
        └── libayatana-appindicator (system tray)
```

## Conclusion

Linux Armoury follows a clean, modular architecture that:

- Separates concerns (UI, logic, system)
- Provides secure privilege escalation
- Maintains user privacy and security
- Allows for future extensions
- Follows GNOME/GTK best practices

______________________________________________________________________

For implementation details, see the source code comments in `linux-armoury-gui.py`.
