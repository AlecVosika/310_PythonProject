#!/usr/bin/env python

# Control Lasermodule from Raspberry Pi
# https://raspberrytips.nl/laser-module-aansturen-via-gpio/

import RPi.GPIO as GPIO
import time

LaserGPIO = 26 # --> PIN11/GPIO17

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
GPIO.setup(LaserGPIO, GPIO.OUT)
GPIO.output(LaserGPIO, GPIO.HIGH)


loop = True
print('1=on  |  2=Off')
UserInput = input('Input: ')

while loop == True:
    if UserInput == '1':
        print('Laser=on')
        GPIO.output(LaserGPIO, GPIO.HIGH) # led on
        print('1=on  |  2=Off')
        UserInput = input('Input: ')
    elif UserInput == '2':	
        print('Laser=off')
        GPIO.output(LaserGPIO, GPIO.LOW) # led off
        print('1=on  |  2=Off')
        UserInput = input('Input: ')
    else:
        loop = False
        GPIO.output(LaserGPIO, GPIO.LOW)
        GPIO.cleanup()

