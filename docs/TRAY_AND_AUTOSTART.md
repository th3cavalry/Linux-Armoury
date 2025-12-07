# System Tray & Autostart Features

## Overview

Linux Armoury now runs as a persistent background service that:

- Minimizes to system tray instead of taskbar
- Continues running when you close the window
- Auto-starts on boot to apply your custom settings
- Only exits when you explicitly quit from the tray icon

## System Tray Behavior

### Window Close Button

When you click the window close button (X):

- Window hides to system tray
- Application continues running in background
- All your custom settings remain active
- A notification appears: "Running in background. Right-click tray icon to quit."

### Tray Icon Menu

Right-click the tray icon to access:

- **Show/Hide Window** - Toggle the main window
- **Quick Profile Switch** - Change power profiles quickly
- **Quick Refresh Rate** - Change display refresh rate
- **Quit** - Actually exit the application

## Auto-Start on Boot

### Why Auto-Start?

Linux Armoury needs to start automatically on boot to:

- Apply your custom TDP settings
- Set your preferred power profile
- Configure display refresh rate
- Enable custom fan curves
- Apply RGB keyboard settings

### Installation

The install script automatically sets up autostart:

```bash
./install.sh
```

This installs the autostart entry to: `~/.config/autostart/linux-armoury.desktop`

### Manual Configuration

To manually enable/disable autostart:

**Enable:**

```bash
mkdir -p ~/.config/autostart
cp linux-armoury-autostart.desktop ~/.config/autostart/linux-armoury.desktop
```

**Disable:**

```bash
rm ~/.config/autostart/linux-armoury.desktop
```

## Command-Line Options

### Start Minimized

Start the application hidden in the system tray:

```bash
python3 linux-armoury-gui.py --minimized
# or
linux-armoury --minimized
```

### Show Version

```bash
python3 linux-armoury-gui.py --version
```

## Usage Scenarios

### Scenario 1: Daily Use

1. Boot your laptop → Linux Armoury starts automatically (hidden)
1. Your custom settings are applied immediately
1. Access quick controls via tray icon when needed
1. Close the window when done → Stays running in background

### Scenario 2: Gaming Session

1. Right-click tray icon → Select "Performance" profile
1. Optionally open window to monitor temps
1. Your settings persist even after closing the window
1. Switch back to "Balanced" from tray when done

### Scenario 3: Battery Conservation

1. Right-click tray icon → Select "Battery Saver" profile
1. Application automatically adjusts TDP and refresh rate
1. Settings remain active as long as app is running
1. No need to keep window open

## Troubleshooting

### Tray Icon Not Visible

Some desktop environments require extensions for tray icons:

**GNOME:**
Install AppIndicator extension:

```bash
# Check if extension is available
gnome-extensions list | grep -i appindicator

# Enable if installed
gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
```

**KDE Plasma:**
Tray icons work by default

**XFCE:**
Add "Notification Area" widget to panel

### Application Not Auto-Starting

Check if the autostart file exists:

```bash
ls -la ~/.config/autostart/linux-armoury.desktop
```

Verify the file contents:

```bash
cat ~/.config/autostart/linux-armoury.desktop
```

Check startup applications in your desktop settings:

- GNOME: Settings → Applications → Startup Applications
- KDE: System Settings → Startup and Shutdown → Autostart

### How to Fully Exit

The application only exits when you:

1. Right-click the tray icon
1. Select "Quit"
1. OR run: `killall python3` (force kill)

Closing the window does NOT exit the application.

## System Resources

Linux Armoury uses minimal resources when minimized:

- Memory: ~50-100 MB
- CPU: < 1% (polling system status every 2 seconds)
- No impact on gaming performance

## Privacy & Security

- No network connections
- No telemetry or tracking
- All settings stored locally in `~/.config/linux-armoury/`
- Uses standard Linux system interfaces (sysfs, asusctl, etc.)

## Integration with Desktop

The application integrates with your desktop environment:

- Desktop notifications for profile changes
- Native system tray icon
- Follows system theme (light/dark mode)
- Standard keyboard shortcuts (Ctrl+Q to quit)

## Advanced: Startup Delay

By default, Linux Armoury waits 5 seconds after boot before starting.
This ensures system services are ready.

To change the delay, edit the autostart file:

```bash
nano ~/.config/autostart/linux-armoury.desktop
```

Change the line:

```
X-GNOME-Autostart-Delay=5
```

To your preferred delay in seconds (0-30 recommended).
