# Linux Armoury

**A modern, lightweight GUI control center for ASUS ROG and other ASUS gaming laptops (2019–present)**

Linux Armoury is inspired by G-Helper and ROG Control Center, providing an intuitive interface to manage ASUS gaming laptop performance settings including TDP control, refresh rate management, and system optimization.

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## ✨ Features

### 🎨 Modern Interface
- **Light & Dark Mode** - Automatic or manual theme switching with system integration
- **System Tray Integration** - Minimize to tray and quick access from taskbar with quick profiles
- **Autostart Support** - Launch automatically on system boot
- **Clean & Intuitive UI** - Built with GTK4 and libadwaita for native GNOME look
- **Real-time Dashboard** - Live monitoring with 2-second refresh intervals

### ⚡ Performance Control
- **7 Power Profiles** - From emergency battery saver to maximum performance
  - Emergency: 10W @ 30Hz
  - Battery: 18W @ 30Hz
  - Efficient: 30W @ 60Hz
  - Balanced: 40W @ 90Hz (default)
  - Performance: 55W @ 120Hz
  - Gaming: 70W @ 180Hz
  - Maximum: 90W @ 180Hz

- **Flexible Refresh Rate Control** - 30Hz to 180Hz display management
- **Auto Profile Switching** - Automatically switch profiles when AC/Battery state changes
- **One-Click Profile Switching** - Apply settings with a single click
- **Quick Actions** - Change profiles and refresh rates from system tray

### 📊 System Monitoring
- **Real-time Temperature Monitoring** - CPU and GPU temperature tracking
- **Battery Status** - Live battery percentage and charging state
- **Power Source Detection** - AC or Battery mode with auto-switching support
- **TDP Monitoring** - Current power limit display
- **Refresh Rate Display** - Current display refresh rate

### 🔧 Integration
-- Works with optional hardware support scripts (for some models)
- Integrates with `asusctl`, `power-profiles-daemon`, or `pwrcfg` for power management
- Uses `xrandr` for display control (auto-detects primary display and current resolution)
- PolicyKit integration for secure privilege elevation
- Temperature monitoring via lm-sensors or hwmon

## 📋 Requirements

### Hardware
**Primary Focus:**
- Modern ASUS ROG and ASUS gaming laptop models released within the last ~6 years (2019 — present)

**Example models supported (non-exhaustive):**
- ROG Flow Z13 series
- ROG Zephyrus series (M15 / G15 and similar)
- ASUS TUF / other gaming series (coverage varies by model)

**System Requirements:**
- Linux kernel 6.14+ (6.17+ recommended)

### Software Dependencies
- Python 3.8+
- GTK 4
- libadwaita 1.0+
- PyGObject (python3-gi)
- PolicyKit
- xrandr

### Optional but Recommended
- Model-specific helper scripts may be required for full hardware integration on some laptops
- asusctl for additional ASUS-specific features
- libayatana-appindicator for system tray integration
- lm-sensors for temperature monitoring

## 🚀 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/th3cavalry/Linux-Armoury.git
cd Linux-Armoury

# Make the installation script executable
chmod +x install.sh

# Run the installer
./install.sh
```

The installer will automatically:
1. Detect your Linux distribution
2. Install required dependencies
3. Install the Linux Armoury application
4. Create desktop entry for easy launching

### Manual Installation

If you prefer to install manually:

```bash
# Install dependencies (Ubuntu/Debian example)
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 policykit-1 x11-xserver-utils

# Copy the application
sudo install -m 755 linux-armoury-gui.py /usr/local/bin/linux-armoury
sudo install -m 755 linux-armoury-cli.py /usr/local/bin/linux-armoury-cli
sudo install -m 644 config.py /usr/local/bin/config.py
sudo install -m 644 system_utils.py /usr/local/bin/system_utils.py

