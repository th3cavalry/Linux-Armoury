# Linux Armoury Feature Mapping & Expansion Plan

## Overview

This document maps features from Windows Armoury Crate to the Linux ecosystem and outlines how Linux Armoury will expand to support all ASUS gaming laptops.

## Feature Comparison Matrix

| Feature | Armoury Crate | asusctl/asusd | Linux Armoury Current | Planned |
|---------|--------------|--------------|----------------------|---------|
| Power Profiles | Silent/Performance/Turbo | platform_profile | Basic TDP | Full support |
| GPU Switching | iGPU/dGPU/Hybrid | supergfxctl | Not supported | Full support |
| Keyboard RGB | Per-key/Zone | aura_led driver | Not supported | Full Aura |
| Fan Curves | Custom curves | asusd curves | Not supported | Custom curves |
| Battery Charge | 60/80/100% | charge_control | Not supported | Full support |
| Display Refresh | Panel overdrive | xrandr/wlr-randr | Supported | Enhanced |
| Anime Matrix | Custom animations | asusd anime | Not supported | Full support |

## Supported ASUS Laptop Families

### ROG (Republic of Gamers)
- ROG Zephyrus (G14, G15, G16, M16, Duo)
- ROG Strix (G15, G17, Scar series)
- ROG Flow (X13, Z13, X16)

### TUF Gaming
- TUF Gaming (A15, A17, F15, F17)
- TUF Dash (F15)

### ProArt
- ProArt Studiobook (16, Pro 16)

## Implementation Phases

### Phase 1: Core Infrastructure (Current)
- [x] Basic TDP control
- [x] Refresh rate management
- [x] Settings persistence
- [x] Plugin system foundation
- [x] GTK4/libadwaita GUI

### Phase 2: ASUS Integration
- [ ] asusd D-Bus client
- [ ] supergfxctl D-Bus client
- [ ] Hardware detection module
- [ ] Fallback to direct sysfs access

### Phase 3: Feature Expansion
- [ ] Full Aura keyboard support
- [ ] Fan curve editor
- [ ] Battery charge limit
- [ ] Anime Matrix support

### Phase 4: Polish
- [ ] Tray icon enhancements
- [ ] Profile import/export
- [ ] Keyboard shortcut customization

## Hardware Detection Paths

Key sysfs paths for ASUS hardware:
- /sys/devices/platform/asus-nb-wmi
- /sys/firmware/acpi/platform_profile
- /sys/class/power_supply/BAT*/charge_control_end_threshold
- /sys/class/leds/asus::kbd_backlight

## D-Bus Interfaces

asusd: org.asuslinux.Daemon, org.asuslinux.Platform, org.asuslinux.Led
supergfxctl: org.supergfxctl.Daemon

## Resources

- https://gitlab.com/asus-linux/asusctl
- https://gitlab.com/asus-linux/supergfxctl
- https://asus-linux.org
- https://wiki.archlinux.org/title/ASUS_Linux
