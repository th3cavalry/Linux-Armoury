#!/bin/bash

# ==============================================================================
# Linux Armoury Installation Script
# Installs the GUI control center for ASUS ROG and other ASUS gaming laptops
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
        # shellcheck disable=SC1091
        . /etc/os-release
        DISTRO_ID=$ID
        DISTRO_LIKE=${ID_LIKE:-}
    else
        error "Cannot detect Linux distribution"
    fi
}

# Detect hardware configuration
detect_hardware() {
    info "Detecting hardware configuration..."

    # CPU Detection
    if grep -q "AuthenticAMD" /proc/cpuinfo; then
        info "CPU: AMD detected"
    elif grep -q "GenuineIntel" /proc/cpuinfo; then
        info "CPU: Intel detected"
    else
        info "CPU: Unknown vendor"
    fi

    # GPU Detection
    HAS_NVIDIA=false
    if lspci | grep -i "NVIDIA" > /dev/null; then
        HAS_NVIDIA=true
        info "GPU: NVIDIA detected"
    fi
    HAS_AMD_GPU=false
    if lspci | grep -i "AMD" > /dev/null || lspci | grep -i "ATI" > /dev/null; then
        HAS_AMD_GPU=true
        info "GPU: AMD detected"
    fi

    # ASUS Laptop Detection
    IS_ASUS=false
    if [ -d "/sys/class/dmi/id" ]; then
        if grep -qi "ASUS" /sys/class/dmi/id/sys_vendor 2>/dev/null; then
            IS_ASUS=true
            info "System: ASUS laptop detected"
        fi
    fi
}

# Install dependencies for Arch-based systems
install_arch_deps() {
    info "Installing dependencies for Arch-based system..."
    sudo pacman -S --noconfirm --needed \
        python python-gobject gtk4 libadwaita \
        polkit xorg-xrandr pciutils power-profiles-daemon \
        python-pip lm_sensors libayatana-appindicator git
    success "Dependencies installed"
}

# Install dependencies for Debian-based systems
install_debian_deps() {
    info "Installing dependencies for Debian-based system..."
    sudo apt update
    sudo apt install -y \
        python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \
        policykit-1 x11-xserver-utils pciutils power-profiles-daemon \
        python3-pip lm-sensors gir1.2-ayatanaappindicator3-0.1 git
    success "Dependencies installed"
}

# Install dependencies for Fedora-based systems
install_fedora_deps() {
    info "Installing dependencies for Fedora-based system..."
    sudo dnf install -y \
        python3 python3-gobject gtk4 libadwaita \
        polkit xrandr pciutils power-profiles-daemon \
        python3-pip lm_sensors libayatana-appindicator-gtk3 git
    success "Dependencies installed"
}

# Install dependencies for OpenSUSE
install_opensuse_deps() {
    info "Installing dependencies for OpenSUSE..."
    sudo zypper install -y \
        python3 python3-gobject gtk4 libadwaita-1-0 \
        polkit xrandr pciutils power-profiles-daemon \
        python3-pip sensors libayatana-appindicator3-1 git
    success "Dependencies installed"
}

# Install ASUS tools for Arch
install_arch_asus_tools() {
    info "Configuring ASUS tools for Arch..."

    # Add g14 repo if not present
    if ! grep -q "\[g14\]" /etc/pacman.conf; then
        info "Adding g14 repository..."
        sudo pacman-key --recv-keys 8F654886F17D497FEFE3DB448B15A6B0E9A3FA35
        sudo pacman-key --lsign-key 8F654886F17D497FEFE3DB448B15A6B0E9A3FA35
        echo -e "
[g14]
Server = https://arch.asus-linux.org" | sudo tee -a /etc/pacman.conf
        sudo pacman -Sy
    fi

    sudo pacman -S --noconfirm --needed asusctl

    if [ "$HAS_NVIDIA" = true ] || [ "$HAS_AMD_GPU" = true ]; then
        sudo pacman -S --noconfirm --needed supergfxctl
        sudo systemctl enable --now supergfxd
    fi

    sudo systemctl enable --now asusd
}

# Install ASUS tools for Fedora
install_fedora_asus_tools() {
    info "Configuring ASUS tools for Fedora..."
    sudo dnf copr enable -y lukenukem/asus-linux
    sudo dnf install -y asusctl

    if [ "$HAS_NVIDIA" = true ] || [ "$HAS_AMD_GPU" = true ]; then
        sudo dnf install -y supergfxctl
        sudo systemctl enable --now supergfxd
    fi

    sudo systemctl enable --now asusd
}

