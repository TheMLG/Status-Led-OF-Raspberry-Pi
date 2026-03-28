import RPi.GPIO as GPIO
import time

PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

state = False
last = 0

def get_ram():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()

        total = int(lines[0].split()[1])
        available = int(lines[2].split()[1])
        used = total - available

        return (used / total) * 100
    except:
        return 0

try:
    while True:
        now = time.time()
        ram = get_ram()

        # Debug (optional)
        # print("RAM:", ram)

        interval = 0.5 if ram < 70 else 0.2

        if now - last > interval:
            state = not state
            GPIO.output(PIN, state)
            last = now

        time.sleep(0.05)

except Exception as e:
    print("Error:", e)
    GPIO.cleanup()