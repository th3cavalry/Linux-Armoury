# Testing Guide

This guide helps you test Linux Armoury on your system.

## Testing Methods

### 1. Demo Mode (No Root Required)

Test the UI without system integration:

```bash
./demo.py
```

**Demo mode allows you to:**
- Test the GUI appearance and layout
- Try theme switching
- Click power profiles (simulated)
- Change refresh rates (simulated)
- Test preferences dialog
- Verify autostart configuration

**Limitations:**
- Actual system commands are not executed
- No root/sudo required
- Changes are simulated only

### 2. Integration Testing (Requires Root)

Test with actual system integration:

```bash
# First, install the application
./install.sh

# Then launch it
linux-armoury
```

**This tests:**
- Real power profile changes (via pwrcfg)
- Actual refresh rate changes (via xrandr)
- PolicyKit privilege elevation
- System tray integration
- Autostart functionality

## Pre-Installation Checks

### Check Dependencies

```bash
# Check Python version (should be 3.8+)
python3 --version

# Check for GTK4
pkg-config --modversion gtk4

# Check for libadwaita
pkg-config --modversion libadwaita-1

# Check for PyGObject
python3 -c "import gi; print('PyGObject OK')"
```

### Check GZ302 Tools (Optional but Recommended)

```bash
# Check if pwrcfg is installed
which pwrcfg

# Check if it works
pwrcfg status
```

If not found, install from: https://github.com/th3cavalry/GZ302-Linux-Setup

## Test Plan

### Phase 1: GUI Loading

- [ ] Application starts without errors
- [ ] Window appears with correct title
- [ ] All sections are visible:
  - [ ] System Status
  - [ ] Power Profiles (7 profiles)
  - [ ] Refresh Rate Profiles (5 rates)
- [ ] Menu button works
- [ ] About dialog opens and shows correct information

### Phase 2: Theme Testing

- [ ] Switch to Light mode
  - [ ] UI updates to light theme
  - [ ] Theme persists after restart
- [ ] Switch to Dark mode
  - [ ] UI updates to dark theme
  - [ ] Theme persists after restart
- [ ] Switch to Auto mode
  - [ ] UI follows system theme
  - [ ] Theme persists after restart

### Phase 3: Power Profile Testing

For each power profile:
- [ ] Emergency (10W @ 30Hz)
- [ ] Battery (18W @ 30Hz)
- [ ] Efficient (30W @ 60Hz)
- [ ] Balanced (40W @ 90Hz)
- [ ] Performance (55W @ 120Hz)
- [ ] Gaming (70W @ 180Hz)
- [ ] Maximum/Beast Mode (90W @ 180Hz)

Test:
1. Click "Apply" button
2. Enter password when prompted (PolicyKit)
3. Verify success dialog appears
4. Check status display updates
5. Verify command executed (check terminal output or system logs)

### Phase 4: Refresh Rate Testing

For each refresh rate:
- [ ] 30 Hz
- [ ] 60 Hz
- [ ] 90 Hz
- [ ] 120 Hz
- [ ] 180 Hz

Test:
1. Click "Apply" button
2. Enter password when prompted
3. Verify success dialog appears
4. Check status display updates
5. Verify actual refresh rate changed (use `xrandr` to check)

### Phase 5: Preferences Testing

**Autostart:**
- [ ] Enable "Start on Boot"
- [ ] Check desktop file created: `~/.config/autostart/linux-armoury.desktop`
- [ ] Verify file contents are correct
- [ ] Disable "Start on Boot"
- [ ] Check desktop file removed

**Minimize to Tray:**
- [ ] Enable "Minimize to System Tray"
- [ ] Close window - app should stay in tray
- [ ] Click tray icon to restore window
- [ ] Disable "Minimize to System Tray"
- [ ] Close window - app should quit

### Phase 6: System Tray Testing

If libayatana-appindicator is installed:
- [ ] Tray icon appears in system tray
- [ ] Right-click shows menu
- [ ] "Show Window" restores window
- [ ] "Quick Profiles" submenu works
- [ ] Selecting a quick profile applies it
- [ ] "Quit" closes the application

