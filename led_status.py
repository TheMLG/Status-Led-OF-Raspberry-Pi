import RPi.GPIO as GPIO
import time
import threading
import subprocess
import psutil

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# 🔌 Pins
GREEN = 17   # WiFi
WHITE = 27   # SSH
RED = 18     # Temp
BLUE = 22    # RAM

GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(WHITE, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

# PWM
pwm_green = GPIO.PWM(GREEN, 1000)
pwm_white = GPIO.PWM(WHITE, 1000)
pwm_red = GPIO.PWM(RED, 1000)
pwm_blue = GPIO.PWM(BLUE, 1000)

for pwm in [pwm_green, pwm_white, pwm_red, pwm_blue]:
    pwm.start(0)

# -----------------------
# 💀 BOOT SEQUENCE
# -----------------------
def trail(pwms, delay=0.08):
    for pwm in pwms:
        pwm.ChangeDutyCycle(100)
        time.sleep(delay)
        pwm.ChangeDutyCycle(0)

def breathe_once(pwm, speed):
    for dc in range(0, 101, 5):
        pwm.ChangeDutyCycle(dc)
        time.sleep(speed)
    for dc in range(100, -1, -5):
        pwm.ChangeDutyCycle(dc)
        time.sleep(speed)

def boot_sequence():
    order = [pwm_green, pwm_white, pwm_red, pwm_blue]

    # Left → Right trail
    trail(order)

    # Right → Left trail
    trail(order[::-1])

    # Left 2 LEDs breathe x2
    for _ in range(2):
        breathe_once(pwm_green, 0.01)
        breathe_once(pwm_white, 0.01)

    # Right 2 LEDs breathe x2
    for _ in range(2):
        breathe_once(pwm_red, 0.01)
        breathe_once(pwm_blue, 0.01)

    # Final 5 flashes
    for _ in range(5):
        for pwm in order:
            pwm.ChangeDutyCycle(100)
        time.sleep(0.1)
        for pwm in order:
            pwm.ChangeDutyCycle(0)
        time.sleep(0.1)

# -----------------------
# STATUS CHECKS
# -----------------------
def wifi_connected():
    try:
        return subprocess.check_output("iwgetid", shell=True).decode() != ""
    except:
        return False

def wifi_monitor_mode():
    try:
        mode = subprocess.check_output("iw dev", shell=True).decode()
        return "type monitor" in mode
    except:
        return False

def ssh_active():
    try:
        output = subprocess.check_output("who", shell=True).decode()
        return "pts/" in output
    except:
        return False

def get_temp():
    temp = subprocess.check_output("vcgencmd measure_temp", shell=True).decode()
    return float(temp.replace("temp=", "").replace("'C\n", ""))

def get_ram():
    return psutil.virtual_memory().percent

# -----------------------
# BREATH FUNCTION
# -----------------------
def breathe_loop(pwm, speed_getter):
    while True:
        speed = speed_getter()

        for dc in range(0, 101, 3):
            pwm.ChangeDutyCycle(dc)
            time.sleep(speed)
        for dc in range(100, -1, -3):
            pwm.ChangeDutyCycle(dc)
            time.sleep(speed)

# -----------------------
# THREADS
# -----------------------

# 🟢 WiFi
def wifi_thread():
    while True:
        if wifi_monitor_mode():
            pwm_green.ChangeDutyCycle(100)
            time.sleep(1)
        elif wifi_connected():
            speed = 0.01  # medium
        else:
            speed = 0.003  # fast

        if not wifi_monitor_mode():
            for dc in range(0, 101, 3):
                pwm_green.ChangeDutyCycle(dc)
                time.sleep(speed)
            for dc in range(100, -1, -3):
                pwm_green.ChangeDutyCycle(dc)
                time.sleep(speed)

# ⚪ SSH
def ssh_thread():
    while True:
        if ssh_active():
            speed = 0.03  # very slow
            for dc in range(0, 101, 2):
                pwm_white.ChangeDutyCycle(dc)
                time.sleep(speed)
            for dc in range(100, -1, -2):
                pwm_white.ChangeDutyCycle(dc)
                time.sleep(speed)
        else:
            pwm_white.ChangeDutyCycle(0)
            time.sleep(1)

# 🔵 RAM
def ram_thread():
    while True:
        ram = get_ram()
        speed = 0.01 if ram < 70 else 0.003

        for dc in range(0, 101, 3):
            pwm_blue.ChangeDutyCycle(dc)
            time.sleep(speed)
        for dc in range(100, -1, -3):
            pwm_blue.ChangeDutyCycle(dc)
            time.sleep(speed)

# 🔴 TEMP
def temp_thread():
    while True:
        temp = get_temp()

        if temp < 40:
            speed = 0.03
        elif temp <= 60:
            speed = 0.01
        else:
            speed = 0.003

        for dc in range(0, 101, 3):
            pwm_red.ChangeDutyCycle(dc)
            time.sleep(speed)
        for dc in range(100, -1, -3):
            pwm_red.ChangeDutyCycle(dc)
            time.sleep(speed)

# -----------------------
# MAIN
# -----------------------
def main():
    boot_sequence()

    threading.Thread(target=wifi_thread, daemon=True).start()
    threading.Thread(target=ssh_thread, daemon=True).start()
    threading.Thread(target=ram_thread, daemon=True).start()
    threading.Thread(target=temp_thread, daemon=True).start()

    while True:
        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()