# Project Summary

## Linux Armoury v1.0.0

**A modern GUI control center for ASUS ROG and other ASUS gaming laptops (2019–present)**

### Quick Facts

- **Language**: Python 3
- **UI Framework**: GTK4 + libadwaita
- **License**: GPL-3.0
- **Platform**: Linux (Multi-distro)
- **Status**: Feature Complete v1.0
- **Target Hardware**: Modern ASUS ROG and ASUS gaming laptops (2019–present)

### Features at a Glance

✅ Light and dark mode support
✅ System tray integration
✅ 7 power profiles (10W - 90W TDP)
✅ 5 refresh rate modes (30Hz - 180Hz)
✅ Autostart on boot
✅ Minimize to tray
✅ PolicyKit security
✅ Multi-distribution support

### Quick Links

- **Installation**: See [QUICKSTART.md](QUICKSTART.md)
- **Documentation**: See [README.md](README.md)
- **Beast Mode**: See [BEAST_MODE.md](BEAST_MODE.md)
- **FAQ**: See [FAQ.md](FAQ.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Testing**: See [TESTING.md](TESTING.md)

### Installation (One Command)

```bash
git clone https://github.com/th3cavalry/Linux-Armoury.git && cd Linux-Armoury && ./install.sh
```

### File Inventory

#### Core Application
- `linux-armoury-gui.py` - Main application (17.6 KB)
- `tray_icon.py` - System tray module (3.2 KB)
- `demo.py` - Demo/test mode (2.6 KB)

#### Installation & Config
- `install.sh` - Installation script (4.7 KB)
- `linux-armoury.desktop` - Desktop entry (395 B)

#### Documentation (46+ KB total)
- `README.md` - Main documentation (7.2 KB)
- `QUICKSTART.md` - Getting started guide (4.9 KB)
- `BEAST_MODE.md` - Performance mode guide (6.6 KB)
- `FAQ.md` - Frequently asked questions (11 KB)
- `CONTRIBUTING.md` - Development guide (7.9 KB)
- `TESTING.md` - Testing procedures (7.2 KB)
- `ARCHITECTURE.md` - Technical architecture (11 KB)
- `UI_OVERVIEW.md` - UI design document (7.9 KB)
- `CHANGELOG.md` - Version history (3.1 KB)
- `SCREENSHOTS.md` - Screenshots guide (1.6 KB)
- `LICENSE` - GPL-3.0 license (968 B)

#### Configuration
- `.gitignore` - Git ignore rules (367 B)

### Power Profiles Summary

| Profile | TDP | Refresh | Best For |
|---------|-----|---------|----------|
| Emergency | 10W | 30Hz | Critical battery |
| Battery | 18W | 30Hz | Max battery life |
| Efficient | 30W | 60Hz | Daily tasks |
| **Balanced** | 40W | 90Hz | **Default** |
| Performance | 55W | 120Hz | Heavy work |
| Gaming | 70W | 180Hz | Gaming |
| Maximum | 90W | 180Hz | Beast Mode |

### Supported Distributions

- Arch Linux, Manjaro, EndeavourOS
- Ubuntu, Pop!_OS, Linux Mint, Debian
- Fedora, Nobara
- OpenSUSE Tumbleweed, Leap

### Dependencies

**Required:**
- Python 3.8+
- GTK 4
- libadwaita 1.0+
- PyGObject
- PolicyKit
- xrandr

**Optional:**
- libayatana-appindicator (system tray)
Model-specific hardware support scripts (community-maintained, varies by model)

### Project Statistics

- **Total Lines of Code**: ~800 (Python)
- **Documentation Pages**: 11
- **Total Documentation**: ~46,000 words
- **Power Profiles**: 7
- **Refresh Rates**: 5
- **Themes**: 3 (Light, Dark, Auto)

### Development Timeline

- **Project Start**: October 15, 2025
- **Version 1.0.0**: October 15, 2025
- **Development Time**: 1 day (intensive development)

### Key Technologies

1. **GTK 4** - Modern GNOME UI toolkit
2. **libadwaita** - GNOME design patterns
3. **PyGObject** - Python bindings for GTK
4. **PolicyKit** - Secure privilege escalation
5. **JSON** - Configuration storage

### Design Philosophy

- **Simplicity** - One-click actions
- **Security** - PolicyKit authentication
- **Clarity** - Clear labels and feedback
- **Modern** - GTK4/Adwaita design
- **Open** - GPL-3.0 licensed

### Inspiration

- **G-Helper** (Windows) - Lightweight ASUS control
- **ROG Control Center** (Linux) - asusctl suite
- **GNOME HIG** - Human Interface Guidelines

### Future Roadmap

#### Version 1.1 (Planned)
- Temperature monitoring
- Custom power profiles
- Fan curve control
- Application-specific profiles

#### Version 1.2 (Planned)
- asusctl integration
- Keyboard RGB control
- Battery charge limiting
- Multi-monitor support

#### Version 2.0 (Future)
- DBus service architecture
- Plugin system
- Game detection
- Power usage graphs

### Community

- **Repository**: https://github.com/th3cavalry/Linux-Armoury
- **Issues**: Report bugs and request features
- **Discussions**: Community support and ideas
- **Pull Requests**: Contributions welcome!

### Related Projects

- Example model-specific hardware helper scripts (community-maintained)
- [asusctl](https://gitlab.com/asus-linux/asusctl) - ASUS Linux control
- [G-Helper](https://github.com/seerge/g-helper) - Windows ASUS control

### Credits

**Author**: th3cavalry

**Inspired by**: seerge (G-Helper), asus-linux team (asusctl/rog-control-center)

**Built with**: GitHub Copilot assistance

### License

GPL-3.0 License - See [LICENSE](LICENSE) file

### Support

- **Documentation**: Full guides in repository
- **GitHub Issues**: Bug reports and features
- **GitHub Discussions**: Community support

### Thank You

Thank you for using Linux Armoury! This project aims to provide ASUS laptop users on Linux with a powerful, user-friendly control center for managing their hardware.

If you find it useful, please:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Contribute code
- 📢 Share with others

---

**Enjoy your optimized Linux experience! 🚀**

*Last Updated: October 15, 2025*
