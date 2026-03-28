import RPi.GPIO as GPIO
import time

# Your LED order
PINS = [
    22,  # 🔴 Red (Temp)
    17,  # 🟢 Green (WiFi)
    18,  # 🔵 Blue (RAM)
    27   # ⚪ White (SSH)
]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# ----------------------------
# 🔥 BOOT ANIMATION
# ----------------------------

# 1️⃣ Left → Right Sweep
for _ in range(2):
    for pin in PINS:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.15)
        GPIO.output(pin, GPIO.LOW)

# 2️⃣ Right → Left Sweep
for _ in range(2):
    for pin in reversed(PINS):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.15)
        GPIO.output(pin, GPIO.LOW)

# 3️⃣ Center Pulse (Green + Blue)
for _ in range(3):
    GPIO.output(17, GPIO.HIGH)  # Green
    GPIO.output(18, GPIO.HIGH)  # Blue
    time.sleep(0.2)
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    time.sleep(0.2)

# 4️⃣ Edge Pulse (Red + White)
for _ in range(3):
    GPIO.output(22, GPIO.HIGH)  # Red
    GPIO.output(27, GPIO.HIGH)  # White
    time.sleep(0.2)
    GPIO.output(22, GPIO.LOW)
    GPIO.output(27, GPIO.LOW)
    time.sleep(0.2)

# 5️⃣ All Blink Finale
for _ in range(4):
    for pin in PINS:
        GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.25)
    for pin in PINS:
        GPIO.output(pin, GPIO.LOW)
    time.sleep(0.25)

GPIO.cleanup()