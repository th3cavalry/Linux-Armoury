# Linux Armoury - ASUS ROG Laptop Control GUI

**ALWAYS follow these instructions first** and only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in error.

Linux Armoury is a Python GUI application built with PySide6 for controlling ASUS ROG laptops on Linux. It provides system monitoring, hardware control, and gaming optimizations similar to Windows ROG Control Center.

## Essential Setup and Dependencies

**Prerequisites:** Python 3.8+ (tested with 3.12.3), Linux distribution, ASUS ROG laptop recommended

**Critical Graphics Libraries Required for GUI:**
```bash
sudo apt-get update && sudo apt-get install -y libegl1 libgl1-mesa-dri libxcb-xinerama0 libxcb-util1 qt6-base-dev
```
**NEVER SKIP:** Install these graphics libraries before testing GUI functionality or the application will crash with Qt platform plugin errors.

## Building and Installation 

**ALWAYS run these exact commands in sequence:**

1. **Install the application (15 seconds):**
   ```bash
   python3 install.py
   ```
   - Installs Python dependencies (PySide6 >= 6.4.0, psutil >= 5.9.0)
   - Creates desktop entry and CLI command
   - Checks for optional ROG tools (expected to be missing on non-ROG systems)

2. **Alternative manual installation:**
   ```bash
   python3 -m pip install -e .
   ```

3. **Quick run without installation:**
   ```bash
   python3 run.py
   ```

## Testing and Validation

**ALWAYS run all tests after making changes. NEVER CANCEL these commands:**

1. **Core functionality test (1.2 seconds):**
   ```bash
   python3 test_app.py
   ```
   - Tests core modules, system monitoring, ROG tool availability
   - Expected: Core modules PASS, ROG tools FAIL (normal without ROG hardware)
   - Expected: UI modules PASS (after installing graphics libraries)

2. **Enhanced features test (0.1 seconds):**
   ```bash
   python3 test_enhanced_features.py
   ```
   - Tests hardware monitoring, RGB control, gaming mode, audio enhancement
   - Expected: 5/5 enhanced features working

3. **Manual validation scenarios (REQUIRED after changes):**
   ```bash
   # Test CLI command exists
   which linux-armoury
   
   # Test module imports
   python3 -c "from linux_armoury.main import main; print('Main module imported successfully')"
   
   # Test configuration system
   python3 -c "from linux_armoury.core.config import Config; c=Config(); print('Config system working')"
   ```

## Code Quality and Linting

**ALWAYS run these before committing (total time: ~1 second):**

1. **Install linting tools once:**
   ```bash
   python3 -m pip install flake8 black isort
   ```

2. **Check for critical errors (0.4 seconds):**
   ```bash
   python3 -m flake8 linux_armoury/ --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

3. **Full style check (0.4 seconds):**
   ```bash
   python3 -m flake8 linux_armoury/ --count --statistics
   ```

4. **Format code (when needed):**
   ```bash
   python3 -m black linux_armoury/
   ```

5. **Check formatting without changes:**
   ```bash
   python3 -m black --check linux_armoury/
   ```

## Running the Application

**GUI requires graphics libraries (see setup section):**

1. **Start main application:**
   ```bash
   linux-armoury
   ```
   OR
   ```bash
   python3 -m linux_armoury.main
   ```

2. **Quick start script:**
   ```bash
   python3 run.py
   ```

**Note:** GUI will crash without proper graphics libraries installed. In headless environments, focus on testing core functionality and module imports.

## Project Structure and Key Files

```
linux_armoury/
├── main.py                  # Application entry point - GUI startup
├── core/                    # Core functionality (import these for testing)
│   ├── config.py           # Configuration management
│   ├── utils.py            # System utilities and monitoring
│   ├── rog_integration.py  # ROG hardware integration (optional)
│   ├── hardware_monitor.py # Enhanced hardware monitoring
│   ├── audio_manager.py    # Audio enhancement features
│   ├── gaming_mode.py      # Gaming optimizations
│   ├── rgb_control.py      # RGB lighting control
│   └── update_manager.py   # Package update management
├── ui/                     # User interface components
│   ├── main_window.py      # Main application window
│   ├── tray_icon.py        # System tray integration
│   ├── enhanced_controls.py # Enhanced control widgets
│   └── update_tab.py       # Update management UI
└── assets/                 # Icons and resources
```

**Key files for understanding the codebase:**
- `linux_armoury/core/utils.py` - System monitoring and utility functions
- `linux_armoury/core/config.py` - Configuration system
- `linux_armoury/main.py` - Application entry point
- `test_app.py` - Core functionality validation
- `test_enhanced_features.py` - Enhanced features validation

## ROG-Specific Tools (Optional)

**These tools are optional and expected to be missing on non-ROG systems:**
- `asusctl` - ASUS control utility
- `supergfxctl` - GPU switching control  
- `gz302-tdp` - TDP management script
- `gz302-refresh` - Refresh rate management script

**Install on Arch Linux:**
```bash
yay -S asusctl supergfxctl rog-control-center
```

**For GZ302 users:**
```bash
curl -L https://raw.githubusercontent.com/th3cavalry/GZ302-Linux-Setup/main/gz302_setup.py -o gz302_setup.py
chmod +x gz302_setup.py
sudo ./gz302_setup.py
```

## Development Workflow

**Always follow this sequence when making changes:**

1. **Make code changes**
2. **Test imports and core functionality:**
   ```bash
   python3 test_app.py
   ```
3. **Test enhanced features:**
   ```bash
   python3 test_enhanced_features.py
   ```
4. **Check for critical errors:**
   ```bash
   python3 -m flake8 linux_armoury/ --count --select=E9,F63,F7,F82
   ```
5. **Manual validation - test specific functionality you changed**
6. **Format code if needed:**
   ```bash
   python3 -m black linux_armoury/
   ```

## Common Validation Commands Output

**Use these cached results instead of running commands repeatedly:**

### Repository root contents:
```
.git/
.gitignore
ENHANCED_FEATURES.md
ENHANCEMENT_SUMMARY.md  
LICENSE
README.md
demo_enhanced_ui.py
install.py*
linux-armoury.desktop
linux_armoury/
requirements.txt
run.py*
setup.py
test_app.py*
test_enhanced_features.py
```

### Python dependencies (requirements.txt):
```
PySide6>=6.4.0
psutil>=5.9.0
```

### Successful test output:
```bash
# python3 test_app.py
Core modules: ✓ PASS
ROG tools: ✗ FAIL (some missing) # Expected on non-ROG systems
UI modules: ✓ PASS # After installing graphics libraries

# python3 test_enhanced_features.py  
Overall: 5/5 enhanced features working
```

## Troubleshooting

**GUI crashes with Qt platform plugin error:**
- Install graphics libraries: `sudo apt-get install -y libegl1 libgl1-mesa-dri qt6-base-dev`

**PySide6 import fails:**
- Run: `python3 install.py` or `python3 -m pip install PySide6`

**ROG tools missing (expected):**
- This is normal on non-ROG systems
- Application works without ROG tools with reduced functionality

**Linting errors:**
- Run `python3 -m black linux_armoury/` to auto-format code
- Focus on fixing critical errors (E9, F63, F7, F82) rather than all style issues

## Timing Expectations

**NEVER CANCEL these operations - they complete quickly:**
- Installation: ~15 seconds
- Core tests: ~1.2 seconds  
- Enhanced tests: ~0.1 seconds
- Linting: ~0.4 seconds
- Module imports: <1 second

**This is a fast-building Python project** - no long compilation steps required.