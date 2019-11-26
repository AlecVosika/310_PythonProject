import time
import math
import RPi.GPIO as GPIO
from PCA9685 import PCA9685
from picamera import PiCamera
from time import sleep

import sys
import time
from queue import Queue
from PIL import Image

# -m pip install imageio --user
import imageio


def iswhite(value):
    if value == (255,255,255) or value == (0,255,0) or value == (255,0,0): 
        return True

def getadjacent(n):
    x,y = n
    return [(x-1,y),(x,y-1),(x+1,y),(x,y+1),
            (x-1,y-1),(x+1,y-1),(x+1,y+1),(x-1,y+1)]

def BFS(start, end, pixels):
    # Used for the gif creation
    count = 0
    gif = []

    queue = Queue()
    queue.put([start]) # Wrapping the start tuple in a list

    while not queue.empty():

        path = queue.get() 
        pixel = path[-1]

        if pixel == end:
            imageio.mimsave('gif.gif', gif)
            return path

        for adjacent in getadjacent(pixel):
            x,y = adjacent

            if iswhite(pixels[x,y]):
                pixels[x,y] = (127,127,127) # Marks a white visited pixel grey. This
                                            # removes the need for a visited list.
                new_path = list(path)
                new_path.append(adjacent)
                queue.put(new_path)

                # Count is used for gif creation
                count = count + 1
                # Used to save the grayed image and create a gif
                if count % 2000 == 0:
                    base_img.save("grey_img.png")
                    gif.append(imageio.imread("grey_img.png"))

    imageio.mimsave('gif.gif', gif)
    quit("Error: no path was found.")

def findStartAndEnd(image):
    convertedImg = Image.open(image)
    (width,height) = convertedImg.size
    startX = 0
    startY = 0
    startTotalPX = 0
    endX = 0
    endY = 0
    endTotalPX = 0
    for x in range(width):
        for y in range(height):
            color = convertedImg.getpixel((x,y))
            if color == (0,255,0):
                startX += x
                startY += y
                startTotalPX += 1
                convertedImg.putpixel((x, y), (255,255,255))
            if color == (255,0,0):
                endX += x
                endY += y
                endTotalPX += 1
                convertedImg.putpixel((x, y), (255,255,255))
            
    start = (int((startX / startTotalPX)),int((startY / startTotalPX)))
    end = (int((endX / endTotalPX)),int((endY / endTotalPX)))
    return start,end

def convertImg(image):
    # Opens the original image and prints its size
    originalImg = Image.open(image)
    # Gets width and height of the originalImg for printing & resizing purposes
    (width,height) = originalImg.size
    print("Image size: " + str(width) + " x " + str(height))

    # Creates a resized image of the original if its taken from phone
    if (width,height) == (1920, 1080):
        resizedImg = originalImg.resize((480, 270), Image.ANTIALIAS)
    # Sets resizedImg variable to the original image
    else:
        resizedImg = originalImg

    # Saves and opens resizedImg for writing to
    resizedImg.save("resizedImg.png")
    resizedImg = Image.open("resizedImg.png")
    # sets width and height to the resizedImg
    (width,height) = resizedImg.size
    print("Downscaled image size: " + str(width) + " x " + str(height))

    # Creates the converted image to place the new pixels in
    convertedImg = Image.new('RGB', (width, height))
    
    for x in range(width):
        for y in range(height):
            color = resizedImg.getpixel((x,y))
            # Puts a black border around the image
            if (x == 0 or y == 0 or x == width - 1 or y == height - 1):
                convertedImg.putpixel((x, y), (0,0,0))
                continue
            # Checks for green color range and converts to solid green
            if (color[0] >= 0 and color[0] <= 50) and (color[1] >= 90) and (color[2] >= 0 and color[2] <= 120):
                convertedImg.putpixel((x, y), (0,255,0))
                continue
            # Checks for red color range and converts to solid red
            if (color[0] >= 95) and (color[1] >= 0 and color[1] <= 50) and (color[2] >= 0 and color[2] <= 60):
                convertedImg.putpixel((x, y), (255,0,0))
                continue
            # converts eny color whose RGB value is less than 225 to white
            if (color[0] >= 90) or (color[1] >= 170) or (color[2] >= 170):
                convertedImg.putpixel((x, y), (255,255,255)) 
                continue
            # converts any color whose RGB value is higher than 225 to black
            if any(z < 225 for z in color):
                convertedImg.putpixel((x, y), (0,0,0))
                continue

    convertedImg.save("convertedImg.png")

