import argparse
import datetime
import math
import random
import signal
import sys

# We're also using spidev, but it's not imported until later.
# Documentation on that package can be found at github.com/doceme/py-spidev
# Some good examples of how to use it can be found in this code and also at http://www.takaitra.com/posts/492

# The class will handle incoming interupt and termination signals so that the
# program can exit "gracefully"
class KillHandler:
   def __init__(self):
      signal.signal(signal.SIGINT, self.handleKill)
      signal.signal(signal.SIGTERM, self.handleKill)
      self.killed = False

   def handleKill(self, signum, frame):
      # Tell the program that it has been killed, so that it can exit 
      # gracefully when it gets a chance
      self.killed = True

   def isKilled(self):
      return self.killed


def main():
   # Initialize the signal handler 
   killHandler = KillHandler()

   # Create the argument parser
   parser = argparse.ArgumentParser(description="Read values off of the SPI and compress the data")

   # The following parameters alter how much data gets compressed
   # Add arguments to the parser
   # Minimum ADC value is 0
   minADCValue = 0
   parser.add_argument("--lowerBound", dest="lowerBound", nargs='?', 
      metavar="lowerBound", default=minADCValue, type=int, 
      help="Set the lower bound of the signal. When using random values, this will be the min random value. Default="+str(minADCValue))

   # Max 10 bit ADC value is 1024
   maxADCValue = 1024
   parser.add_argument("--upperBound", dest="upperBound", nargs='?',
      metavar="upperBound", default=maxADCValue, type=int, 
      help="Set the upper bound of the signal. When using random values, this will be the max random value. Default="+str(maxADCValue))

   # The default threshold range (aka bound offset) of values that make up the 
   # upper/lower thresholds. The value 20 is arbitrary
   defaultThresholdRange = 20
   parser.add_argument("--boundOffset", dest="boundOffset", nargs='?',
      metavar="boundOffset", default=defaultThresholdRange, type=int,
      help="The offset from the upper/lower bound that defines the range of values that will have their values altered to the upper/lower range, respectively. Default="+str(defaultThresholdRange))

   # The default size (i.e. number of values) of ramps entering/exiting the 
   # thresholds that won't be changed to the upper/lower bound. 
   # The value of 5 is arbitrary.
   defaultRampSize = 5
   parser.add_argument("--rampPct", dest="rampPct", nargs='?', metavar="rampPct",
      default=defaultRampSize, type=int, 
      help="Set the size of the ramp, which will control how many of the values in a threshold are preservered when entering/exiting the threshold. Default="+str(defaultRampSize))

   # This is the default number of values that will be compressed at once.
   # The value of 5000 is arbitrary
   defaultCompressionSize = 5000
   parser.add_argument("--maxRepeats", dest="maxRepeats", nargs='?', metavar="maxRepeats",
      default=5000, type=int,
      help="Control how many equal values in a row are compressed together at once. Default=5000")
   
   # This argument allows random values to be used instead of SPI
   parser.add_argument("--randValues", dest="randValues", action="store_true", 
      help="Use random values, insteads of reading off the SPI")

   # The following two arguments determine where data will be written to, 
   # and whether or not a debug file is used
   parser.add_argument("--debugOutput", dest="debugOutput", nargs='?',
      metavar="debugOutput", type=argparse.FileType('w'), 
      help="Output files that contains the  original values of all data collected. Default='debugOutput'")
   parser.add_argument("--outputFile", dest="outputFile", nargs='?',
      metavar="outputFile", default="data", type=argparse.FileType('w'),
      help="File where collected data will be written to. Default='data'")

   args = parser.parse_args()

   lowerBound = args.lowerBound
   upperBound = args.upperBound
   boundOffset = args.boundOffset

   # Open the file to write data to
   dataFile = args.outputFile

   # Open a file to write debug values to
   debugFile = args.debugOutput

   useRand = args.randValues
   
   oldData = 0
   oldDataTime = datetime.datetime.now()

   # The signal needs to be within the upper/lower bound for a certain number
   # of iterations before changing values
   inBoundIterations = 0
   rampPct = float(args.rampPct) / 100
   rampSize = 0

   # If the data is in the threshold then buffer it
   thresholdBuffer = list()
   inThreshold = False
   rampStart = 0 # How many values into the buffer the ramp starts
   bufferValuesRead = 0 # How many values have been read from the buffer

   # Control how many equal values in a row are compressed together
   repeatingValues = 0
   maxRepeatingValues = args.maxRepeats

   processData = True

   # These represent the indicies used to indicate the high and low byte of the
   # data that is sent over SPI
   lowByte = 0
   highByte = 1
   spiData = [0, 0]

   # If the SPI argument was given, or no argument at all, then get data off of the SPI.
   if (not useRand):
      import spidev
      useRand = False
      spi = spidev.SpiDev()
      spi.open(0,0)

      # The following is a list of values accepted for the max_speed_hz parameter
      # Credit goes to http://www.takaitra.com/posts/492 for defining these values
      # 125.0 MHz       125000000
      # 62.5 MHz        62500000
      # 31.2 MHz        31200000
      # 15.6 MHz        15600000
      # 7.8 MHz         7800000
      # 3.9 MHz         3900000
      # 1953 kHz        1953000 <-- Works best
      # 976 kHz         976000
      # 488 kHz         488000
      # 244 kHz         244000
      # 122 kHz         122000
      # 61 kHz          61000
      # 30.5 kHz        30500
      # 15.2 kHz        15200
      # 7629 Hz         7629
      spi.max_speed_hz = 1953000
   elif (useRand):
      useRand = True

   # Run until the program receives a signal to stop 
   while (not killHandler.isKilled()):
      # If outside of the threshold, and there are still values left in the threshold
      # then get data from the buffer, and not the normal way
      if (not inThreshold and len(thresholdBuffer) != 0):
         bufferValuesRead += 1
         bufferData = thresholdBuffer.pop()
         data = bufferData[0]
         dataTime = bufferData[1]
      else:
         if (useRand == True):
            # Get random values
            data = random.randint(lowerBound, upperBound + 1)

         else:
            # Read a byte from SPI and multiply it by 4 to get the full value
            # The use of 0 here is arbitrary 
            spiData[highByte] = spi.xfer([0x0])[0]
            spiData[lowByte] = spi.xfer([0x0])[0]


            # Take the two separate bytes and combine it into one value
            data = (spiData[highByte] << 8) | spiData[lowByte]

            # If the data is equal to 0, that means that the slave doesn't have
            # any data to send over. So we'll ignore this data and sleep for a
            # little bit
            if (data == 0):
               processData = False
               time.sleep(1)
            else:
               processData = True

         dataTime = datetime.datetime.now()
      
      # If the data is good (i.e. not 0), then we'll process it
      if (processData):
         # If currently within the threshold, add the data to the buffer
         if (inThreshold):
            # Add data to the buffer
            thresholdBuffer.append([data, dataTime])

            # Check to make sure that the data is still within the threshold
            # If not, then we want to start clearing the buffer.
            if (not (data >= (lowerBound - boundOffset) and data <= (lowerBound + boundOffset)) 
               and not (data >= (upperBound - boundOffset) and data <= (upperBound + boundOffset))):
               inThreshold = False

               # Calculate the size of the ramp based on the size of the buffer and the % of the buffer we want to preserve
               rampSize = (len(thresholdBuffer) * rampPct) // 1

               # Since the buffer is complete, we want to know when we should 
               # stop altering the data (in order to preserve the ramp of signals
               rampStart = len(thresholdBuffer) - rampSize

               # We also need to indicate that we haven't read any values off the buffer
               bufferValuesRead = 0

               # If the ramp start is less then 0, then set it to 0
               if (rampStart < 0):
                  rampStart = 0

         # Otherwise, process the data
         else:
            # If a debug file is being used write the data and time to it
            if (not debugFile is None):
               debugFile.write(str(data) + " " + dataTime.strftime("%I:%M:%S.%f") + "\n")

            # If the data is between either the upper or lower range, then we want 
            # to set data to the respective value in order to eliminate minor 
            # deviations when the signal is either high or low. 
            if (data >= (lowerBound - boundOffset) and data <= (lowerBound + boundOffset)):
               # If there isn't any data in the buffer, then that means this 
               # value is straight off of the SPI
               if (len(thresholdBuffer) == 0):
                  inThreshold = True
               else:
                  inBoundIterations += 1

               # If the data isn't in the beginning or ending ramp, then change the value
               if (inBoundIterations >= rampSize and bufferValuesRead <= rampStart):
                  data = lowerBound

            elif (data >= (upperBound - boundOffset) and data <= (upperBound + boundOffset)):
               # If there isn't any data in the buffer, then that means this 
               # value is straight off of the SPI
               if (len(thresholdBuffer) == 0):
                  inThreshold = True
               else:
                  inBoundIterations += 1

               # If the data isn't in the beginning or ending ramp, then change the value
               if (inBoundIterations >= rampSize and bufferValuesRead <= rampStart):
                  data = upperBound

            else:
               inThreshold = False
               inBoundIterations = 0

            # If the current data is equal the previously acquired data, and 
            # the max number of repeating values hasn't been reach then we 
            # want to increase the counter of repeating values
            if (data == oldData and repeatingValues < maxRepeatingValues):
               repeatingValues += 1

            # Otherwise, if the current data is equal to the last data, then we want
            # to write the previous data to the file and set the previous data to 
            # our current data
            # Or if there have been too many repeating values, then also write to the file
            else:
               # If there is more than one value in a row, then we want to indicate that 
               if (repeatingValues > 1):
                  # Firstly, write something that indicates that the following line contains repeating values 
                  dataFile.write("-R-\n")
                  
                  # Next, write the number of times the value repeats, the 
                  # value itself, and the time the first of the repeating values was encountered
                  dataFile.write(str(repeatingValues) + " " + str(oldData) + " " 
                  + oldDataTime.strftime("%I:%M:%S.%f") + "\n")

               # Otherwise, if this is just a value by itself, then just print that value
               elif (repeatingValues == 1):
                  dataFile.write(str(oldData) + "\n")

               # Reset the number of repeating values, and set the current data as the old data
               repeatingValues = 1
               oldData = data
               oldDataTime = dataTime


   # Since the program has been killed, write whatever data is in the buffer 
   # to the file, and then close the file.
   bufferData = thresholdBuffer.pop()
   data = bufferData[0]
   dataTime = bufferData[1]
   
   # Determine if the value is in the upper or lower bound
   if (data >= (lowerBound - boundOffset) and data <= (lowerBound + boundOffset)):
      data = lowerBound
   elif (data >= (upperBound - boundOffset) and data <= (upperBound + boundOffset)):
      data = upperBound

   
   dataFile.write("-R-\n")
   dataFile.write(str(len(thresholdBuffer) + 1) + " " + str(data) + " " + dataTime.strftime("%I:%M:%S.%f") + "\n")

   # If there is a debug file, write all the data to it
   if (not debugFile is None):
      while(len(thresholdBuffer) > 0):
         bufferData = thresholdBuffer.pop()
         data = bufferData[0]
         dataTime = bufferData[1]
         debugFile.write(str(data) + " " + dataTime.strftime("%I:%M:%S.%f") + "\n")
      debugFile.close()


   # Finally, close the file
   dataFile.close()


if __name__ == "__main__":
   main()

