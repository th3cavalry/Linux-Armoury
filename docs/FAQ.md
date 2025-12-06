# Frequently Asked Questions (FAQ)

## General Questions

### What is Linux Armoury?

Linux Armoury is a GUI control center for ASUS GZ302EA laptops running Linux. It provides an easy-to-use interface for managing power profiles, TDP settings, and display refresh rates, similar to G-Helper (Windows) and ROG Control Center.

### Which laptop models are supported?

Currently supported:
- ASUS ROG Flow Z13 (GZ302EA-XS99) - 128GB variant
- ASUS ROG Flow Z13 (GZ302EA-XS64) - 64GB variant
- ASUS ROG Flow Z13 (GZ302EA-XS32) - 32GB variant

Future versions may support additional models.

### Do I need the GZ302-Linux-Setup scripts?

While Linux Armoury can run independently, it works best with the [GZ302-Linux-Setup](https://github.com/th3cavalry/GZ302-Linux-Setup) scripts installed. These provide:
- `pwrcfg` command for power management
- `rrcfg` command for refresh rate control
- Hardware fixes and optimizations

Without them, the GUI will show errors when trying to apply profiles.

## Installation Questions

### Which Linux distributions are supported?

All major distributions are equally supported:
- **Arch-based:** Arch Linux, EndeavourOS, Manjaro
- **Debian-based:** Ubuntu, Pop!_OS, Linux Mint, Debian
- **RPM-based:** Fedora, Nobara
- **OpenSUSE:** Tumbleweed, Leap

### Do I need root/sudo to install?

The installation script (`install.sh`) requires sudo to install system-wide files, but you run it as a regular user:
```bash
./install.sh  # Will ask for password when needed
```

### Can I install without the script?

Yes, see the "Manual Installation" section in the README.

### Where are files installed?

- Application: `/usr/local/bin/linux-armoury`
- Desktop file: `/usr/share/applications/linux-armoury.desktop`
- Config: `~/.config/linux-armoury/settings.json` (per user)

## Usage Questions

### What is Beast Mode?

Beast Mode (called "Maximum" in Linux Armoury) is the highest performance mode:
- 90W TDP (maximum power)
- 180Hz refresh rate
- Maximum CPU/GPU performance
- Highest fan speeds
- Shortest battery life

See [BEAST_MODE.md](BEAST_MODE.md) for detailed information.

### How do I apply a power profile?

1. Open Linux Armoury
2. Scroll to "Power Profiles"
3. Click "Apply" on your desired profile
4. Enter your password when prompted
5. Done! Settings apply immediately

### Why do I need to enter a password?

Power and display management require root privileges. We use PolicyKit (pkexec) for secure privilege elevation instead of storing or handling passwords directly.

### Can I auto-switch profiles based on AC power?

Not yet in version 1.0, but this feature is planned for future releases. Currently, you need to manually switch profiles.

### What's the difference between power profiles?

| Profile | Power | Use Case | Battery Impact |
|---------|-------|----------|----------------|
| Emergency | 10W | Critical battery | Best |
| Battery | 18W | Extended use | Very Good |
| Efficient | 30W | Daily tasks | Good |
| Balanced | 40W | General use | Moderate |
| Performance | 55W | Heavy work | Fair |
| Gaming | 70W | Gaming | Poor |
| Maximum | 90W | Beast Mode | Very Poor |

### How do I enable autostart?

1. Open Linux Armoury
2. Click menu (⋮) → Preferences
3. Toggle "Start on Boot"
4. Done! App will launch when you log in

### How does minimize to tray work?

When enabled in Preferences:
- Closing the window keeps the app running in the system tray
- Click the tray icon to restore the window
- Right-click for quick access menu
- Select "Quit" from tray menu to exit

**Note:** Requires libayatana-appindicator to be installed.

## Troubleshooting

### The application won't start

1. **Check dependencies:**
   ```bash
   python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')"
   ```

2. **Run from terminal to see errors:**
   ```bash
   linux-armoury
   ```

3. **Reinstall dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt install --reinstall python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
   ```

### I get "pwrcfg not found" errors

Install the GZ302-Linux-Setup scripts:
```bash
curl -L https://raw.githubusercontent.com/th3cavalry/GZ302-Linux-Setup/main/gz302-main.sh -o gz302-main.sh
chmod +x gz302-main.sh
sudo ./gz302-main.sh
```

### Refresh rate changes don't work

1. **Check your display output name:**
   ```bash
   xrandr | grep " connected"
   ```

2. If it's not `eDP-1`, the code needs updating. Please report this as an issue on GitHub with your output name.

### The system tray icon doesn't appear

1. **Check if libayatana-appindicator is installed:**
   ```bash
   # Ubuntu/Debian
   sudo apt install gir1.2-ayatanaappindicator3-0.1

   # Arch
   sudo pacman -S libayatana-appindicator

   # Fedora
   sudo dnf install libayatana-appindicator-gtk3
   ```

2. **Check if your desktop supports system tray:**
   - GNOME: Requires extension like "AppIndicator Support"
   - KDE: Built-in support
   - XFCE: Built-in support
   - Others: Varies

### Settings don't persist

Check config file permissions:
```bash
ls -la ~/.config/linux-armoury/settings.json
```

Should be writable by your user. If not:
```bash
chmod 644 ~/.config/linux-armoury/settings.json
```

### Changes don't apply or I get errors

1. **Check system logs:**
   ```bash
   journalctl -xe | grep -i power
   ```

2. **Test commands manually:**
   ```bash
   sudo pwrcfg balanced
   sudo rrcfg balanced
   ```

3. **Verify PolicyKit is working:**
   ```bash
   pkexec echo "PolicyKit works"
   ```

### Application uses too much memory/CPU

Normal usage:
- **Memory:** 40-80 MB
- **CPU:** <1% when idle

If higher:
1. Close and restart the application
2. Check for memory leaks (report as bug)
3. Check system resources in general

## Feature Questions

### Can I create custom power profiles?

Not in version 1.0, but this is a planned feature for future releases.

### Does it monitor temperatures?

Not currently. Temperature monitoring is planned for a future release.

### Can it control fan speeds?

Not directly. Fan control would require integration with asusctl, which is planned for future releases.

### Does it support RGB keyboard lighting?

No, RGB control requires asusctl integration, which is not included in the current version.

### Can it limit battery charge?

No, battery charge limiting requires asusctl or similar tools and is not currently implemented.

### Will it work on other ASUS laptops?

The current version is specifically designed for GZ302EA. Support for other models may be added in the future. The UI would work, but power profile values would need adjustment for different hardware.

### Can I use this on non-ASUS laptops?

The GUI would load, but power profiles are optimized for GZ302EA hardware. You could modify the TDP values for your specific laptop, but this is not officially supported.

## Technical Questions

### What technology stack does it use?

- **Language:** Python 3.8+
- **UI Framework:** GTK 4
- **UI Library:** libadwaita
- **Bindings:** PyGObject
- **Privilege Elevation:** PolicyKit (pkexec)

### Why GTK4/libadwaita instead of Qt?

GTK4 with libadwaita provides:
- Native GNOME integration
- Automatic light/dark mode support
- Modern, clean interface
- Smaller dependencies on GNOME-based systems

### Is it safe to use?

Yes:
- Uses PolicyKit for secure privilege elevation
- No hardcoded credentials
- Open source (GPL-3.0)
- Minimal system modifications
- Sandboxed privilege escalation

### How does it compare to G-Helper?

**Similarities:**
- Clean, modern UI
- Power profile management
- TDP control
- Multiple performance modes

**Differences:**
- G-Helper: Windows only (C#, .NET)
- Linux Armoury: Linux only (Python, GTK)
- G-Helper: Direct ASUS ACPI control
- Linux Armoury: Uses system scripts (pwrcfg, xrandr)

### Can I run it on Wayland?

Yes, GTK4 supports both X11 and Wayland. However, some features may work differently:
- PolicyKit works on both
- System tray support varies by compositor
- Display control uses xrandr (X11) or equivalent Wayland tools

### Does it work over SSH/remote desktop?

The GUI requires a display server. For headless systems, use the command-line tools (pwrcfg, rrcfg) directly.

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Performance Questions

### Which profile should I use for gaming?

For gaming:
- **On AC power:** Gaming (70W) or Maximum (90W)
- **On battery:** Don't game on battery (use Balanced max)

### Which profile is best for battery life?

- **Maximum battery:** Battery profile (18W @ 30Hz)
- **Balanced:** Efficient profile (30W @ 60Hz)

### Does higher refresh rate drain more battery?

Yes, significantly:
- 30Hz: Best battery life
- 60Hz: Good battery life
- 90Hz: Moderate battery drain
- 120-180Hz: High battery drain

Higher refresh rates also increase GPU workload.

### Can I use Maximum profile on battery?

Technically yes, but not recommended:
- Drains battery in 1-2 hours
- May throttle due to power delivery limits
- Generates excessive heat
- Reduces battery lifespan

Use only when plugged in.

## Future Plans

### What features are planned?

See [CHANGELOG.md](CHANGELOG.md) for planned features:
- Custom profile editor
- Temperature monitoring
- Fan curve control
- asusctl integration
- Auto profile switching
- Game detection
- Battery health monitoring

### When will feature X be added?

We don't have specific timelines. Features are added based on:
- Community feedback
- Development time available
- Technical feasibility

Feel free to contribute or sponsor development!

### Can I request a feature?

Yes! Open an issue on GitHub with:
- Clear description of the feature
- Use case (why it's needed)
- Expected behavior
- Any examples from other tools

## Support

### Where can I get help?

- **Documentation:** README.md, QUICKSTART.md, this FAQ
- **Issues:** [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
- **Discussions:** [GitHub Discussions](https://github.com/th3cavalry/Linux-Armoury/discussions)

### How do I report a bug?

See the "Reporting Bugs" section in [CONTRIBUTING.md](CONTRIBUTING.md).

### Is there a user community?

Join the GitHub Discussions to connect with other users and developers.

---

**Don't see your question?** Open a discussion on GitHub and we'll add it to this FAQ!
