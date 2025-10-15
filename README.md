# Linux Armoury

**A modern, lightweight GUI control center for ASUS GZ302EA laptops running Linux**

Linux Armoury is inspired by G-Helper and ROG Control Center, providing an intuitive interface to manage your ASUS ROG Flow Z13 (GZ302) laptop's performance settings including TDP control, refresh rate management, and system optimization.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## ✨ Features

### 🎨 Modern Interface
- **Light & Dark Mode** - Automatic or manual theme switching with system integration
- **System Tray Integration** - Minimize to tray and quick access from taskbar
- **Autostart Support** - Launch automatically on system boot
- **Clean & Intuitive UI** - Built with GTK4 and libadwaita for native GNOME look

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
- **Real-time Status Monitoring** - View current TDP and refresh rate settings
- **One-Click Profile Switching** - Apply settings with a single click

### 🔧 Integration
- Works seamlessly with [GZ302-Linux-Setup](https://github.com/th3cavalry/GZ302-Linux-Setup) scripts
- Integrates with `pwrcfg` for power management
- Uses `xrandr` for display control
- PolicyKit integration for secure privilege elevation

## 📋 Requirements

### Hardware
- ASUS ROG Flow Z13 (GZ302EA) - Models: XS99, XS64, XS32
- Linux kernel 6.14+ (6.17+ recommended)

### Software Dependencies
- Python 3.8+
- GTK 4
- libadwaita 1.0+
- PyGObject (python3-gi)
- PolicyKit
- xrandr

### Optional but Recommended
- [GZ302-Linux-Setup](https://github.com/th3cavalry/GZ302-Linux-Setup) scripts for full functionality
- asusctl for additional ASUS-specific features

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

# Create desktop entry
sudo cp linux-armoury.desktop /usr/share/applications/
```

## 📖 Usage

### Launching the Application

- **From Application Menu**: Search for "Linux Armoury" in your application launcher
- **From Terminal**: Run `linux-armoury`

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

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Beast Mode Guide](BEAST_MODE.md)** - Understanding ASUS performance modes
- **[FAQ](FAQ.md)** - Frequently asked questions
- **[Testing Guide](TESTING.md)** - How to test the application
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Screenshots](SCREENSHOTS.md)** - Visual overview of features

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

### "pwrcfg not found" error
Install the GZ302-Linux-Setup scripts:
```bash
curl -L https://raw.githubusercontent.com/th3cavalry/GZ302-Linux-Setup/main/gz302-main.sh -o gz302-main.sh
chmod +x gz302-main.sh
sudo ./gz302-main.sh
```

### Display refresh rate changes don't work
Check your display output name:
```bash
xrandr | grep " connected"
```
Update the output name in the application if it differs from `eDP-1`.

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
- **Hardware research**: [GZ302-Linux-Setup](https://github.com/th3cavalry/GZ302-Linux-Setup)

## 🔗 Related Projects

- [GZ302-Linux-Setup](https://github.com/th3cavalry/GZ302-Linux-Setup) - Core hardware fixes and management scripts
- [asusctl](https://gitlab.com/asus-linux/asusctl) - ASUS laptop control daemon
- [G-Helper](https://github.com/seerge/g-helper) - Windows ASUS control tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
- **Discussions**: [GitHub Discussions](https://github.com/th3cavalry/Linux-Armoury/discussions)

---

**Note**: This is a community project and is not officially affiliated with or endorsed by ASUS.
