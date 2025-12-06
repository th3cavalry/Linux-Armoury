# ASUS Performance Modes and Beast Mode Guide

## Overview

This document explains ASUS laptop performance modes, Beast Mode functionality, and how Linux Armoury implements similar features on Linux.

## ASUS Armoury Crate Performance Modes

ASUS laptops traditionally come with Armoury Crate software on Windows that provides several performance modes:

### Standard Performance Modes

1. **Silent Mode**
   - Minimal fan noise
   - Conservative power limits
   - Ideal for basic tasks and quiet environments
   - Longer battery life

2. **Performance Mode**
   - Balanced power and acoustics
   - Moderate fan curves
   - Good for everyday tasks
   - Balanced battery life

3. **Turbo Mode (Beast Mode)**
   - Maximum CPU/GPU performance
   - Aggressive fan curves
   - Highest power limits
   - Reduced battery life
   - Best for gaming and intensive workloads

## Beast Mode 3.1

"Beast Mode" is ASUS's marketing term for their maximum performance mode, also called "Turbo Mode". The "3.1" designation is not an official ASUS version number but rather refers to:

### Beast Mode Characteristics

1. **Maximum TDP Allocation**
   - Pushes CPU and GPU to maximum thermal design power
   - For GZ302EA: up to 90W total system power
   - Removes conservative power limits

2. **Aggressive Cooling**
   - Fans run at maximum speeds
   - Prioritizes cooling over acoustics
   - Maintains sustained performance

3. **GPU Boost**
   - Maximum GPU clock speeds
   - Enhanced memory bandwidth
   - Optimized for gaming workloads

4. **CPU Optimization**
   - All-core boost enabled
   - Higher sustained frequencies
   - Better multi-threaded performance

## Linux Armoury Implementation

Linux Armoury provides equivalent functionality through its power profile system:

### Power Profile Mapping

| Linux Armoury | Windows Equivalent | TDP | Refresh Rate | Use Case |
|---------------|-------------------|-----|--------------|----------|
| Emergency | N/A | 10W | 30Hz | Critical battery |
| Battery | Silent+ | 18W | 30Hz | Extended battery |
| Efficient | Silent | 30W | 60Hz | Quiet operation |
| Balanced | Performance | 40W | 90Hz | Daily use |
| Performance | Performance+ | 55W | 120Hz | Heavy work |
| Gaming | Turbo | 70W | 180Hz | Gaming |
| **Maximum** | **Beast Mode** | **90W** | **180Hz** | **Maximum performance** |

### Maximum Profile (Beast Mode Equivalent)

The **Maximum** profile in Linux Armoury is designed to match or exceed ASUS Beast Mode:

```
Power Configuration:
- SPL (Stapm Power Limit): 90W
- sPPT (Slow Package Power Tracking): 90W
- fPPT (Fast Package Power Tracking): 90W
- Refresh Rate: 180Hz
- Fan Control: Maximum (via asusctl if available)
```

## Technical Implementation

### Power Limits (AMD Ryzen AI MAX+ 395)

The GZ302EA uses AMD's power management system:

1. **SPL (Stapm Power Limit)**
   - Long-term sustained power
   - Prevents thermal throttling

2. **sPPT (Slow Package Power Tracking)**
   - Medium-term power budget
   - Manages average power draw

3. **fPPT (Fast Package Power Tracking)**
   - Short-term burst power
   - Allows brief performance spikes

### Display Refresh Rate

The integrated 2560x1600 display supports:
- 30Hz (power saving)
- 60Hz (standard)
- 90Hz (smooth)
- 120Hz (high refresh)
- 180Hz (maximum gaming)

Higher refresh rates consume more power but provide smoother visuals.

## Using Beast Mode in Linux Armoury

### Via GUI

1. Launch Linux Armoury
2. Scroll to "Power Profiles"
3. Click "Apply" on the "Maximum" profile
4. Enter password when prompted
5. System will apply maximum performance settings

### Via Command Line

If you have the GZ302-Linux-Setup scripts installed:

```bash
# Apply maximum performance (Beast Mode)
sudo pwrcfg maximum

# Check current status
sudo pwrcfg status

# Return to balanced
sudo pwrcfg balanced
```

## Performance Comparison

### Expected Performance Gains (Maximum vs Balanced)

- **CPU Multi-core**: +25-35% sustained performance
- **GPU Performance**: +20-30% in games
- **Memory Bandwidth**: +15-20%
- **Thermal Output**: +40-50% heat generation
- **Fan Noise**: 2-3x louder
- **Battery Life**: -60-70% on battery

### When to Use Beast Mode

✅ **Recommended for:**
- Gaming sessions (plugged in)
- Video rendering
- 3D modeling
- Compilation tasks
- AI/ML inference
- When maximum performance is critical

❌ **Not recommended for:**
- Battery operation (drains very quickly)
- Quiet environments (fans are loud)
- Basic tasks (web browsing, documents)
- Extended sessions without AC power

## Advanced Features

### Automatic Profile Switching

Linux Armoury can automatically switch profiles based on:
- AC power state (plugged in vs battery)
- Application launch (game detection)
- Temperature thresholds
- Time of day

### Custom Fan Curves

With asusctl integration, you can:
- Define custom fan curves per profile
- Set temperature triggers
- Balance noise vs cooling

### Power Monitoring

Real-time monitoring of:
- Current TDP limits
- Actual power consumption
- CPU/GPU temperatures
- Fan speeds
- Battery drain rate

## Safety Considerations

### Thermal Protection

The system includes automatic protection:
- Hardware thermal throttling at 95°C
- Automatic shutdown at 105°C
- Fan failure detection
- Power limit override protection

### Battery Health

Using maximum performance mode frequently can:
- Increase battery wear
- Reduce overall battery lifespan
- Generate excess heat
- Shorten battery cycle life

**Recommendation**: Use maximum performance only when needed and when plugged into AC power.

## Troubleshooting

### Beast Mode Not Working

1. **Check kernel version**
   ```bash
   uname -r  # Should be 6.14+
   ```

2. **Verify power management tools**
   ```bash
   which pwrcfg
   ```

3. **Check for conflicts**
   ```bash
   # Ensure no other power management tools are active
   systemctl status power-profiles-daemon
   ```

### Performance Not as Expected

1. **Thermal throttling**
   - Check temperatures with `sensors`
   - Ensure proper ventilation
   - Consider laptop cooling pad

2. **Power delivery**
   - Use official 100W+ charger
   - Check cable quality
   - Verify AC adapter connection

3. **Background processes**
   - Close unnecessary applications
   - Check CPU usage with `htop`
   - Disable unnecessary services

## References

- [GZ302-Linux-Setup Repository](https://github.com/th3cavalry/GZ302-Linux-Setup)
- [ASUS Armoury Crate Performance Modes](https://rog.asus.com/articles/guides/armoury-crate-performance-modes-explained/)
- [AMD Ryzen Power Management](https://www.kernel.org/doc/html/latest/admin-guide/pm/amd-pstate.html)
- [Linux Power Management](https://www.kernel.org/doc/html/latest/power/index.html)

---

**Last Updated**: October 2025
