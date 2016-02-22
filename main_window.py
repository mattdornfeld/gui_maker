import sys
sys.dont_write_bytecode = True
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg, 
	NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import QtWidgets as widgets
from PyQt5.QtCore import Qt
import gui_maker as gui

plt.style.use('ggplot')

def fig0_update(ax, values):
	[a.cla() for a in ax]
	
	T = values['T']
	fs = values['fs']
	x = np.arange(0, T, 1./fs)
	ax[0].plot(x, np.sin(x))
	ax[1].plot(x, np.tan(x))

window = gui.Window(1, 3, fig0_update)
dock = window.add_dock()
#window.add_page(2, 3, update_functions.execute)
dock.add_textbox(1, 0, 'T', 10)
dock.add_textbox(2, 0, 'fs', 10)
window.show()