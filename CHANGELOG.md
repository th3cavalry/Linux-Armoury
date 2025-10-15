# Changelog

All notable changes to Linux Armoury will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-15

### Added
- Initial release of Linux Armoury GUI
- GTK4/libadwaita-based modern interface
- Light and dark theme support with auto-detection
- System tray icon integration (with libayatana-appindicator)
- Minimize to tray functionality
- Autostart on boot support
- 7 power profiles (Emergency to Maximum/Beast Mode):
  - Emergency: 10W @ 30Hz
  - Battery: 18W @ 30Hz
  - Efficient: 30W @ 60Hz
  - Balanced: 40W @ 90Hz
  - Performance: 55W @ 120Hz
  - Gaming: 70W @ 180Hz
  - Maximum: 90W @ 180Hz (Beast Mode equivalent)
- Flexible refresh rate control (30Hz - 180Hz)
- Real-time status monitoring
- Integration with GZ302-Linux-Setup tools (pwrcfg, rrcfg)
- PolicyKit integration for secure privilege elevation
- Preferences dialog with user settings
- JSON-based configuration storage
- Comprehensive documentation:
  - README with installation and usage guide
  - BEAST_MODE.md explaining ASUS performance modes
  - CONTRIBUTING.md with development guidelines
- Multi-distribution support:
  - Arch-based (Arch, Manjaro, EndeavourOS)
  - Debian-based (Ubuntu, Pop!_OS, Mint)
  - RPM-based (Fedora, Nobara)
  - OpenSUSE (Tumbleweed, Leap)
- Automated installation script
- Desktop entry for application launcher

### Technical Details
- Written in Python 3 with PyGObject
- Uses GTK 4 and libadwaita for modern UI
- Follows GNOME HIG (Human Interface Guidelines)
- Settings stored in ~/.config/linux-armoury/settings.json
- Desktop file for autostart in ~/.config/autostart/

### Target Hardware
- ASUS ROG Flow Z13 (GZ302EA)
  - GZ302EA-XS99 (128GB variant)
  - GZ302EA-XS64 (64GB variant)
  - GZ302EA-XS32 (32GB variant)

### Dependencies
- Python 3.8+
- GTK 4
- libadwaita 1.0+
- PyGObject (python3-gi)
- PolicyKit
- xrandr
- Optional: libayatana-appindicator for system tray

### Known Issues
- System tray requires libayatana-appindicator (not all distros have it by default)
- pwrcfg integration requires GZ302-Linux-Setup scripts to be installed
- Display output name hardcoded as eDP-1 (may vary on some systems)

### Future Enhancements
- Auto-detect display output name
- Application-specific profile switching
- Temperature monitoring
- Fan curve control (with asusctl)
- Multi-monitor support
- Custom profile creation
- Power consumption graphs
- Battery health monitoring

## [Unreleased]

### Planned Features
- Custom power profile editor
- Temperature and fan speed monitoring
- Integration with asusctl for additional ASUS features
- Keyboard backlight control
- Battery charge limit control
- Game detection and auto-profile switching
- Power consumption history graphs
- Notification system for profile changes
- Wayland native support improvements
- Additional laptop model support

---

For more details about each version, see the [releases page](https://github.com/th3cavalry/Linux-Armoury/releases).
