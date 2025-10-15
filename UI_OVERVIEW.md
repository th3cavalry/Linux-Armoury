# Linux Armoury - UI Overview

## Application Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Linux Armoury                              [Theme ▼] [≡]   │  ← Header Bar
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ System Status                                       │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Power Profile          Balanced                     │   │
│  │ Refresh Rate           90 Hz                        │   │
│  │ TDP Settings           Available via power profiles │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Power Profiles                                      │   │
│  │ Control system TDP and performance                  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Emergency                                   [Apply] │   │
│  │ 10W @ 30Hz - Critical battery preservation          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Battery Saver                               [Apply] │   │
│  │ 18W @ 30Hz - Maximum battery life                   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Efficient                                   [Apply] │   │
│  │ 30W @ 60Hz - Balanced efficiency                    │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Balanced                                    [Apply] │   │
│  │ 40W @ 90Hz - Default balanced mode                  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Performance                                 [Apply] │   │
│  │ 55W @ 120Hz - High performance                      │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Gaming                                      [Apply] │   │
│  │ 70W @ 180Hz - Gaming optimized                      │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Maximum                                     [Apply] │   │
│  │ 90W @ 180Hz - Absolute maximum (Beast Mode)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Refresh Rate Profiles                               │   │
│  │ Control display refresh rate                        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 30 Hz                                       [Apply] │   │
│  │ Power saving mode                                   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 60 Hz                                       [Apply] │   │
│  │ Standard                                            │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 90 Hz                                       [Apply] │   │
│  │ Smooth                                              │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 120 Hz                                      [Apply] │   │
│  │ High refresh                                        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 180 Hz                                      [Apply] │   │
│  │ Maximum gaming                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Menu Options

```
[≡] Menu
├── Theme
│   ├── Light Mode
│   ├── Dark Mode
│   └── Auto
├── Preferences
├── About
└── Quit
```

## Preferences Dialog

```
┌───────────────────────────────────────────┐
│  Preferences                          [×] │
├───────────────────────────────────────────┤
│                                           │
│  General                                  │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │ Startup                             │ │
│  ├─────────────────────────────────────┤ │
│  │ Start on Boot                  [○]  │ │
│  │ Launch Linux Armoury when sys...    │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │ Behavior                            │ │
│  ├─────────────────────────────────────┤ │
│  │ Minimize to System Tray        [●]  │ │
│  │ Keep running in background wh...    │ │
│  └─────────────────────────────────────┘ │
│                                           │
└───────────────────────────────────────────┘
```

## System Tray Menu

```
┌────────────────────────┐
│ Linux Armoury          │
├────────────────────────┤
│ Show Window            │
├────────────────────────┤
│ Quick Profiles      ▶  │
├────────────────────────┤
│ Quit                   │
└────────────────────────┘
       │
       └─► ┌──────────────┐
           │ Battery      │
           │ Balanced     │
           │ Performance  │
           │ Gaming       │
           └──────────────┘
```

## Color Schemes

### Light Mode
- Background: Light gray/white
- Text: Dark gray/black
- Accent: Blue (Adwaita blue)
- Buttons: Light gray with blue hover

### Dark Mode
- Background: Dark gray/charcoal
- Text: Light gray/white
- Accent: Blue (Adwaita blue)
- Buttons: Dark gray with blue hover

## UI Components

### Header Bar
- Application title on left
- Theme selector (optional)
- Menu button (hamburger) on right

### Status Section
- Read-only display of current settings
- Updates automatically after profile changes
- Shows: Power Profile, Refresh Rate, TDP info

### Power Profiles Section
- List of 7 pre-configured profiles
- Each row shows:
  - Profile name (bold)
  - Description with TDP and refresh rate
  - Apply button (right-aligned)

### Refresh Rate Section
- List of 5 refresh rate options
- Each row shows:
  - Refresh rate (bold)
  - Description/use case
  - Apply button (right-aligned)

### Dialogs
- Success dialog: Green checkmark, message, OK button
- Error dialog: Red warning, message, OK button
- Preferences: Modal dialog with switches

## Interaction Flow

### Applying a Power Profile

```
User clicks "Apply" on a profile
         ↓
PolicyKit prompts for password
         ↓
User enters password
         ↓
Command executes (pwrcfg <profile>)
         ↓
Success dialog appears
         ↓
Status section updates
         ↓
Settings saved to config file
```

### Theme Switching

```
User selects theme from menu
         ↓
StyleManager applies theme
         ↓
UI updates instantly
         ↓
Setting saved to config
         ↓
Theme persists on restart
```

## Responsive Design

The UI adapts to different window sizes:
- Minimum width: 600px
- Minimum height: 400px
- Default size: 800x600
- Scrollable content area
- Fixed header bar

## Accessibility

- Full keyboard navigation
- Screen reader support (via GTK4)
- High contrast mode support
- Clear focus indicators
- Descriptive button labels

## Visual Hierarchy

1. **Header** - Application identity
2. **Status** - Current state (most important info)
3. **Power Profiles** - Primary controls
4. **Refresh Rates** - Secondary controls
5. **Menu/Preferences** - Settings and options

## Design Principles

- **Simplicity** - One-click actions
- **Clarity** - Clear labels and descriptions
- **Consistency** - Follows GNOME HIG
- **Feedback** - Immediate visual confirmation
- **Safety** - Confirmation for critical actions

---

This layout provides a clean, modern interface for laptop performance management while maintaining the familiar GNOME/Adwaita aesthetic.
