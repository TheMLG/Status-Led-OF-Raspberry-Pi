# Raspberry Pi Status LED Monitor 🎛️

A real-time status indicator system for Raspberry Pi using RGB LEDs to display system information at a glance.

## 📊 LED Status Indicators

This project uses 4 individual LEDs to monitor different system aspects:

| LED Color | GPIO Pin | Status Indicator | Details |
|-----------|----------|------------------|---------|
| 🔴 **Red** | GPIO 22 | **Temperature** | • Solid ON: CPU temp > 60°C<br>• Slow blink (0.5s): Temp < 50°C<br>• Fast blink (0.2s): Temp 50-60°C |
| 🟢 **Green** | GPIO 17 | **WiFi Connection** | • Slow blink (0.5s): Connected<br>• Fast blink (0.2s): Disconnected |
| 🔵 **Blue** | GPIO 18 | **RAM Usage** | • Slow blink (0.5s): Usage < 70%<br>• Fast blink (0.2s): Usage ≥ 70% |
| ⚪ **White** | GPIO 27 | **SSH Connection** | • Solid ON: Active SSH session<br>• OFF: No connection |

### 🎬 Boot Animation

On startup, all 4 LEDs display a beautiful initialization sequence:
- Left → Right sweep
- Right → Left sweep  
- Center pulse (Green + Blue)
- Edge pulse (Red + White)

## 🛠️ Hardware Requirements

- **Raspberry Pi** (any model with GPIO pins)
- **4 LEDs**: Red, Green, Blue, White
- **4 Resistors**: 220Ω-330Ω (current limiting)
- **Jumper Wires**
- **Breadboard** (optional)

## 📋 Wiring Diagram

Connect the LEDs to the following GPIO pins:

```
Raspberry Pi GPIO Header
┌─────────────────────┐
│ 3.3V    │    5V     │
│ GPIO2   │    5V     │
│ GPIO3   │    GND    │
│ GPIO4   │    14     │
│ GND     │    GPIO15 │
│ GPIO17  │    GPIO18 │ (Green LED)  (Blue LED)
│ GPIO27  │    GND    │ (White LED)
│ GPIO22  │    GPIO23 │ (Red LED)
│ 3.3V    │    GPIO24 │
│ GPIO10  │    GND    │
│ GPIO9   │    GPIO25 │
│ GPIO11  │    GPIO8  │
│ GND     │    GPIO7  │
└─────────────────────┘
```

**LED Connection (each LED):**
```
GPIO Pin ─→ [220Ω Resistor] ─→ [LED Anode] ─→ GND
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Python GPIO library
sudo apt-get install python3-rpi.gpio python3-pip -y

# Install additional tools
sudo apt-get install wireless-tools net-tools -y
```

### 2. Clone or Download Files

```bash
git clone https://github.com/TheMLG/Status-Led-OF-Raspberry-Pi.git
cd Status-led
```

Or upload all `.py` files and `.service` file to your Raspberry Pi.

### 3. Set Up Systemd Services

This project uses systemd services to run each LED monitor automatically on boot.

#### Create Service Files

For each LED module, create a systemd service file:

```bash
# For each service (replace FILENAME and FILE_PATH accordingly)
sudo nano /etc/systemd/system/boot-led.service
```

**Example `boot-led.service`:**
```ini
[Unit]
Description=Boot LED Animation
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/Status-led/boot_led.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

**Create similar files for:**
- `temp-led.service` → `/home/pi/Status-led/temp_led.py`
- `wifi-led.service` → `/home/pi/Status-led/wifi_led.py`
- `ram-led.service` → `/home/pi/Status-led/ram_led.py`
- `ssh-led.service` → `/home/pi/Status-led/ssh_led.py`

**Update the script paths** in each service file to match your installation directory.

#### Enable and Start Services

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable boot-led.service
sudo systemctl enable temp-led.service
sudo systemctl enable wifi-led.service
sudo systemctl enable ram-led.service
sudo systemctl enable ssh-led.service

# Start services immediately
sudo systemctl start boot-led.service
sudo systemctl start temp-led.service
sudo systemctl start wifi-led.service
sudo systemctl start ram-led.service
sudo systemctl start ssh-led.service
```

### 4. Verify Installation

Check the status of services:

```bash
sudo systemctl status boot-led.service
sudo systemctl status temp-led.service
sudo systemctl status wifi-led.service
sudo systemctl status ram-led.service
sudo systemctl status ssh-led.service
```

View logs:

```bash
sudo journalctl -u temp-led.service -f
```

## 📝 File Description

| File | Purpose |
|------|---------|
| `boot_led.py` | Boot animation sequence (runs once at startup) |
| `temp_led.py` | CPU temperature monitor |
| `wifi_led.py` | WiFi connection status monitor |
| `ram_led.py` | RAM usage monitor |
| `ssh_led.py` | SSH connection detector |
| `service_name.service` | Template for systemd service configuration |

## 🔧 Custom Configuration

### Modify GPIO Pins

Edit the `PIN` variable in each `.py` file to use different GPIO pins if needed:

```python
PIN = 22  # Change this to your desired GPIO pin
```

### Adjust Temperature Thresholds

In `temp_led.py`, modify these lines:

```python
if temp > 60:           # Change 60 to your threshold
    GPIO.output(PIN, GPIO.HIGH)
else:
    interval = 0.5 if temp < 50 else 0.2  # Change these values
```

### Adjust RAM Thresholds

In `ram_led.py`, modify this line:

```python
interval = 0.5 if ram < 70 else 0.2  # Change 70 to your threshold
```

## 🐛 Troubleshooting

**LEDs not lighting up:**
- Verify GPIO pins are correct
- Check LED polarity (longer leg is positive)
- Test with `raspi-gpio` tool: `raspi-gpio get=22`

**Services not starting:**
```bash
# Check for permission issues
sudo systemctl status temp-led.service

# View error logs
sudo journalctl -xe
```

**High CPU usage:**
- Increase `time.sleep()` values in scripts to reduce polling frequency
- Adjust intervals between status checks

**GPIO permission denied:**
```bash
# Run services as root (already configured in service files)
# Or add user to gpio group:
sudo usermod -a -G gpio pi
```

## 📜 License

This project is open source and available on GitHub: [Status-Led-OF-Raspberry-Pi](https://github.com/TheMLG/Status-Led-OF-Raspberry-Pi)

## 🤝 Contributing

Feel free to fork, modify, and improve this project!

## 📧 Support

For issues or questions, please open an issue on the GitHub repository.

---

**Made with ❤️ for Raspberry Pi enthusiasts**
