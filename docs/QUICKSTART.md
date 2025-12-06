# Quick Start Guide

Get up and running with Linux Armoury in minutes!

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/th3cavalry/Linux-Armoury.git
cd Linux-Armoury
```

### Step 2: Run the Installer

```bash
chmod +x install.sh
./install.sh
```

The installer will:
- Detect your Linux distribution automatically
- Install all required dependencies
- Install Linux Armoury to your system
- Create a desktop entry

### Step 3: Launch the Application

Launch from your application menu or run:

```bash
linux-armoury
```

## First Time Setup

### 1. Choose Your Theme

- Click the menu button (⋮) in the top-right
- Select "Theme" → Choose your preference:
  - **Auto**: Follows your system theme
  - **Light**: Always use light mode
  - **Dark**: Always use dark mode

### 2. Enable Autostart (Optional)

- Click menu → "Preferences"
- Toggle "Start on Boot"
- Linux Armoury will launch automatically when you log in

### 3. Configure Tray Behavior

- In Preferences, toggle "Minimize to System Tray"
- When enabled, closing the window keeps the app running in the background
- Access it anytime from the system tray icon

## Using Power Profiles

### Applying a Profile

1. Scroll to "Power Profiles" section
2. Choose a profile based on your needs:
   - **Emergency** (10W): Critical battery situations
   - **Battery** (18W): Maximum battery life
   - **Efficient** (30W): Good performance with efficiency
   - **Balanced** (40W): Daily use (default)
   - **Performance** (55W): Heavy workloads
   - **Gaming** (70W): Gaming sessions
   - **Maximum** (90W): Beast Mode - absolute maximum
3. Click "Apply"
4. Enter your password when prompted
5. Settings apply immediately!

### Understanding Power Profiles

Each profile sets three parameters:
- **TDP (Thermal Design Power)**: How much power the CPU/GPU can use
- **Refresh Rate**: Display refresh rate for smoothness vs battery
- **Fan Curves**: Cooling behavior (via asusctl if available)

Higher profiles = More performance + More heat + More battery drain

## Adjusting Refresh Rate

### Quick Change

1. Go to "Refresh Rate Profiles"
2. Select your desired rate:
   - **30 Hz**: Maximum battery savings
   - **60 Hz**: Standard smooth
   - **90 Hz**: Enhanced smoothness
   - **120 Hz**: High refresh
   - **180 Hz**: Maximum gaming
3. Click "Apply"

**Tip**: Refresh rate is automatically set when applying a power profile, but can be manually overridden.

## Understanding Status Display

The "System Status" section shows:
- **Power Profile**: Currently active profile
- **Refresh Rate**: Current display refresh rate
- **TDP Settings**: Power limits in effect

This updates after each profile change.

## Tips & Tricks

### Battery Life

For maximum battery life:
1. Use "Battery" profile (18W @ 30Hz)
2. Close unnecessary applications
3. Lower screen brightness
4. Disable Bluetooth if not needed

### Gaming Performance

For best gaming experience:
1. Plug in AC adapter (required for high power)
2. Apply "Gaming" or "Maximum" profile
3. Close background applications
4. Ensure good ventilation

### Quick Access from Tray

If system tray is enabled:
1. Right-click the tray icon
2. Select "Quick Profiles"
3. Choose a profile without opening the main window

### Switching on AC/Battery

Recommended profiles:
- **On Battery**: Battery or Efficient (18-30W)
- **On AC Power**: Balanced to Maximum (40-90W)

Manual switching helps optimize for your current situation.

## Troubleshooting

### Power Profile Issues

If power profiles are not working, ensure you have a supported power management tool installed:
- **asusctl**: Recommended for ASUS ROG laptops.
- **power-profiles-daemon**: Standard for GNOME/KDE.
- **pwrcfg**: Legacy/Model-specific scripts (e.g. GZ302).

Linux Armoury will automatically detect and use the available tool.

### App Won't Start

Check dependencies:

```bash
# Ubuntu/Debian
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Arch
sudo pacman -S python python-gobject gtk4 libadwaita

# Fedora
sudo dnf install python3 python3-gobject gtk4 libadwaita
```

### Changes Don't Apply

1. Ensure you entered the password correctly
2. Check that pwrcfg is installed: `which pwrcfg`
3. Try running manually: `sudo pwrcfg balanced`
4. Check for error messages in the terminal

### Refresh Rate Not Changing

1. Check your display name: `xrandr | grep connected`
2. If it's not `eDP-1`, the code needs updating
3. Report this as an issue on GitHub

## Next Steps

- Explore all 7 power profiles to find your favorites
- Experiment with different refresh rates
- Enable autostart for convenience
- Check out the [Beast Mode documentation](BEAST_MODE.md)
- Read the [full README](README.md) for advanced features
- Join the community discussions on GitHub

## Getting Help

- **Documentation**: See README.md and BEAST_MODE.md
- **Issues**: [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
- **Discussions**: [GitHub Discussions](https://github.com/th3cavalry/Linux-Armoury/discussions)

---

**Enjoy your optimized Linux experience! 🚀**
