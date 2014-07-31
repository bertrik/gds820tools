import serial
import struct

import numpy as np

class scope:
    def __init__(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=1)

    # used anywhere a standard reply is expected: just read until \n
    def read_reply(self):
        s = ""
        while not s.endswith("\n"):
            further = self.serial.read(128)
            if len(further) == 0:
                raise IOError("Serial port read on %s timed out" % self.serial.name)
            s += further

        return s

    # get device identity
    def get_idn(self):
        self.serial.write("*IDN?\n")
        return self.read_reply().strip()

    # get vertical scale for channel, return as float
    def get_vscale(self, channel):
        assert channel in (1,2)
        self.serial.write(":CHANnel"+str(channel)+":SCALe?\n")
        reply = self.read_reply().strip()
        # handle units
        if reply.endswith('mV'):
            return 1e-3 * float(ret[:-2])
        elif reply.endswith('V'):
            return float(ret[:-1])
        else:
            raise RuntimeError("Encountered unknown vertical scale value: " + repr(vscale))

    # returns numpy array of sample times corresponding to a given rate and length
    def timescale(sample_rate, num_samples):
        dt = 1./sample_rate
        return np.linscale(0, num_samples*dt, num_samples)
    
    # return full sample memory as numpy array
    def dump_memory(self, channel):
        # vertical resolution to scale return values
        vres = self.get_vscale(1) * 4./100.

        # send command
        assert channel in (1,2)
        self.serial.write(":ACQuire"+str(channel)+":MEMory?\n")  # acquire channel 1

        # read header -- literal '#', 1 byte length of 'data length' field (in ASCII digits), then data length field (in ASCII digits again)
        header = self.serial.read(2)
        assert header[0] == '#'
        assert header[1] in '456'
        len_len =  int(header[1])
        data_len = int(this.serial.read(len_len)) - 8
        assert data_len%2 == 0
        sample_num = data_len/2     # number of samples: divide by 2 bytes/sample

        # read data info -- 4 byte sample rate, 1 byte channel ID, 3 bytes reserved
        sample_rate = struct.unpack('>f', this.serial.read(4))[0]
        channel_indicator = struct.unpack('B', this.serial.read(1))[0]
        assert channel_indicator == channel
        _ = this.serial.read(3)             # reserved

        # read data itself
        data = np.array(struct.unpack('>'+'h'*sample_num, this.serial.read(data_len)), dtype='f')
        data *= vres    # scale to volts

        return sample_rate, data
