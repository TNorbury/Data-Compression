# Data-Compression
A set of programs that compress incoming data & writes the compressed data to a file, and another that takes the compressed file and decompresses it into a .csv format
  
---  
  
## Usage  
python dataCompression.py [-h] [--lowerBound [lowerBound]]  
                          [--upperBound [upperBound]]  
                          [--boundOffset [boundOffset]]  
                          [--rampSize [rampSize]] [--maxRepeats [maxRepeats]]  
                          [--randValues] [--debugOutput [debugOutput]]  
                          [--outputFile [outputFile]]  
  
optional arguments:  
  -h, --help  
> show the help message and exit  
  
  --lowerBound [lowerBound]  
> Set the lower bound of the signal. When using random values, this will be the min random value. Default=0  
  
  --upperBound [upperBound]  
> Set the upper bound of the signal. When using random values, this will be the max random value. Default=1024  
  
  --boundOffset [boundOffset]  
> The offset from the upper/lower bound that defines the range of values that will have their values altered to the upper/lower range, respectively. Default=20  
  
  --rampSize [rampSize]  
> Set the size of the ramp, which will control how many of the values in a threshold are preservered when entering/exiting the threshold. Default=5  
  
  --maxRepeats [maxRepeats]  
> Control how many equal values in a row are compressed together at once. Default=5000  
  
  --randValues  
> Use random values, insteads of reading off the SPI  
  
  --debugOutput [debugOutput]  
> Output files that contains the original values of all data collected. Default='debugOutput'  
  
  --outputFile [outputFile]  
> File where collected data will be written to. Default='data'  
  
---  
  
## Compressed Data Format
The data that is written to the compressed file is in the following format:  
> r d t (where r & t are only used when there are repeating values)
>
> Where:  
> r = # of following data points that have the following value subsequently  
> d = value of the data point  
> t = the time (formatted as hour:minute:second.fractionOfSecond) that the first data point in the "collection" of equal values was read
> 
> A line of repeating values will always be preceded by "-R-"
  
For example, the following lines in the compressed data:
> 48  
> 50  
> -R-  
> 3 249 1:56:10.0020  
> 40  
  
Would represent the following stream of data:  
> 48 50 249 249 249 40  
  
---  
  
