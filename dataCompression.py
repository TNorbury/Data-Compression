import datetime
import math
import random

def main():
   oldData = 0
   oldDataTime = datetime.datetime.now()
   numChunks = 0
   compressionThreshold = 32767 

   # Open the file to write data to
   dataFile = open("data", "w")
   
   # Indefintely read data in (from SPI, or just a num generator)
   while (True):
      # Generate a random value (this will be SPI in the real deal)
      data = random.randint(0x0, 0xFFFF)
      dataTime = datetime.datetime.now()

      # If the difference between the new data and the last data read 
      # (or the average of chunks read) is greater than the amount we set for 
      # compression, then we want to write it to the file
      if (math.fabs(data - oldData) > compressionThreshold):
         # Don't write to the file if this is the first data being read
         if (numChunks != 0):
            dataLog = str(numChunks) + " " + str(oldData) + " " + str(oldDataTime.strftime("%I:%M:%S.%f"))         
            dataFile.write(dataLog + "\n")

         # We're starting on a new chunk of data, with the current data serving as the starting point
         numChunks = 1
         oldData = data
         oldDataTime = dataTime

      # Otherwise, if the difference is too small, or there isn't any old data,
      # then average old data with data
      elif (math.fabs(data - oldData) <= compressionThreshold):
         # Adjust the average size of the chunk
         oldData = (oldData * numChunks) + data
         numChunks += 1
         oldData = oldData // numChunks

if __name__ == "__main__":
   main()

