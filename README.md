# Linux Armoury

A sleek, lightweight GUI application for controlling ASUS ROG laptops on Linux. Designed specifically for ROG devices like the Flow Z13 (GZ302), this application provides system tray integration, TDP management, refresh rate control, and package update management.

![Linux Armoury](https://img.shields.io/badge/Linux-Armoury-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Qt](https://img.shields.io/badge/Qt-PySide6-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

### 🎯 Core Features
- **System Tray Integration** - Runs minimized in system tray with quick access controls
- **Auto-Start on Boot** - Configurable automatic startup with system
- **Compact UI Design** - Small, sleek interface that doesn't take much screen space
- **Real-time Monitoring** - Live system status including CPU, memory, battery, and temperature

### 🔧 ROG Laptop Controls
- **TDP Management** - Control power profiles (gaming, performance, balanced, efficient, power_saver)
- **Refresh Rate Control** - Manage display refresh rates with profile switching
- **GPU Mode Switching** - Switch between Integrated, Hybrid, and Dedicated GPU modes
- **ASUS Profile Control** - Integration with asusctl for performance profiles
- **VRR Support** - Variable Refresh Rate control for compatible displays

### 📦 Update Management
- **Package Updates** - Check and install updates for ROG-specific packages
- **Driver Updates** - Monitor and update laptop-specific drivers
- **Automatic Checking** - Configurable automatic update checking
- **Categorized Updates** - Updates organized by type (ASUS Control, Kernel & Drivers, etc.)

### ⚙️ Smart Features
- **Auto Power Switching** - Automatically switch profiles when plugging/unplugging AC adapter
- **Tray Quick Controls** - Change TDP and refresh rate profiles directly from system tray
- **Notification Support** - Optional notifications for profile changes and updates
- **Configuration Persistence** - Saves and restores your preferences

## Screenshots

*Screenshots will be added once the application is tested*

## Installation

### Prerequisites

- Linux distribution (Arch, Ubuntu, Fedora, or OpenSUSE based)
- Python 3.8 or higher
- Qt6 libraries (automatically installed)
- ASUS ROG laptop (tested on Flow Z13 GZ302)

### Quick Install

1. **Clone the repository:**
   ```bash
   git clone https://github.com/th3cavalry/Linux-Armoury.git
   cd Linux-Armoury
   ```

2. **Run the installation script:**
   ```bash
   python3 install.py
   ```

3. **Start the application:**
   ```bash
   linux-armoury
   ```

### Manual Installation

If you prefer manual installation:

```bash
# Install dependencies
pip install PySide6 psutil

# Install the application
pip install -e .

# Create desktop entry
python3 -c "from linux_armoury.core.utils import create_desktop_entry; create_desktop_entry()"
```

### ROG-Specific Tools

For full functionality, install these ROG-specific tools:

**Arch Linux / AUR:**
```bash
yay -S asusctl supergfxctl rog-control-center
```

**Ubuntu / Debian:**
```bash
# Add the ROG PPA or build from source
# See: https://gitlab.com/asus-linux/asusctl
```

**GZ302 Setup Script (Recommended):**
```bash
curl -L https://raw.githubusercontent.com/th3cavalry/GZ302-Linux-Setup/main/gz302_setup.py -o gz302_setup.py
chmod +x gz302_setup.py
sudo ./gz302_setup.py
```

## Usage

### Starting the Application

- **GUI:** Find "Linux Armoury" in your application menu
- **Terminal:** Run `linux-armoury`
- **Auto-start:** Enable in Settings tab to start on boot

### System Tray Controls

Right-click the system tray icon for quick access to:
- TDP profiles (gaming, performance, balanced, efficient, power_saver)
- Refresh rate profiles
- Show/Hide main window
- Settings and About

### Main Interface

The main window has several sections:

1. **Status Panel** - Real-time system information
2. **ROG Controls** - TDP, GPU, refresh rate, and ASUS profile controls
3. **Updates Tab** - Check and install ROG-specific package updates
4. **Settings Tab** - Configure auto-start, notifications, and other preferences

### Configuration

Settings are automatically saved to `~/.config/linux-armoury/config.json`

Key settings:
- `auto_start`: Start automatically on boot
- `start_minimized`: Start minimized to tray
- `auto_switch_power`: Auto-switch profiles based on AC/battery
- `show_notifications`: Enable/disable notifications
- `check_updates`: Automatic update checking

## Supported Packages

The update manager monitors these ROG-specific packages:

### ASUS Control
- asusctl - ASUS laptop control utility
- rog-control-center - ROG Control Center GUI
- supergfxctl - GPU switching control

### Kernel & Drivers
- linux-g14 - Optimized kernel for ROG laptops
- linux-g14-headers - Kernel headers
- linux-firmware - Latest firmware
- mesa, vulkan-radeon - Graphics drivers
- rocm-opencl-runtime - AMD GPU compute

### Power Management
- power-profiles-daemon - Power profile management
- ryzenadj - AMD CPU TDP control
- switcheroo-control - GPU switching

### Gaming & Graphics
- gamemode - Gaming optimizations
- mangohud - Performance overlay
- steam, lutris - Gaming platforms

## Compatibility

### Tested Devices
- ✅ ASUS ROG Flow Z13 (GZ302) - Primary target
- ✅ Other ASUS ROG laptops with similar hardware

### Supported Distributions
- ✅ Arch Linux / EndeavourOS / Manjaro
- ✅ Ubuntu / Pop!_OS / Linux Mint
- ✅ Fedora / Nobara
- ✅ OpenSUSE Tumbleweed / Leap

### Required Tools
- `asusctl` - For ASUS-specific controls (optional but recommended)
- `supergfxctl` - For GPU switching (optional)
- `gz302-tdp` - For TDP management (from GZ302-Linux-Setup)
- `gz302-refresh` - For refresh rate control (from GZ302-Linux-Setup)

## Development

### Project Structure
```
linux_armoury/
├── __init__.py
├── main.py              # Application entry point
├── core/                # Core functionality
│   ├── config.py        # Configuration management
│   ├── utils.py         # Utility functions
│   ├── rog_integration.py # ROG hardware integration
│   └── update_manager.py # Package update management
├── ui/                  # User interface
│   ├── main_window.py   # Main application window
│   ├── tray_icon.py     # System tray integration
│   └── update_tab.py    # Update management UI
└── assets/              # Icons and resources
    └── icon.svg         # Application icon
```

### Building from Source

```bash
git clone https://github.com/th3cavalry/Linux-Armoury.git
cd Linux-Armoury
python3 -m pip install -e .
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on your ROG device
5. Submit a pull request

## Related Projects

- **[GZ302-Linux-Setup](https://github.com/th3cavalry/GZ302-Linux-Setup)** - Comprehensive setup script for GZ302
- **[asusctl](https://gitlab.com/asus-linux/asusctl)** - ASUS laptop control utility
- **[supergfxctl](https://gitlab.com/asus-linux/supergfxctl)** - GPU switching control
- **[rog-control-center](https://gitlab.com/asus-linux/rog-control-center)** - Official ROG control GUI

## Troubleshooting

### Common Issues

**Application won't start:**
- Check Python version: `python3 --version` (requires 3.8+)
- Install dependencies: `pip install PySide6 psutil`
- Check for Qt6: `python3 -c "import PySide6; print('Qt6 OK')"`

**No ROG controls available:**
- Install asusctl: See [asus-linux.org](https://asus-linux.org)
- Install GZ302 setup script for TDP/refresh rate controls
- Check logs: `~/.config/linux-armoury/logs/linux-armoury.log`

**System tray not working:**
- Ensure your desktop environment supports system tray
- Try restarting the application
- Check tray icon visibility settings in your DE

**Updates not working:**
- Ensure you have sudo privileges
- Check your package manager is supported
- Verify internet connection

### Logs

Application logs are stored in:
- `~/.config/linux-armoury/logs/linux-armoury.log`

Enable debug logging by setting log level to DEBUG in settings.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **ASUS Linux Community** - For asusctl and related tools
- **GZ302 Users** - For testing and feedback
- **Qt/PySide6** - For the excellent GUI framework
- **Python Community** - For the robust ecosystem

## Support

- **Issues:** [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
- **Discussions:** [GitHub Discussions](https://github.com/th3cavalry/Linux-Armoury/discussions)
- **ASUS Linux:** [asus-linux.org](https://asus-linux.org)

---

**Made with ❤️ for the ASUS ROG Linux community**
