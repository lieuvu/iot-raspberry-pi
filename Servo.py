import RPi.GPIO as GPIO
import time

print("Running Servo...")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 50) # pin and frequency
p.start(5) # Start at 0 degree

try:
    while True:
        p.ChangeDutyCycle(6)
        time.sleep(1)
        p.ChangeDutyCycle(7.5)  # turn towards 90 degree
        time.sleep(1) # sleep 1 second
        p.ChangeDutyCycle(9)  # turn towards 180 degree
        time.sleep(1) # sleep 1 second
        p.ChangeDutyCycle(10) # turn towards 180 degree
        time.sleep(1) # sleep 1 second
        p.ChangeDutyCycle(9)
        time.sleep(1)
        p.ChangeDutyCycle(7.5)
        time.sleep(1)
         
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()
