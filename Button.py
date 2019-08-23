
import RPi.GPIO as GPIO
import time

count=8
push_pin=4

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(push_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

for i in range(count):
   print("Starting")
   print(GPIO.input(push_pin))
   time.sleep(1)

GPIO.cleanup()
