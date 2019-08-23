import RPi.GPIO as GPIO
import time

count = 10
led_pin = 17

GPIO.setmode(GPIO.BCM) # Use BCM for GPIO numbering
GPIO.setwarnings(False)
GPIO.setup(led_pin, GPIO.OUT)

for i in range(count):
    print("Led on")
    GPIO.output(led_pin, GPIO.HIGH)
    time.sleep(1)
    print("Led off")
    GPIO.output(led_pin, GPIO.LOW)
    time.sleep(1)

GPIO.cleanup()