# Install ASUS tools for Debian/Ubuntu
install_debian_asus_tools() {
    info "Configuring ASUS tools for Debian/Ubuntu..."
    # Check for PPA support
    if command -v add-apt-repository >/dev/null; then
        if ! grep -r "mitchellaugustin/asusctl" /etc/apt/sources.list /etc/apt/sources.list.d/ >/dev/null 2>&1; then
            info "Adding ASUS PPA..."
            sudo add-apt-repository -y ppa:mitchellaugustin/asusctl
            sudo apt update
        else
            info "ASUS PPA already configured."
        fi

        sudo apt install -y asusctl

        if [ "$HAS_NVIDIA" = true ] || [ "$HAS_AMD_GPU" = true ]; then
            sudo apt install -y supergfxctl
            sudo systemctl enable --now supergfxd
        fi

        sudo systemctl enable --now asusd
    else
        warning "add-apt-repository not found. Skipping automatic asusctl installation."
        info "Please install asusctl manually from https://asus-linux.org"
    fi
}

# Install ASUS tools for OpenSUSE
install_opensuse_asus_tools() {
    info "Configuring ASUS tools for OpenSUSE..."

    if grep -q "Tumbleweed" /etc/os-release; then
        sudo zypper ar -f https://download.opensuse.org/repositories/hardware:/asus/openSUSE_Tumbleweed/ hardware:asus
    elif grep -q "Leap 15.6" /etc/os-release; then
        sudo zypper ar -f https://download.opensuse.org/repositories/hardware:/asus/openSUSE_Leap_15.6/ hardware:asus
    fi

    sudo zypper ref
    sudo zypper install -y asusctl

    if [ "$HAS_NVIDIA" = true ] || [ "$HAS_AMD_GPU" = true ]; then
        sudo zypper install -y supergfxctl
        sudo systemctl enable --now supergfxd
    fi

    sudo systemctl enable --now asusd
}

# Main hardware tool installer
install_hardware_tools() {
    if [ "$IS_ASUS" = true ]; then
        case "$DISTRO_ID" in
            arch|manjaro|endeavouros|cachyos)
                install_arch_asus_tools
                ;;
            fedora|nobara)
                install_fedora_asus_tools
                ;;
            ubuntu|debian|pop|linuxmint)
                install_debian_asus_tools
                ;;
            opensuse*|suse)
                install_opensuse_asus_tools
                ;;
        esac
    else
        warning "Not an ASUS laptop (or detection failed). Skipping ASUS-specific tools."
    fi
}

# Install the application
install_application() {
    info "Installing Linux Armoury GUI and CLI..."

    # Directories
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
    DBUS_CONF_DIR="/etc/dbus-1/system.d"
    SYSTEMD_DIR="/etc/systemd/system"
    POLKIT_DIR="/usr/share/polkit-1/actions"

    # Install Python package
    info "Installing Python package..."
    if ! sudo python3 -m pip install . --break-system-packages 2>/dev/null; then
        sudo python3 -m pip install .
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

    # Install udev rules
    if [ -f data/udev/99-linux-armoury.rules ]; then
        info "Installing udev rules..."
        sudo install -m 644 data/udev/99-linux-armoury.rules /etc/udev/rules.d/
        sudo udevadm control --reload-rules
        sudo udevadm trigger

        # Ensure user is in video group
        if ! groups "$USER" | grep -q video; then
            info "Adding user to 'video' group for backlight control..."
            sudo usermod -aG video "$USER"
            warning "You may need to log out and back in for group changes to take effect."
        fi
    fi

    # Install polkit policy for passwordless privilege escalation
    if [ -f data/polkit/com.github.th3cavalry.linux-armoury.policy ]; then
        info "Installing polkit policy for passwordless hardware control..."
        sudo mkdir -p "$POLKIT_DIR"
        sudo install -m 644 data/polkit/com.github.th3cavalry.linux-armoury.policy "$POLKIT_DIR/"
        info "Polkit policy installed - hardware settings can be changed without password prompts"
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
        install -m 644 linux-armoury-autostart.desktop "$AUTOSTART_DIR/linux-armoury-autostart.desktop"
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

    # Detect hardware
    detect_hardware

    # Install dependencies based on distribution
    case "$DISTRO_ID" in
        arch|manjaro|endeavouros|cachyos)
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

    # Install hardware tools (asusctl, supergfxctl, etc.)
    install_hardware_tools

    # Install the application
    install_application

    echo
    success "Installation complete!"
    echo
    info "You can now launch Linux Armoury from your application menu"
    info "or run 'linux-armoury' from the terminal"
    echo
}

main "$@"
