import RPi.GPIO as GPIO
import subprocess
import time

PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

def ssh_active():
    try:
        # Check active SSH connections on port 22
        result = subprocess.check_output(
            "ss -tn state established '( sport = :22 )'", 
            shell=True
        ).decode()

        # If more than header line → connection exists
        return len(result.strip().split("\n")) > 1

    except:
        return False

try:
    while True:
        if ssh_active():
            GPIO.output(PIN, GPIO.HIGH)
        else:
            GPIO.output(PIN, GPIO.LOW)

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()