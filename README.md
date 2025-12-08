
<div align="center">
  <img src="assets/rog_logo.png" alt="Linux Armoury Logo" width="200"/>
  <h1>Linux Armoury</h1>
  <p><b>A modern, lightweight GUI control center for ASUS ROG and other ASUS gaming laptops.</b></p>
  <p>
    <a href="https://github.com/th3cavalry/Linux-Armoury/releases"><img src="https://img.shields.io/github/v/release/th3cavalry/Linux-Armoury" alt="Version"></a>
    <a href="https://github.com/th3cavalry/Linux-Armoury/blob/main/LICENSE"><img src="https://img.shields.io/github/license/th3cavalry/Linux-Armoury" alt="License"></a>
    <a href="https://github.com/th3cavalry/Linux-Armoury/actions/workflows/lint.yml"><img src="https://github.com/th3cavalry/Linux-Armoury/actions/workflows/lint.yml/badge.svg" alt="Lint"></a>
  </p>
</div>

---

Linux Armoury is a user-friendly application that allows you to control various aspects of your ASUS gaming laptop, such as power profiles, display refresh rates, and keyboard lighting. It is inspired by G-Helper and ROG Control Center, and it provides a simple and intuitive interface for managing your laptop's performance.

## ✨ Features

- **Modern and Intuitive UI:** A clean and easy-to-use interface built with GTK 4 and libadwaita.
- **Power Profiles:** Switch between multiple power profiles to optimize performance and battery life.
- **Refresh Rate Control:** Change your display's refresh rate on the fly.
- **System Monitoring:** Keep an eye on your CPU and GPU temperatures, battery status, and more.
- **Autostart:** Automatically start the application on system boot.
- **System Tray Integration:** Minimize the application to the system tray for quick access.
- **Auto Profile Switching:** Automatically switch between power profiles when you plug in or unplug your laptop.

## 🚀 Installation

### Flatpak (Recommended)

The recommended way to install Linux Armoury is via Flatpak. This method works on most modern Linux distributions and provides a sandboxed environment for the application.

```bash
flatpak install flathub com.github.th3cavalry.linux-armoury
```

### Traditional Installation

If you prefer a traditional installation, you can use the provided installation script.

```bash
git clone https://github.com/th3cavalry/Linux-Armoury.git
cd Linux-Armoury
chmod +x install.sh
./install.sh
```

## 📖 Usage

After installation, you can launch Linux Armoury from your application menu. The application will automatically detect your hardware and provide you with the available options.

## 🤝 Contributing

Contributions are welcome! Please read the [contributing guidelines](docs/CONTRIBUTING.md) to get started.

## 📜 License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.
