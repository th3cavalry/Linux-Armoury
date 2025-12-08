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
- **Clean & Intuitive UI** - Built with Flet and CustomTkinter for a modern dark gray aesthetic
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

- Modern ASUS ROG and ASUS gaming laptop models (2019–present)
- Broader ASUS laptop support including TUF, VivoBook Pro, and other gaming-focused lines

**Example models supported (non-exhaustive):**

- ROG Flow Z13 series (GZ302, GZ302VU, etc.)
- ROG Zephyrus series (M15 / G15 / G16 and similar)
- ROG Strix Scar series (16 / 18 and variants)
- ASUS TUF Gaming series (A15 / A16 / F15 / F17 and variants)
- ROG Ally / ROG Ally X (handheld gaming device) — Hardware control varies by SoC
- Other ASUS gaming-focused models with similar hardware architecture

**Note:** Not all features are available on all models. Hardware control capabilities depend on available ASUS-specific drivers (`asusctl`, `supergfxctl`) and standard Linux power management tools (`power-profiles-daemon`). The application gracefully falls back to available backends.

**System Requirements:**

- Linux kernel 6.14+ (6.17+ recommended for full stability)
- Modern GNOME Stack (GTK4, libadwaita)
- systemd-based init system

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

### Flatpak (Recommended for Immutable Systems)

For Bazzite, Fedora Silverblue, uBlue, and other immutable/containerized systems:

```bash
# Build and install from source
flatpak install flathub org.gnome.Platform//46 org.gnome.Sdk//46
flatpak-builder --user --install --force-clean build-dir com.github.th3cavalry.linux-armoury.yml

# Run the application
flatpak run com.github.th3cavalry.linux-armoury
```

Or install the pre-built `.flatpak` file:

```bash
flatpak install linux-armoury-0.5.0b0.flatpak
flatpak run com.github.th3cavalry.linux-armoury
```

**Note:** Flatpak support is essential for systems like Bazzite that have removed native `asusctl` packages. The Flatpak includes all necessary runtime permissions for hardware monitoring and power management.

### Quick Install (Traditional Linux)

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
1. Install required dependencies
1. Configure hardware-specific repositories (asusctl, power-profiles-daemon)
1. Install the Linux Armoury application
1. Create desktop entry for easy launching

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

### Flatpak-Specific Notes

**When to use Flatpak:**

- ✅ Running Bazzite, Fedora Silverblue, uBlue, or other immutable systems
- ✅ You want automatic updates and easy removal
- ✅ System-wide `asusctl` is not available or you want isolation

**Flatpak permissions:**
The Flatpak manifest includes system D-Bus access to:

- Read power supply information (`/sys/class/power_supply`)
- Monitor CPU information (`/sys/devices/system/cpu`)
- Access hardware monitoring (`/sys/class/hwmon`)
- Communicate with PolicyKit for privilege elevation

These permissions are necessary for hardware control and monitoring functionality. You can inspect the full manifest in `com.github.th3cavalry.linux-armoury.yml`.

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
1. Navigate to the "Power Profiles" section
1. Click "Apply" on your desired profile
1. Enter your password when prompted (via PolicyKit)
1. The new profile will be applied immediately

### Adjusting Refresh Rate

1. Go to the "Refresh Rate Profiles" section
1. Select your preferred refresh rate
1. Click "Apply" to change the display settings

### Configuring Preferences

1. Click the menu button (⋮) in the top-right corner
1. Select "Preferences"
1. Toggle options:
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
1. Select "Theme" submenu
1. Choose:
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

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Overview and quick facts
- **[FAQ](docs/FAQ.md)** - Frequently asked questions

### Feature Documentation

- **[Beast Mode Guide](docs/BEAST_MODE.md)** - Understanding ASUS performance modes
- **[UI Overview](docs/UI_OVERVIEW.md)** - Interface layout and design

### Development

- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture and design
- **[Testing Guide](docs/TESTING.md)** - How to test the application
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute to the project

### Reference

- **[Changelog](docs/CHANGELOG.md)** - Version history and updates
- **[Screenshots](docs/SCREENSHOTS.md)** - Visual overview of features
- **[License](LICENSE)** - GPL-3.0 license

## 🎯 Supported Distributions

All distributions receive equal support:

- **Arch-based**: Arch Linux, EndeavourOS, Manjaro
- **Debian-based**: Ubuntu, Pop!\_OS, Linux Mint, Debian
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

If using **Flatpak on Bazzite or immutable systems**, the backend detection is automatic within the container. The Flatpak includes system D-Bus access to find available power management backends.

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

### Flatpak on Bazzite/Silverblue not finding asusctl

The Flatpak includes runtime permissions for `asusctl` via system D-Bus. If it still doesn't work:

```bash
# Check if Flatpak has system D-Bus access
flatpak info com.github.th3cavalry.linux-armoury | grep system-bus

# Grant/revoke permissions with Flatseal or manually
flatpak override --user --socket=system-bus com.github.th3cavalry.linux-armoury
```

### Application doesn't start

Ensure all dependencies are installed:

```bash
# Ubuntu/Debian
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Arch
sudo pacman -S python python-gobject gtk4 libadwaita

# Fedora
sudo dnf install python3 python3-gobject gtk4 libadwaita

# Flatpak (self-contained, no external deps needed)
flatpak run com.github.th3cavalry.linux-armoury
```

# Ubuntu/Debian

sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Arch

sudo pacman -S python python-gobject gtk4 libadwaita

# Fedora

sudo dnf install python3 python3-gobject gtk4 libadwaita

# Flatpak (self-contained, no external deps needed)

flatpak run com.github.th3cavalry.linux-armoury

```

## 💬 Supported Devices & Community Feedback

Linux Armoury is designed to work with a wide range of ASUS gaming laptops and devices. The project actively incorporates feedback from the community.

### Known Compatibility

**Tested and Verified:**
- ASUS ROG Strix Scar (16/18 inch models)
- ASUS ROG Zephyrus series (M15/G15/G16)
- ASUS ROG Flow Z13
- ROG Ally X (hardware control via system backends)

**In Development/Community Testing:**
- ASUS TUF Gaming series
- ASUS VivoBook Pro gaming models
- ROG Ally (original) — varying support by SoC

### Community Contributions

We welcome feedback and testing reports from users with different devices. If you have a device not listed above, please:

1. **Test Linux Armoury** and report compatibility in [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
2. **Share your hardware specs** (CPU, GPU, model number) to help us improve support
3. **Use Flatpak** on Bazzite or immutable systems for the best experience

**Example Issue Template:**
```

Device: ASUS ROG [Model Name]
CPU: [e.g., AMD Ryzen 7 7840HS]
GPU: [e.g., NVIDIA RTX 4070]
OS: [e.g., Bazzite, Fedora 39, Ubuntu 24.04]
Status: [Works / Partial / Doesn't Work]
Notes: [Your feedback here]

```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug reports
- Feature requests
- Documentation improvements
- Code optimizations
- Testing on new device models
- Hardware compatibility reports

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
```
