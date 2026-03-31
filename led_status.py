import RPi.GPIO as GPIO
import time
import threading
import subprocess
import psutil

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Pins
PINS = {
    "wifi": 17,
    "ssh": 27,
    "temp": 18,
    "ram": 22
}

# Setup
for pin in PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# PWM init
pwms = {}
for key, pin in PINS.items():
    pwm = GPIO.PWM(pin, 1000)
    pwm.start(0)
    pwms[key] = pwm

# -----------------------
# LED CLASS (CORE ENGINE)
# -----------------------
class BreathingLED:
    def __init__(self, pwm):
        self.pwm = pwm
        self.speed = 0.01
        self.mode = "breathing"  # breathing / solid / off
        self.value = 0
        self.direction = 1

    def update(self):
        if self.mode == "off":
            self.pwm.ChangeDutyCycle(0)
            return

        if self.mode == "solid":
            self.pwm.ChangeDutyCycle(100)
            return

        # breathing mode
        self.value += self.direction * 3

        if self.value >= 100:
            self.value = 100
            self.direction = -1
        elif self.value <= 0:
            self.value = 0
            self.direction = 1

        self.pwm.ChangeDutyCycle(self.value)

# -----------------------
# STATUS FUNCTIONS
# -----------------------
def wifi_connected():
    try:
        return subprocess.check_output("iwgetid", shell=True).decode() != ""
    except:
        return False

def wifi_monitor_mode():
    try:
        return "type monitor" in subprocess.check_output("iw dev", shell=True).decode()
    except:
        return False

def ssh_active():
    try:
        output = subprocess.check_output("ss -tnp | grep sshd", shell=True).decode()
        return "ESTAB" in output
    except:
        return False

def get_temp():
    t = subprocess.check_output("vcgencmd measure_temp", shell=True).decode()
    return float(t.replace("temp=", "").replace("'C\n", ""))

def get_ram():
    return psutil.virtual_memory().percent

# -----------------------
# BOOT SEQUENCE (NON-BLOCKING STYLE)
# -----------------------
def boot_sequence():
    order = ["wifi", "ssh", "temp", "ram"]

    # trail →
    for k in order:
        pwms[k].ChangeDutyCycle(100)
        time.sleep(0.08)
        pwms[k].ChangeDutyCycle(0)

    # trail ←
    for k in reversed(order):
        pwms[k].ChangeDutyCycle(100)
        time.sleep(0.08)
        pwms[k].ChangeDutyCycle(0)

    # left breathe x2
    for _ in range(2):
        for dc in range(0, 101, 5):
            pwms["wifi"].ChangeDutyCycle(dc)
            pwms["ssh"].ChangeDutyCycle(dc)
            time.sleep(0.01)
        for dc in range(100, -1, -5):
            pwms["wifi"].ChangeDutyCycle(dc)
            pwms["ssh"].ChangeDutyCycle(dc)
            time.sleep(0.01)

    # right breathe x2
    for _ in range(2):
        for dc in range(0, 101, 5):
            pwms["temp"].ChangeDutyCycle(dc)
            pwms["ram"].ChangeDutyCycle(dc)
            time.sleep(0.01)
        for dc in range(100, -1, -5):
            pwms["temp"].ChangeDutyCycle(dc)
            pwms["ram"].ChangeDutyCycle(dc)
            time.sleep(0.01)

    # flash x5
    for _ in range(5):
        for pwm in pwms.values():
            pwm.ChangeDutyCycle(100)
        time.sleep(0.1)
        for pwm in pwms.values():
            pwm.ChangeDutyCycle(0)
        time.sleep(0.1)

# -----------------------
# MAIN ENGINE
# -----------------------
leds = {k: BreathingLED(pwms[k]) for k in pwms}

def status_updater():
    while True:

        # WIFI
        if wifi_monitor_mode():
            leds["wifi"].mode = "solid"
        elif wifi_connected():
            leds["wifi"].mode = "breathing"
            leds["wifi"].speed = 0.01
        else:
            leds["wifi"].mode = "breathing"
            leds["wifi"].speed = 0.003

        # SSH
        if ssh_active():
            leds["ssh"].mode = "breathing"
            leds["ssh"].speed = 0.03
        else:
            leds["ssh"].mode = "off"

        # RAM
        ram = get_ram()
        leds["ram"].mode = "breathing"
        leds["ram"].speed = 0.01 if ram < 70 else 0.003

        # TEMP
        temp = get_temp()
        leds["temp"].mode = "breathing"
        if temp < 40:
            leds["temp"].speed = 0.03
        elif temp <= 60:
            leds["temp"].speed = 0.01
        else:
            leds["temp"].speed = 0.003

        time.sleep(2)

def animation_loop():
    while True:
        for led in leds.values():
            led.update()
        time.sleep(0.01)

# -----------------------
# START
# -----------------------
try:
    boot_sequence()

    threading.Thread(target=status_updater, daemon=True).start()
    threading.Thread(target=animation_loop, daemon=True).start()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()