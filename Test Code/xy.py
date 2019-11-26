import time
import math
import RPi.GPIO as GPIO
from PCA9685 import PCA9685
from picamera import PiCamera
from time import sleep
    
    
LaserGPIO = 26 # --> PIN11/GPIO17


GPIO.setmode(GPIO.BCM)
GPIO.setup(LaserGPIO, GPIO.OUT)
GPIO.output(LaserGPIO, GPIO.HIGH)   

GPIO.output(LaserGPIO, GPIO.HIGH) # led on    
    

pwm = PCA9685()
PWM_FREQ = 50
pwm.setPWMFreq(PWM_FREQ)
yaw = 97.5
pitch = 90
pwm.setRotationAngle(0, yaw)
pwm.setRotationAngle(1, pitch)
time.sleep(.5)


pwm.exit_PCA9685()
#GPIO.cleanup()




        


