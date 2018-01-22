import sys

def main():
    # The first argument will be the name of the (compressed) data file, while
    # second will be the output file
    compressedFilePath = sys.argv[1]
    decompressedFilePath = sys.argv[2]

    compressedFile = open(compressedFilePath, "r")
    decompressedFile = open(decompressedFilePath, "w")

    # Iterate over each line in the file
    for line in compressedFile:
        # Split the line into three parts: number of repeating values, the data,
        # and the time the data was read
        lineSplit = line.split()

        # If the line didn't have 3 sections, then don't write anything
        if (len(lineSplit) == 3):
            repeatingValues = int(lineSplit[0])
            data = lineSplit[1]
            dataTime = lineSplit[2]

            # Now for each of the repeating values, write the data, along with the
            # timestamp, to the file
            for i in range(0, repeatingValues):
                decompressedFile.write(data + "," + dataTime + "\n")

    compressedFile.close()
    decompressedFile.close()


if __name__ == "__main__":
    main()
