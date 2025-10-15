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
    info "Installing Linux Armoury GUI..."
    
    # Create installation directory
    INSTALL_DIR="/usr/local/bin"
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
    
    # Copy the Python script
    sudo install -m 755 linux-armoury-gui.py "$INSTALL_DIR/linux-armoury"
    
    # Create desktop entry
    sudo tee "$DESKTOP_DIR/linux-armoury.desktop" > /dev/null <<EOF
[Desktop Entry]
Type=Application
Name=Linux Armoury
Comment=Control Center for ASUS GZ302EA Laptop
Exec=linux-armoury
Icon=applications-system
Terminal=false
Categories=System;Settings;
Keywords=asus;laptop;tdp;power;performance;
StartupNotify=true
EOF
    
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
