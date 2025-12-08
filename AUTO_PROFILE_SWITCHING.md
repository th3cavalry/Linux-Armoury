# Auto Profile Switching Feature

## Feature Overview
Automatically switches power profiles based on AC adapter connection status for optimal performance and battery life.

## Implementation Status: ✅ COMPLETE

### Feature Behavior
- **Default State**: Disabled (user must enable via Settings)
- **When Enabled**:
  - 🔌 **AC Connected** → Gaming Profile (70W TDP)
  - 🔋 **On Battery** → Battery Saver Profile (18W TDP)

### Profile Details

#### Gaming Profile (AC Power)
- **asusd Policy**: Performance mode
- **TDP Settings** (if RyzenAdj available):
  - STAPM Limit: 70W
  - Fast Limit: 75W
  - Slow Limit: 70W
- **Use Case**: Maximum performance when plugged in

#### Battery Saver Profile (Battery Power)
- **asusd Policy**: Quiet mode
- **TDP Settings** (if RyzenAdj available):
  - STAPM Limit: 18W
  - Fast Limit: 20W
  - Slow Limit: 18W
- **Use Case**: Maximum battery runtime when unplugged

## User Interface

### Settings Location
Navigate to: **⚙️ Settings** → **Power Management** section

### Toggle Switch
```
🔌 Power Management
Auto Profile Switching

✓ Auto switching enabled - Gaming (AC) / Battery Saver (Battery)
```

### Status Indicators
- **Enabled**: Green checkmark with descriptive text
- **Disabled**: Gray text "Auto profile switching disabled"

## Technical Implementation

### Battery Status Detection
Uses `battery_control` module to detect AC adapter state:
```python
battery_status = battery_ctrl.get_battery_status()
on_ac = battery_status in ["Charging", "Full", "Not charging"]
```

### Profile Switching Logic
Implemented in `update_loop()` background thread:
1. Check if auto switching is enabled
2. Get current battery status
3. Compare with last known status
4. If changed:
   - Switch asusd throttle policy
   - Set TDP limits (if RyzenAdj available)
   - Log the change

### Monitoring Frequency
- Checks AC status every 2 seconds (monitoring loop interval)
- Only switches profiles when AC state actually changes
- No unnecessary profile changes

### State Tracking
```python
self.auto_profile_switching = False  # User-controlled flag
self.last_ac_status = None  # Tracks last known AC state
```

## Requirements

### Essential
- ✅ Battery controller support (standard on all laptops)
- ✅ asusd daemon running
- ✅ Valid battery status path

### Optional (Enhanced Functionality)
- RyzenAdj for TDP control (AMD CPUs only)
- Without RyzenAdj: Only asusd policy switching (still effective)

## Console Output

### When Enabled and Switching
```
Auto profile switching enabled
AC adapter connected - Switching to Gaming profile
TDP set to Gaming profile (70W)
```

```
On battery power - Switching to Battery Saver profile
TDP set to Battery Saver profile (18W)
```

### Error Handling
All errors are caught and logged:
```
Auto profile switching error: [error message]
```

## User Benefits

### Battery Life
- Automatically reduces power consumption when unplugged
- 18W profile significantly extends battery runtime
- No manual intervention required

### Performance
- Automatically maximizes performance when plugged in
- 70W gaming profile for demanding workloads
- Seamless transition when plugging/unplugging

### Convenience
- Set it and forget it
- Works in background
- No interruptions or notifications

## Testing

### Test Procedure
1. Enable "Auto Profile Switching" in Settings
2. Verify status shows enabled
3. Unplug AC adapter
4. Check console: Should show "On battery power - Switching to Battery Saver profile"
5. Plug in AC adapter
6. Check console: Should show "AC adapter connected - Switching to Gaming profile"

### Verification Commands
```bash
# Check current asusd profile
asusctl profile -p

# Monitor battery status
cat /sys/class/power_supply/BAT*/status

# View application logs
# Console output shows switching events
```

## Code Locations

### Settings UI
File: `src/linux_armoury/gui.py`
Function: `show_settings()`
Lines: ~1334-1420

### Auto Switching Logic
File: `src/linux_armoury/gui.py`
Function: `update_loop()`
Lines: ~1500-1540

### Initialization
File: `src/linux_armoury/gui.py`
Function: `__init__()`
Lines: ~388-390 (flag initialization)

## Known Limitations

1. **D-Bus Access**: Requires proper D-Bus access to asusd
2. **RyzenAdj**: TDP control requires RyzenAdj (AMD only)
3. **Permissions**: TDP changes may require pkexec/sudo
4. **Polling**: Uses polling (2s) instead of event-based (negligible impact)

## Future Enhancements

### Possible Improvements
- [ ] Custom profile selection per state (not just Gaming/Battery Saver)
- [ ] Event-based AC detection (udev integration)
- [ ] User notification on profile change
- [ ] Profile change history log
- [ ] Battery threshold integration (switch at X% remaining)

## Conclusion

Auto Profile Switching provides seamless power management by automatically optimizing system performance based on power source. The feature is production-ready, well-tested, and provides immediate value to users who frequently switch between AC and battery power.

**Implementation Date**: 2025-12-07
**Status**: Production Ready ✅
