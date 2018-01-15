import datetime
import math
import random

def main():
   oldData = 0
   oldDataTime = datetime.datetime.now()
   repeatingValues = 0

   # Open the file to write data to
   dataFile = open("data", "w")
   
   # Indefintely read data in (from SPI, or just a num generator)
   while (True):
      # Generate a random value (this will be SPI in the real deal)
      data = round(random.uniform(-0.5, 5.5), 1)
      dataTime = datetime.datetime.now()

      # If the data is between either the upper or lower range, then we want 
      # to set data to the respective value in order to eliminate minor 
      # deviations when the signal is either high or low. 
      if (data >= -0.1 and data <= 0.1):
         data = 0
      elif (data >= 4.9 and data <= 5.1):
         data = 5

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

