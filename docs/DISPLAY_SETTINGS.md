# Display Color Management - sRGB Gamut Clamp & Color Profiles

## Overview

Linux Armoury now includes comprehensive display color management features specifically designed to fix color accuracy issues on ASUS Flow Z13 and other ASUS gaming laptops running Linux.

**Problem Solved:** Flow Z13 users experience over-saturated, overly bright, and inaccurate colors due to improper display gamma settings. This feature provides an sRGB gamut clamp to correct these issues.

## Features

### 1. sRGB Gamut Clamp Toggle
- **Purpose:** Clamps the display to the sRGB color gamut, fixing over-saturated and overly bright colors
- **Impact:** Significantly improves color accuracy for web content, games, and professional applications
- **Status:** Can be toggled on/off at any time
- **Command:** `asusctl bios display-srgb on/off`

### 2. Color Profile Selection
Choose between three industry-standard color profiles:

| Profile | Use Case | Best For |
|---------|----------|----------|
| **sRGB** | Standard web and content | Web browsing, streaming, most games |
| **Adobe RGB** | Professional graphics work | Photo editing, design software |
| **DCI-P3** | Cinema and HDR content | High-end gaming, video content |

## Usage

### GUI Usage

1. Navigate to **⚙️ Settings** in the sidebar
2. Scroll to **🎨 Display Color Settings**
3. **For sRGB Gamut Clamp:**
   - Click "Toggle sRGB Gamut Clamp" button
   - Status updates immediately
4. **For Color Profiles:**
   - Select desired profile: sRGB, Adobe RGB, or DCI-P3
   - Selected profile is highlighted in accent color

### CLI Usage

#### Check Current Settings
```bash
linux-armoury-cli --get-color-settings
```

Output:
```
sRGB Gamut Clamp: Enabled
Color Profile: sRGB
Available Profiles: sRGB, Adobe RGB, DCI-P3
```

#### Toggle sRGB Gamut Clamp
```bash
# Enable
linux-armoury-cli --srgb-clamp on

# Disable
linux-armoury-cli --srgb-clamp off

# Toggle (current state flips)
linux-armoury-cli --srgb-clamp toggle
```

#### Set Color Profile
```bash
# Set to sRGB
linux-armoury-cli --color-profile srgb

# Set to Adobe RGB
linux-armoury-cli --color-profile adobe-rgb

# Set to DCI-P3
linux-armoury-cli --color-profile dci-p3
```

## Technical Details

### System Requirements
- **ASUS ROG/Gaming Laptop** with display color management support
- **asusctl** installed and configured
- **Linux** kernel with proper BIOS/firmware support

### Command Implementation

The feature uses `asusctl` BIOS commands:

```bash
# Check current sRGB status
asusctl bios display-srgb -g

# Enable sRGB gamut clamp
asusctl bios display-srgb on

# Disable sRGB gamut clamp
asusctl bios display-srgb off

# Check available color profiles
asusctl bios display-color -l

# Set color profile
asusctl bios display-color [srgb|adobe-rgb|dci-p3]
```

### Backend Architecture

```
GUI/CLI Input
    ↓
system_utils.py (SystemUtils class)
    ├── get_srgb_clamp_status()      → Query current state
    ├── set_srgb_clamp(enabled)      → Toggle on/off
    ├── toggle_srgb_clamp()          → Auto-toggle
    ├── get_color_profile()          → Get current profile
    ├── set_color_profile(profile)   → Change profile
    ├── get_available_color_profiles() → List available
    └── get_display_color_settings() → Get all settings
    ↓
asusctl commands (via subprocess)
    ↓
ASUS BIOS/Firmware
    ↓
Display Hardware
```

## Flow Z13 Specific Notes

### Why Colors Appear Over-Saturated
- Flow Z13 display runs in extended color gamut by default
- This exceeds standard sRGB range, making colors appear "radioactive"
- Content is mastered for sRGB, leading to significant mismatch

### Solution
Enable **sRGB Gamut Clamp** to:
- Map extended gamut back to sRGB
- Improve color accuracy dramatically
- Make web content display as intended
- Enhance gaming experience with proper color representation

### Recommended Settings
- **Default:** sRGB with sRGB Gamut Clamp Enabled
- **Gaming:** sRGB or DCI-P3 with sRGB Gamut Clamp (depending on game)
- **Photo Editing:** Adobe RGB with Gamut Clamp disabled
- **Video Work:** DCI-P3 with Gamut Clamp disabled

## Troubleshooting

### Command Not Supported
```
Error: asusctl bios display-srgb not found
```
**Solution:** Update asusctl to latest version or check BIOS support

```bash
asusctl --version
```

### Changes Not Taking Effect
1. Ensure asusctl service is running:
   ```bash
   systemctl status asusd
   ```

2. Try manual setting:
   ```bash
   sudo asusctl bios display-srgb on
   ```

3. Check BIOS firmware version - some older versions may not support this

### Not Supported on Your Model
Check if your ASUS laptop model supports color management:

```bash
linux-armoury-cli --detect
```

Look for "Display Color Settings: Supported" in output

## Integration with Other Features

### Works With
- **Profile Switching:** Color settings persist across power profiles
- **Refresh Rate Control:** Independent from display refresh rates
- **Auto-Switching:** Can be included in custom automation

### Does Not Affect
- **Brightness Control:** Separate from color management
- **Contrast Settings:** Not modified by color profiles
- **GPU Rendering:** Settings apply at display output level

## Future Enhancements

Planned additions:
- [ ] Gamma adjustment slider
- [ ] Brightness/Contrast controls
- [ ] Custom color temperature (K)
- [ ] HDR mode toggle
- [ ] Per-application color profile switching
- [ ] Color calibration wizard

## Resources

### Related Files
- **Backend:** [`src/linux_armoury/system_utils.py`](../src/linux_armoury/system_utils.py)
  - `get_srgb_clamp_status()`
  - `set_srgb_clamp()`
  - `get_color_profile()`
  - `set_color_profile()`

- **CLI:** [`src/linux_armoury/cli.py`](../src/linux_armoury/cli.py)
  - `set_srgb_clamp()`
  - `set_color_profile()`
  - `show_color_settings()`

- **GUI:** [`src/linux_armoury/gui.py`](../src/linux_armoury/gui.py)
  - Display Color Settings section in `show_battery()`

### External References
- [asusctl Documentation](https://gitlab.com/asus-linux/asusctl)
- [sRGB Gamut Explanation](https://en.wikipedia.org/wiki/Srgb)
- [DCI-P3 Color Space](https://en.wikipedia.org/wiki/DCI-P3)
- [ASUS Linux Community](https://asus-linux.org)

## Support

For issues or feature requests:
1. Check [FAQ](FAQ.md) for common questions
2. Review [CONTRIBUTING.md](CONTRIBUTING.md) for bug reports
3. Open issue on [GitHub](https://github.com/th3cavalry/Linux-Armoury/issues)

Include:
- Laptop model (e.g., "Flow Z13")
- asusctl version: `asusctl --version`
- Output of: `linux-armoury-cli --get-color-settings`
- Output of: `linux-armoury-cli --detect`