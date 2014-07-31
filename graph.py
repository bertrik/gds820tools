import gds820_rs232

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np


# constants
UPDATE_PERIOD = 2000  # this many ms between memory dumps. memory dumps are slow for right now.

s = gds820_rs232.scope("/dev/ttyUSB0", 38400)
print "Oscilloscope identity: " + scope.get_identity()

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

sample_rate, ch1_data = acquire(1)
dt = 1./sample_rate
time_scale = np.linspace(0,len(ch1)*dt, len(ch1))
plot_data = p.plot(time_scale, ch1_data, pen=(255,255,255,128), symbol='o', symbolPen=None, symbolBrush=(255,255,255,192), symbolSize=2)

p.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted

def update():
    sample_rate, ch1_data = acquire(1)
    dt = 1./sample_rate
    time_scale = np.linspace(0,len(ch1_data)*dt, len(ch1_data))
    pd.setData(time_scale, ch1_data)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(UPDATE_RATE)

QtGui.QApplication.instance().exec_()
