import sys
import time
from queue import Queue
from PIL import Image

# -m pip install imageio --user
import imageio

class Main:

    def __init__(self, image):
        self.image = image


    @property
    def setConvertedImage(self):
        return self.convertedImage

    @setConvertedImage.setter
    def setConvertedImage(self, convertedImage):
        self.convertedImage = convertedImage

    @property
    def setStartAndEnd(self):
        return self.start,self.end

    @setStartAndEnd.setter
    def setStartAndEnd(self, start, end):
        self.start = start
        self.end = end

    @property
    def setPath(self):
        return self.path

    @setPath.setter
    def setPath(self, path):
        self.path = path
    
    def iswhite(self, value):
        if value == (255,255,255) or value == (0,255,0) or value == (255,0,0): 
            return True

    def getadjacent(self, n):
        x,y = n
        return [(x-1,y),(x,y-1),(x+1,y),(x,y+1),
                (x-1,y-1),(x+1,y-1),(x+1,y+1),(x-1,y+1)]

    def BFS(self):

        base_img = Image.open(self.convertedImage)
        pixels = base_img.load()

        # Used for the gif creation
        count = 0
        gif = []

        queue = Queue()
        queue.put([self.start]) # Wrapping the start tuple in a list

        while not queue.empty():

            path = queue.get() 
            pixel = path[-1]

            if pixel == self.end:
                imageio.mimsave('gif.gif', gif)
                base_img.save("grey_img.png")

                self.setPath(path)

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

    def findStartAndEnd(self):
        convertedImg = Image.open(self.convertedImage)
        (width,height) = self.convertedImg.size
        startX = 0
        startY = 0
        startTotalPX = 0
        endX = 0
        endY = 0
        endTotalPX = 0
        for x in range(width):
            for y in range(height):
                color = self.convertedImg.getpixel((x,y))
                if color == (0,255,0):
                    startX += x
                    startY += y
                    startTotalPX += 1
                    self.convertedImg.putpixel((x, y), (255,255,255))
                if color == (255,0,0):
                    endX += x
                    endY += y
                    endTotalPX += 1
                    self.convertedImg.putpixel((x, y), (255,255,255))
                
        start = (int((startX / startTotalPX)),int((startY / startTotalPX)))
        end = (int((endX / endTotalPX)),int((endY / endTotalPX)))
        
        self.setStartAndEnd(start, end)

        print("Start Coordinate: " + str(start))
        print("End Coordinate: " + str(end), end="\n\n")

    def convertImg(self):
        # Opens the original image and prints its size
        originalImg = Image.open(self.image)
        # Gets width and height of the originalImg for printing & resizing purposes
        (width,height) = originalImg.size
        print("Image size: " + str(width) + " x " + str(height))

        # Creates a resized image of the original if its taken from phone
        if (width,height) == (4032,1960):
            resizedImg = originalImg.resize((504, 245), Image.ANTIALIAS)
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
                if (color[0] >= 0 and color[0] <= 200) and (color[1] >= 200) and (color[2] >= 0 and color[2] <= 120):
                    convertedImg.putpixel((x, y), (0,255,0))
                    continue
                # Checks for red color range and converts to solid red
                if (color[0] >= 200) and (color[1] >= 0 and color[1] <= 200) and (color[2] >= 0 and color[2] <= 120):
                    convertedImg.putpixel((x, y), (255,0,0))
                    continue
                # converts eny color whose RGB value is less than 225 to white
                if (color[0] >= 170) or (color[1] >= 170) or (color[2] >= 170):
                    convertedImg.putpixel((x, y), (255,255,255)) 
                    continue
                # converts any color whose RGB value is higher than 225 to black
                if any(z < 225 for z in color):
                    convertedImg.putpixel((x, y), (0,0,0))
                    continue

        convertedImg.save("convertedImg.png")

        self.setConvertedImage("convertedImg.png")

    def solve(self, path):
        path_img = Image.open("convertedImg.png")
        path_pixels = path_img.load()
        for position in self.path:
            x,y = position
            path_pixels[x,y] = (0,0,255)
        
        path_img.save("solved_img.png")


if __name__ == '__main__':

    run1 = Main("Pictures/img.png")
    run1.convertImg()
    run1.findStartAndEnd()

    timerStart = time.process_time()

    base_img = Image.open("convertedImg.png")
    base_pixels = base_img.load()
    run1.BFS()
    run1.solve()

    # Prints timer
    timerEnd = time.process_time()
    time = timerEnd - timerStart
    print("Time taken to solve maze: " + str(round(time, 2)))

