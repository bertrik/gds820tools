import sys
import gds820_rs232
import numpy as np
import csv

s = gds820_rs232.scope("/dev/ttyUSB0", 38400)
print "Oscilloscope identity: " + scope.get_identity()

sample_rate, ch1 = s.acquire(1)
sample_rate, ch2 = s.acquire(2)

print "Received %d samples" % len(ch1)
print "Sample rate: %f Hz"  % sample_rate

outfile = 'scope.csv'
t = scope.timescale(sample_rate, len(ch1))
with open(outfile, 'w') as f:
    w = csv.writer(f)
    w.writerows(zip(t, ch1, ch2))
