import sys

def main():
   # The first argument will be the name of the (compressed) data file, while
   # second will be the output file
   compressedFilePath = sys.argv[1]
   decompressedFilePath = sys.argv[2]

   compressedFile = open(compressedFilePath, "r")
   decompressedFile = open(decompressedFilePath, "w")

   repeatingValues = False

   # Iterate over each line in the file
   for line in compressedFile:
      line = line.replace("\n", "")

      # If the line is "-" that means that the next line in the file is 
      # repeating values
      if (line == "-"):
         repeatingValues = True
      
      # Otherwise, if the line doesn't contain repeating values, then just 
      # print the value
      elif (not repeatingValues):
         decompressedFile.write(line + "\n")

      # Otherwise, if the line does contain repeating values, then we want to
      # print out the value the number of times it repeats
      elif (repeatingValues):


         # Split the line into three parts: number of repeating values, the data,
         # and the time the data was read
         lineSplit = line.split()

         # If the line didn't have 3 sections, then don't write anything
         if (len(lineSplit) == 3):
            numValues = int(lineSplit[0])
            data = lineSplit[1]
            dataTime = lineSplit[2]

         # Write the first value with a time stamp
         decompressedFile.write(data + "," + dataTime + "\n")

         # Now, for the remaining repeated values, just write the value by itself
         for i in range(1, numValues):
            decompressedFile.write(data + "\n")

         repeatingValues = False

   compressedFile.close()
   decompressedFile.close()


if __name__ == "__main__":
    main()