# Create desktop entry
sudo cp linux-armoury.desktop /usr/share/applications/
```

## 📖 Usage

### Launching the Application

- **From Application Menu**: Search for "Linux Armoury" in your application launcher
- **From Terminal**: Run `linux-armoury`
- **CLI Tool**: Use `linux-armoury-cli` for scripted/headless control

Examples:

```
linux-armoury-cli --status
linux-armoury-cli --profile gaming
linux-armoury-cli --refresh 180
linux-armoury-cli --monitor
```

### Setting Power Profiles

1. Open Linux Armoury
2. Navigate to the "Power Profiles" section
3. Click "Apply" on your desired profile
4. Enter your password when prompted (via PolicyKit)
5. The new profile will be applied immediately

### Adjusting Refresh Rate

1. Go to the "Refresh Rate Profiles" section
2. Select your preferred refresh rate
3. Click "Apply" to change the display settings

### Configuring Preferences

1. Click the menu button (⋮) in the top-right corner
2. Select "Preferences"
3. Toggle options:
   - **Start on Boot**: Launch automatically when system starts
   - **Minimize to System Tray**: Keep running in background when closed
   - **Auto Profile Switching**: Automatically change profiles when switching between AC and Battery power

### Using Auto Profile Switching

When enabled, the application will automatically:
- Switch to "Performance" profile when AC adapter is connected
- Switch to "Efficient" profile when running on battery
- Notify you of automatic profile changes
- Continue monitoring power source every 2 seconds

This feature helps optimize battery life and performance without manual intervention.

### System Tray Quick Actions

Right-click the system tray icon to:
- Show/Hide the main window
- Quickly apply any power profile (all 7 profiles available)
- Quickly change refresh rate (30, 60, 90, 120, 180 Hz)
- Quit the application

### Changing Theme

1. Click the menu button (⋮)
2. Select "Theme" submenu
3. Choose:
   - **Light Mode**: Force light theme
   - **Dark Mode**: Force dark theme
   - **Auto**: Follow system theme preference

## 🏗️ Architecture

### Technology Stack
- **Language**: Python 3
- **UI Framework**: GTK 4 with libadwaita
- **Configuration**: JSON-based settings storage
- **Privilege Elevation**: PolicyKit (pkexec)

### File Structure
```
Linux-Armoury/
├── linux-armoury-gui.py    # Main application
├── install.sh              # Installation script
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

### Configuration Location
Settings are stored in: `~/.config/linux-armoury/settings.json`

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Project Summary](PROJECT_SUMMARY.md)** - Overview and quick facts
- **[FAQ](FAQ.md)** - Frequently asked questions

### Feature Documentation
- **[Beast Mode Guide](BEAST_MODE.md)** - Understanding ASUS performance modes
- **[UI Overview](UI_OVERVIEW.md)** - Interface layout and design

### Development
- **[Architecture](ARCHITECTURE.md)** - Technical architecture and design
- **[Testing Guide](TESTING.md)** - How to test the application
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

### Reference
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Screenshots](SCREENSHOTS.md)** - Visual overview of features
- **[License](LICENSE)** - GPL-3.0 license

## 🎯 Supported Distributions

All distributions receive equal support:

- **Arch-based**: Arch Linux, EndeavourOS, Manjaro
- **Debian-based**: Ubuntu, Pop!_OS, Linux Mint, Debian
- **RPM-based**: Fedora, Nobara
- **OpenSUSE**: Tumbleweed, Leap

## 🔐 Security

- Uses PolicyKit for secure privilege elevation
- No hardcoded credentials or passwords
- Settings stored in user's home directory
- Minimal system modifications

## 🐛 Troubleshooting

### Power backend not found
Ensure you have `asusctl` (recommended), `power-profiles-daemon`, or `pwrcfg` installed. Linux Armoury requires one of these to manage power profiles.

### Display refresh rate changes don't work
We now auto-detect your primary display and current resolution. If issues persist:
```bash
xrandr --query
```
Ensure the requested mode/rate is supported by your panel.

### Notifications don't show
Make sure the D-Bus activatable desktop file is installed so your desktop allows app notifications:
`/usr/share/applications/com.github.th3cavalry.linux-armoury.desktop` should include:
DBusActivatable=true and X-GNOME-UsesNotifications=true

### Application doesn't start
Ensure all dependencies are installed:
```bash
# Ubuntu/Debian
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug reports
- Feature requests
- Documentation improvements
- Code optimizations
- Additional laptop model support

## 📜 License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## 🙏 Credits

- **Author**: th3cavalry
- **Inspired by**:
  - [G-Helper](https://github.com/seerge/g-helper) by seerge
  - [asusctl/rog-control-center](https://gitlab.com/asus-linux/asusctl) by asus-linux team
- **Hardware research / example scripts**: community-provided model-specific helper scripts (search your laptop family)

## 🔗 Related Projects

- Example model-specific hardware helper scripts (community-maintained)
- [asusctl](https://gitlab.com/asus-linux/asusctl) - ASUS laptop control daemon
- [G-Helper](https://github.com/seerge/g-helper) - Windows ASUS control tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
- **Discussions**: [GitHub Discussions](https://github.com/th3cavalry/Linux-Armoury/discussions)

---

**Note**: This is a community project and is not officially affiliated with or endorsed by ASUS.
