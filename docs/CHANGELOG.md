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

## [1.3.0b1] - 2025-12-06

### Added
- Package refactor: source moved to src/linux_armoury and proper Python package layout
- CI workflow for linting, formatting and tests (GitHub Actions)
- Pre-commit configuration with black, isort and flake8
- Makefile developer helpers for formatting, linting and tests
- System utilities improvements (dynamic /sys path detection for battery/AC/hwmon)
- Tests updated and hardened to be more robust across different platform permutations

### Changed
- Formatting applied (black/isort) and flake8 relaxations for a smooth migration
- Documentation moved into docs/ and updated

## [Unreleased]

### Added
- **Real-Time System Monitoring Dashboard**
  - CPU and GPU temperature monitoring with live updates
  - Battery status with percentage and charging state
  - AC/Battery power source detection
  - Automatic status refresh every 2 seconds
  - Visual indicators in GUI status section

- **Expanded Hardware Support**
  - Support for multiple ASUS laptop models:
    - ROG Flow Z13 2023 (GZ302EZ)
    - ROG Flow Z13 2021 (GZ301)
    - ROG Zephyrus M15 (GU502)
    - ROG Zephyrus G15 (GA502)
  - Model-specific configurations (TDP limits, resolutions, refresh rates)
  - Laptop model detection via DMI
  - Hardware detection CLI command (`--detect`)

- **Auto Profile Switching**
  - Automatic profile changes when AC/Battery state changes
  - Configurable via preferences dialog
  - Default: Performance on AC, Efficient on Battery
  - Desktop notifications for automatic switches

- **Enhanced System Tray**
  - Quick access to all 7 power profiles (not just 4)
  - Quick refresh rate menu (30, 60, 90, 120, 180 Hz)
  - Graceful fallback when libayatana-appindicator unavailable
  - Better notification integration

- **Plugin System Foundation**
  - PluginBase class for creating extensions
  - PluginManager for loading and managing plugins
  - Plugin callbacks: on_load, on_status_update, on_profile_change
  - Automatic plugin directory creation
  - Example temperature alert plugin
  - Comprehensive plugin documentation (PLUGIN_SYSTEM.md)

- **Enhanced CLI**
  - Improved monitoring with visual indicators (emojis)
  - Gaming app detection in monitor mode
  - Periodic timestamps in monitoring output
  - Hardware detection command
  - Better status display formatting

- **Documentation**
  - Updated README with hardware support list
  - Auto-profile switching usage guide
  - System tray quick actions documentation
  - Plugin development guide
  - Extended feature documentation

### Changed
- Status section now shows 5 rows (added temperature and power source)
- CLI monitoring output more informative and visually appealing
- System tray icon setup more robust with error handling

### Technical Details
- Added `plugin_system.py` for extensibility
- Enhanced `system_utils.py` with laptop detection
- Model configurations in `config.py`
- Custom profile storage infrastructure

### Planned Features
- Custom power profile editor
- Integration with asusctl for additional ASUS features
- Keyboard backlight control
- Battery charge limit control
- Power consumption history graphs
- Wayland native support improvements

---

For more details about each version, see the [releases page](https://github.com/th3cavalry/Linux-Armoury/releases).