#########################################################################
#########################################################################
if __name__ == '__main__':
    pwm = PCA9685()
    PWM_FREQ = 50
    pwm.setPWMFreq(PWM_FREQ)
    yaw = 90
    pitch = 90    
    
    pwm.setRotationAngle(0, yaw)
    pwm.setRotationAngle(1, pitch)
    
    time.sleep(.2)
    #pwm.exit_PCA9685()
    #GPIO.cleanup()


    camera = PiCamera()
    camera.resolution = (1920,1080)
    camera.rotation = 180
    camera.start_preview()
    sleep(2)
    camera.capture("/home/pi/Desktop/Python Project/photo.png")
    camera.stop_preview()
    
    # Converts all colors to be either black, white, red, or green
    convertImg("photo.png")

    # locates the center of the green and red dots
    start,end  = findStartAndEnd("convertedImg.png")
    distanceX = start[0]
    distanceY = start[1]
    
    
    # Starts timer
    timerStart = time.process_time()

    # Opens and loads the image
    base_img = Image.open("convertedImg.png")
    base_pixels = base_img.load()

    # Runs the Breadth-First Search (BFS) algorithm
    print("Start Coordinate: " + str(start))
    print("End Coordinate: " + str(end), end="\n\n")
    path = BFS(start, end, base_pixels)

    # Saves a greyed out version for trouble-shooting purposes
    base_img.save("grey_img.png")

    # Opens the original image agian to print the fastest path
    path_img = Image.open("convertedImg.png")
    path_pixels = path_img.load()

    # Prints the fastest path in blue
    for position in path:
        x,y = position
        path_pixels[x,y] = (0,0,255)
        

    ##############################################################
    # This needed to be cleaned up but we ran out of time... Sorry :(
    ##############################################################
    LaserGPIO = 26 # --> PIN11/GPIO17


    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LaserGPIO, GPIO.OUT)
    GPIO.output(LaserGPIO, GPIO.HIGH)   
    
    GPIO.output(LaserGPIO, GPIO.HIGH) # led on
    
    
    laserPos = [254,148]
    moveList = []
    moveList.append([distanceX,distanceY])
    start = True
    for position in path:
        x,y = position
        if start == True:
            start = False
            prev = [x,y]
            prevslope = 0 
            xMove = (distanceX - laserPos[0])/ 6.35
            yMove = (distanceY - laserPos[1])/ 6.26
            pwm.setRotationAngle(0, (90 - yMove))
            pwm.setRotationAngle(1, (90 - xMove))
            time.sleep(.2)

        else:
            current = [x,y] 
            yslope = current[1] - prev[1]
            xslope = current[0] - prev[0]
            if xslope != 0:
                slope = yslope / xslope
            else:
                slope = 0
            if slope != prevslope:
                moveList.append(current)
                prev = current
                prevslope= slope
            else:
                prev = current
                prevslope= slope
      
    print(moveList)
                
    begin = True
    for coordinate in path:
        x,y = coordinate
        if begin == True:
            begin = False
            old = [x,y]
            xAngle = 90 - xMove #98.6
            yAngle = 90 - yMove

        else:
            new = [x,y] 
            x1dist = new[0] - old[0] #105.4
            y1dist = new[1] - old[1]
            x1move = x1dist / 6.35 # 16.5
            y1move = y1dist / 6.26
            xAngle = xAngle - x1move 
            yAngle = yAngle + y1move
            pwm.setRotationAngle(0, yAngle)
            pwm.setRotationAngle(1, xAngle)
            old = new
            time.sleep(.2)
    #####################################################################
    #####################################################################



    #GPIO.output(LaserGPIO, GPIO.LOW)      
    pwm.exit_PCA9685()
    #GPIO.cleanup()        

    # Saves the solved image
    path_img.save("solved_img.png")

    # Prints timer
    timerEnd = time.process_time()
    time = timerEnd - timerStart
    print("Time taken to solve maze: " + str(round(time, 2)))


    
#########################################################################
#########################################################################