### Phase 7: Configuration Persistence

- [ ] Set a power profile
- [ ] Set a theme
- [ ] Close application
- [ ] Reopen application
- [ ] Verify settings were saved:
  - [ ] Last power profile is shown in status
  - [ ] Theme is still applied
- [ ] Check config file: `~/.config/linux-armoury/settings.json`

### Phase 8: Error Handling

**Missing pwrcfg:**
- [ ] Temporarily rename pwrcfg (if installed)
- [ ] Try to apply a power profile
- [ ] Should show error: "pwrcfg not found"
- [ ] Should not crash
- [ ] Restore pwrcfg

**Invalid refresh rate:**
- [ ] Try to apply a refresh rate not supported by display
- [ ] Should show error message
- [ ] Should not crash

**No password entered:**
- [ ] Click "Apply" on a profile
- [ ] Cancel the password prompt
- [ ] Should handle gracefully
- [ ] Should not crash

## Platform-Specific Testing

### Arch Linux
```bash
# Install dependencies
sudo pacman -S python python-gobject gtk4 libadwaita

# Test installation
./install.sh

# Launch and test
linux-armoury
```

### Ubuntu/Debian
```bash
# Install dependencies
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Test installation
./install.sh

# Launch and test
linux-armoury
```

### Fedora
```bash
# Install dependencies
sudo dnf install python3 python3-gobject gtk4 libadwaita

# Test installation
./install.sh

# Launch and test
linux-armoury
```

### OpenSUSE
```bash
# Install dependencies
sudo zypper install python3 python3-gobject gtk4 libadwaita-1-0

# Test installation
./install.sh

# Launch and test
linux-armoury
```

## Performance Testing

### Resource Usage

Check resource consumption:
```bash
# Memory usage
ps aux | grep linux-armoury

# CPU usage
top -p $(pgrep -f linux-armoury)
```

Expected:
- Memory: 40-80 MB
- CPU: < 1% when idle
- CPU: 2-5% when animating

### Response Time

- UI should be responsive
- Profile changes should apply within 2-3 seconds
- No lag when switching themes
- Smooth animations

## Automated Testing

### Syntax Check

```bash
# Check all Python files
python3 -m py_compile linux-armoury-gui.py
python3 -m py_compile demo.py
python3 -m py_compile tray_icon.py
```

### Shell Script Check

```bash
# Check installation script
bash -n install.sh
shellcheck install.sh  # if shellcheck is installed
```

## Reporting Issues

When reporting bugs, include:

1. **System Information:**
   ```bash
   uname -a
   cat /etc/os-release
   python3 --version
   pkg-config --modversion gtk4
   pkg-config --modversion libadwaita-1
   ```

2. **Error Messages:**
   - Terminal output
   - Error dialogs (screenshots)
   - System logs if relevant

3. **Steps to Reproduce:**
   - Exact sequence of actions
   - Expected vs actual behavior

4. **Configuration:**
   ```bash
   cat ~/.config/linux-armoury/settings.json
   ```

## Success Criteria

The application passes testing if:
- ✅ All UI elements render correctly
- ✅ All themes work properly
- ✅ Power profiles apply successfully (with pwrcfg installed)
- ✅ Refresh rates change correctly
- ✅ Preferences save and persist
- ✅ Autostart configuration works
- ✅ No crashes or unhandled exceptions
- ✅ Error messages are clear and helpful
- ✅ Resource usage is reasonable

## Known Limitations

Current known limitations:
- System tray requires libayatana-appindicator
- Display output hardcoded as eDP-1 (may vary)
- Requires pwrcfg/rrcfg from GZ302-Linux-Setup for full functionality
- No temperature monitoring yet
- No custom profile creation yet

## Next Steps After Testing

1. Report any bugs found
2. Suggest improvements
3. Contribute patches
4. Share screenshots
5. Write documentation improvements

---

**Happy Testing! 🧪**
