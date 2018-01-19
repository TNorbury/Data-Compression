import datetime
import math
import random
import spidev

def main():
   spi = spidev.SpiDev()
   spi.open(0,0)

   oldData = 0
   oldDataTime = datetime.datetime.now()
   repeatingValues = 0

   lowerBound = 0
   upperBound = 1024
   boundOffset = 20

   # Open the file to write data to
   dataFile = open("data", "w")
   
   # Indefinetely read data from SPI
   while (True):
      # Read two bytes off of SPI and them coerce
      spiData = spi.xfer([0xFF])
      data = spiData[0] * 4
      dataTime = datetime.datetime.now()

      # If the data is between either the upper or lower range, then we want 
      # to set data to the respective value in order to eliminate minor 
      # deviations when the signal is either high or low. 
      if (data >= (lowerBound - boundOffset) and data <= (lowerBound + boundOffset)):
         data = lowerBound
      elif (data >= (upperBound - boundOffset) and data <= (upperBound + boundOffset)):
         data = upperBound

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

