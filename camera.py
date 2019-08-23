
from picamera import PiCamera
from time import sleep

print('Starting camera...')

camera = PiCamera()

camera.start_preview()
sleep(10)
camera.capture('/home/pi/Desktop/image.jpeg')
camera.stop_preview()
