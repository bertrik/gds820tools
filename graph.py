import gds820_rs232

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np


# constants
UPDATE_PERIOD = 1  # this many ms between memory dumps. memory dumps are slow for right now.

s = gds820_rs232.scope("/dev/ttyUSB0", 38400)
print "Oscilloscope identity: " + s.get_identity()

# set up Qt
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Oscilloscope dump")
win.setWindowTitle('Oscilloscope dump')

# set up pyqtgraph
pg.setConfigOptions(antialias=True)

# add plot
p = win.addPlot(title="Channel 1")
p.setLabel('left', "Voltage", units='V')
p.setLabel('bottom', "Time", units='s')
p.showGrid(x=True, y=True)

sample_rate, ch1_data = s.dump_memory(1)
dt = 1./sample_rate
time_scale = np.linspace(0,len(ch1_data)*dt, len(ch1_data))
plot_data = p.plot(time_scale, ch1_data, pen=(255,255,255,128), symbol='o', symbolPen=None, symbolBrush=(255,255,255,192), symbolSize=2)

p.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted

timer = QtCore.QTimer()
timer.setSingleShot(True)

def update():
    try:
        sample_rate, ch1_data = s.dump_memory(1)
        dt = 1./sample_rate
        time_scale = np.linspace(0,len(ch1_data)*dt, len(ch1_data))
        plot_data.setData(time_scale, ch1_data)
    except Exception as e:
        print "Warning: ", e
    finally:
        timer.start(UPDATE_PERIOD)

timer.timeout.connect(update)
timer.start(UPDATE_PERIOD)

QtGui.QApplication.instance().exec_()
