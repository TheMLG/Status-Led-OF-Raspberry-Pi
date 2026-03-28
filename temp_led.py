import RPi.GPIO as GPIO
import subprocess
import time

PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

state = False
last = 0

def get_temp():
    try:
        temp = subprocess.check_output("vcgencmd measure_temp", shell=True).decode()
        return float(temp.replace("temp=", "").replace("'C\n", ""))
    except:
        return 0

try:
    while True:
        now = time.time()
        temp = get_temp()

        if temp > 60:
            GPIO.output(PIN, GPIO.HIGH)

        else:
            interval = 0.5 if temp < 50 else 0.2
            if now - last > interval:
                state = not state
                GPIO.output(PIN, state)
                last = now

        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()