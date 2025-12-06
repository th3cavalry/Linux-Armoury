#!/bin/bash

# ==============================================================================
# Linux Armoury Installation Script
# Installs the GUI control center for ASUS GZ302EA laptops
# ==============================================================================

set -euo pipefail

# Color codes
C_BLUE='\033[0;34m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'
C_NC='\033[0m'

info() {
    echo -e "${C_BLUE}[INFO]${C_NC} $1"
}

success() {
    echo -e "${C_GREEN}[SUCCESS]${C_NC} $1"
}

warning() {
    echo -e "${C_YELLOW}[WARNING]${C_NC} $1"
}

error() {
    echo -e "${C_RED}[ERROR]${C_NC} $1"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "This script should NOT be run as root. Run as a regular user."
fi

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
        DISTRO_LIKE=${ID_LIKE:-}
    else
        error "Cannot detect Linux distribution"
    fi
}

# Install dependencies for Arch-based systems
install_arch_deps() {
    info "Installing dependencies for Arch-based system..."
    sudo pacman -S --noconfirm --needed \
        python python-gobject gtk4 libadwaita \
        polkit xorg-xrandr
    success "Dependencies installed"
}

# Install dependencies for Debian-based systems
install_debian_deps() {
    info "Installing dependencies for Debian-based system..."
    sudo apt update
    sudo apt install -y \
        python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \
        policykit-1 x11-xserver-utils
    success "Dependencies installed"
}

# Install dependencies for Fedora-based systems
install_fedora_deps() {
    info "Installing dependencies for Fedora-based system..."
    sudo dnf install -y \
        python3 python3-gobject gtk4 libadwaita \
        polkit xrandr
    success "Dependencies installed"
}

# Install dependencies for OpenSUSE
install_opensuse_deps() {
    info "Installing dependencies for OpenSUSE..."
    sudo zypper install -y \
        python3 python3-gobject gtk4 libadwaita-1-0 \
        polkit xrandr
    success "Dependencies installed"
}

# Install the application
install_application() {
    info "Installing Linux Armoury GUI and CLI..."
    
    # Directories
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
    DBUS_CONF_DIR="/etc/dbus-1/system.d"
    SYSTEMD_DIR="/etc/systemd/system"
    
    # Install Python package
    info "Installing Python package..."
    if ! sudo pip install . --break-system-packages 2>/dev/null; then
        sudo pip install .
    fi
    
    # Install app icon
    if [ -f data/icons/linux-armoury.svg ]; then
        sudo mkdir -p "$ICON_DIR"
        sudo install -m 644 data/icons/linux-armoury.svg "$ICON_DIR/linux-armoury.svg"
        info "App icon installed"
    fi
    
    # Install D-Bus configuration
    if [ -f data/dbus/com.github.th3cavalry.LinuxArmoury.conf ]; then
        sudo mkdir -p "$DBUS_CONF_DIR"
        sudo install -m 644 data/dbus/com.github.th3cavalry.LinuxArmoury.conf "$DBUS_CONF_DIR/"
        info "D-Bus configuration installed"
    fi
    
    # Install systemd service
    if [ -f data/systemd/linux-armoury.service ]; then
        sudo install -m 644 data/systemd/linux-armoury.service "$SYSTEMD_DIR/"
        sudo systemctl daemon-reload
        info "Systemd service installed (enable with: sudo systemctl enable linux-armoury)"
    fi
    
    # Install desktop entries (legacy and DBus activatable)
    sudo install -m 644 linux-armoury.desktop "$DESKTOP_DIR/linux-armoury.desktop"
    if [ -f com.github.th3cavalry.linux-armoury.desktop ]; then
        sudo install -m 644 com.github.th3cavalry.linux-armoury.desktop "$DESKTOP_DIR/com.github.th3cavalry.linux-armoury.desktop"
    fi
    
    # Install autostart entry (starts minimized to tray on boot)
    info "Installing autostart entry..."
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    if [ -f linux-armoury-autostart.desktop ]; then
        install -m 644 linux-armoury-autostart.desktop "$AUTOSTART_DIR/linux-armoury.desktop"
        success "Autostart entry installed - Linux Armoury will start on boot"
    fi
    
    # Update desktop database and icon cache
    if command -v update-desktop-database &> /dev/null; then
        sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache &> /dev/null; then
        sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
    fi
    
    success "Application installed"
}

# Main installation flow
main() {
    echo
    echo "============================================================"
    echo "  Linux Armoury GUI Installation"
    echo "============================================================"
    echo
    
    # Detect distribution
    detect_distro
    
    # Install dependencies based on distribution
    case "$DISTRO_ID" in
        arch|manjaro|endeavouros)
            install_arch_deps
            ;;
        ubuntu|debian|pop|linuxmint)
            install_debian_deps
            ;;
        fedora|nobara)
            install_fedora_deps
            ;;
        opensuse*|suse)
            install_opensuse_deps
            ;;
        *)
            # Check ID_LIKE for derivative distributions
            if [[ "$DISTRO_LIKE" == *"arch"* ]]; then
                install_arch_deps
            elif [[ "$DISTRO_LIKE" == *"debian"* ]] || [[ "$DISTRO_LIKE" == *"ubuntu"* ]]; then
                install_debian_deps
            elif [[ "$DISTRO_LIKE" == *"fedora"* ]]; then
                install_fedora_deps
            elif [[ "$DISTRO_LIKE" == *"suse"* ]]; then
                install_opensuse_deps
            else
                error "Unsupported distribution: $DISTRO_ID"
            fi
            ;;
    esac
    
    # Install the application
    install_application
    
    echo
    success "Installation complete!"
    echo
    info "You can now launch Linux Armoury from your application menu"
    info "or run 'linux-armoury' from the terminal"
    echo
    warning "Note: This GUI integrates with GZ302 management tools (pwrcfg, rrcfg)"
    warning "Make sure you have installed the GZ302-Linux-Setup scripts first"
    warning "See: https://github.com/th3cavalry/GZ302-Linux-Setup"
    echo
}

main "$@"
