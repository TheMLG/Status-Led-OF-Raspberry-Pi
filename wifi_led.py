import RPi.GPIO as GPIO
import time
import subprocess

PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

def wifi_status():
    try:
        # safer check
        result = subprocess.run(["iwgetid"], capture_output=True)
        if result.returncode == 0:
            return "connected"
        else:
            return "disconnected"
    except:
        return "disconnected"

state = False
last = 0

try:
    while True:
        now = time.time()
        status = wifi_status()

        interval = 0.5 if status == "connected" else 0.2

        if now - last > interval:
            state = not state
            GPIO.output(PIN, state)
            last = now

        time.sleep(0.05)

except Exception as e:
    print("Error:", e)
    GPIO.cleanup()