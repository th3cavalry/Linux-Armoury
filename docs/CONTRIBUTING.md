# Contributing to Linux Armoury

Thank you for your interest in contributing to Linux Armoury! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title** - Descriptive and specific
- **Steps to reproduce** - Detailed sequence of steps
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **System information**:
  - Linux distribution and version
  - Kernel version (`uname -r`)
  - Python version
  - GTK/Adwaita versions
  - Laptop model (if applicable)
- **Screenshots** - If relevant
- **Logs** - Any error messages or console output

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear use case** - Why is this feature needed?
- **Detailed description** - How should it work?
- **Alternative solutions** - Other approaches you've considered
- **Mockups/examples** - Visual aids if applicable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Setup

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# Arch Linux
sudo pacman -S python python-gobject gtk4 libadwaita

# Fedora
sudo dnf install python3 python3-gobject gtk4 libadwaita
```

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Linux-Armoury.git
cd Linux-Armoury

# Run the application
python3 linux-armoury-gui.py

# Or make it executable
chmod +x linux-armoury-gui.py
./linux-armoury-gui.py
```

### Testing Changes

```bash
# Test basic functionality
./linux-armoury-gui.py

# Test different themes
# (Use the UI menu to switch themes)

# Test autostart
# Enable in Preferences and check ~/.config/autostart/

# Verify no errors
python3 -m py_compile linux-armoury-gui.py
```

## Coding Standards

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these guidelines:

```python
# Good
def create_power_profile_section(self):
    """Create the power profile control section"""
    group = Adw.PreferencesGroup()
    group.set_title("Power Profiles")
    return group

# Bad
def createPowerProfileSection(self):
    group = Adw.PreferencesGroup()
    group.set_title("Power Profiles")
    return group
```

### Key Principles

1. **Readability** - Code should be self-documenting
2. **Simplicity** - Prefer simple solutions
3. **Consistency** - Match existing code style
4. **Documentation** - Add docstrings to functions
5. **Error Handling** - Always handle exceptions gracefully

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `LinuxArmouryApp`)
- **Functions/Methods**: `snake_case` (e.g., `apply_power_profile`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `CONFIG_DIR`)
- **Private members**: Prefix with `_` (e.g., `_internal_method`)

### Documentation

```python
def apply_power_profile(self, profile: str) -> bool:
    """
    Apply a power profile using pwrcfg command.

    Args:
        profile: Name of the profile to apply (e.g., 'balanced', 'gaming')

    Returns:
        True if profile was applied successfully, False otherwise

    Raises:
        subprocess.TimeoutExpired: If the command times out
        subprocess.CalledProcessError: If pwrcfg returns an error
    """
    # Implementation
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(ui): add system tray icon support

- Implement tray icon using libayatana-appindicator
- Add quick access menu for power profiles
- Add show/hide window functionality

Closes #42
```

```
fix(power): handle missing pwrcfg command gracefully

Show user-friendly error message when pwrcfg is not installed
instead of crashing the application.

Fixes #38
```

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All functions have docstrings
- [ ] Changes are tested locally
- [ ] No syntax errors or warnings
- [ ] README updated if needed
- [ ] CHANGELOG updated (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test these changes

## Screenshots
If applicable

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tested on target platform
```

### Review Process

1. Automated checks must pass
2. At least one maintainer review required
3. All comments must be addressed
4. Squash commits if requested
5. Maintainer will merge when approved

## Testing

### Manual Testing

Test the following before submitting:

1. **Launch** - Application starts without errors
2. **Theme switching** - Light/dark/auto modes work
3. **Power profiles** - Can apply different profiles
4. **Refresh rates** - Display settings change correctly
5. **Preferences** - Settings save and persist
6. **Autostart** - Desktop file created correctly
7. **Error handling** - Graceful failures with clear messages

### Platform Testing

If possible, test on multiple distributions:
- Arch-based (Arch, Manjaro, EndeavourOS)
- Debian-based (Ubuntu, Pop!_OS, Mint)
- RPM-based (Fedora, Nobara)
- OpenSUSE (Tumbleweed, Leap)

### Test Cases

```bash
# Test 1: Basic launch
python3 linux-armoury-gui.py

# Test 2: Permission handling (should ask for password)
# Click "Apply" on a power profile

# Test 3: Configuration persistence
# Change theme, close app, reopen
# Theme should be remembered

# Test 4: Error handling
# Rename pwrcfg temporarily
# Application should show error, not crash
```

## Adding New Features

### Feature Development Workflow

1. **Create issue** - Discuss the feature first
2. **Get feedback** - Wait for maintainer input
3. **Design** - Plan the implementation
4. **Implement** - Write the code
5. **Test** - Verify it works
6. **Document** - Update README/docs
7. **Submit PR** - Follow PR template

### Adding a New Power Profile

```python
# In create_power_profile_section method
profiles = [
    # Add new profile here
    ("custom", "Custom Profile", "50W @ 144Hz - Custom settings"),
    # ...
]
```

### Adding a New Feature

1. Update UI in `setup_ui()` or relevant method
2. Add action handler
3. Update settings schema if needed
4. Add to preferences if user-configurable
5. Document in README.md

## Questions?

- **Issues**: [GitHub Issues](https://github.com/th3cavalry/Linux-Armoury/issues)
- **Discussions**: [GitHub Discussions](https://github.com/th3cavalry/Linux-Armoury/discussions)

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.

---

Thank you for contributing to Linux Armoury! 🎉
