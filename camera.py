import time
import math
import RPi.GPIO as GPIO
from PCA9685 import PCA9685
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180
camera.start_preview()
sleep(5)
camera.stop_preview()
