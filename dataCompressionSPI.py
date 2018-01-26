import datetime
import math
import random
import spidev
import sys

def main():
   oldData = 0
   oldDataTime = datetime.datetime.now()
   repeatingValues = 0

   lowerBound = 0
   upperBound = 1024
   boundOffset = 20

   # The signal needs to be within the upper/lower bound for a certain number
   # of iterations before changing values
   inBoundIterations = 0
   MAX_ITERATIONS = 5

   # Open the file to write data to
   dataFile = open("data", "w")

   useRand = False;
   processData = True
   
   # If the SPI argument was given, or no argument at all, then get data off of the SPI.
   if (len(sys.argv) == 1 || sys.argv[1] == "SPI"):
      useRand = False
      spi = spidev.SpiDev()
      spi.open(0,0)
   elif (len(sys.argv) == 2 && sys.argv[2] == "rand"):
      useRand = True

   # Indefinetely read data from SPI
   while (True):
      if (useRand == True):
         # Get random values
         data = random.randint(lowerBound, upperBound + 1)

      else:
         # Read a byte from SPI and multiply it by 4 to get the full value
         spiData = spi.xfer([0xFF])

         # If the "ignore" value was sent. If it was, then don't process the data.
         if (spiData[0] == 0xFF):
            processData = False
         else:
            processData = True
            data = spiData[0] * 4

      if (processData == True):
         dataTime = datetime.datetime.now()

         # If the data is between either the upper or lower range, then we want 
         # to set data to the respective value in order to eliminate minor 
         # deviations when the signal is either high or low. 
         if (data >= (lowerBound - boundOffset) and data <= (lowerBound + boundOffset)):
            inBoundIterations += 1
            if (inBoundIterations == MAX_ITERATIONS):
               data = lowerBound

         elif (data >= (upperBound - boundOffset) and data <= (upperBound + boundOffset)):
            inBoundIterations += 1
            if (inBoundIterations == MAX_ITERATIONS):
               data = upperBound

         else:
            inBoundIterations = 0

         # If the current data is equal the previously acquired data, then we want
         # to increase the counter of repeating values
         if (data == oldData):
            repeatingValues += 1

         # Otherwise, if the current data is equal to the last data, then we want
         # to write the previous data to the file and set the previous data to 
         # our current data
         elif (data != oldData):
            # If this is the first data that's been read, then don't write 
            # anything to the file
            if (repeatingValues != 0):
               dataFile.write(str(repeatingValues) + " " + str(oldData) + " " 
               + oldDataTime.strftime("%I:%M:%S.%f") + "\n")

            # Reset the number of repeating values, and set the current data as the old data
            repeatingValues = 1
            oldData = data
            oldDataTime = dataTime


if __name__ == "__main__":
   main()

