import sys, matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg, 
	NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import QtWidgets as widgets
from PyQt5.QtCore import Qt
from functools import partial
from IPython import embed

mpl.use("Qt5Agg")

app = widgets.QApplication(sys.argv)

class Button:
	def __init__(self, row, col, update_fun, name):
		self.row = row
		self.col = col
		self.update_fun = update_fun
		self.name = name
		self.button = widgets.QPushButton(name)
		self.button.clicked.connect(update_fun)

class TextBox:
	def __init__(self, row, col, value, name, update_fun, parent_window):
		#self.type_check(row, col, update_fun, value, name)

		self.row = row
		self.col = col
		self.update_fun = update_fun
		self.value = value
		self.name = name
		self.parent_window = parent_window

		self.line_edit = self.add_line_edit(value, update_fun)
		self.label = self.add_label_text(name)

	def add_line_edit(self, value, update_fun):
		line_edit = widgets.QLineEdit()
		line_edit.setText( str(value) )
		if update_fun is None:
			update_fun = partial(self._default_update_fun, self.name)
			line_edit.textChanged[str].connect(update_fun)
		else:
			line_edit.textChanged[str].connect(update_fun)

		return line_edit

	def add_label_text(self, name):
		label = widgets.QLabel()
		label.setText(name)

		return label

	def _default_update_fun(self, name, text):
		self.parent_window.dock.values[name] = float(text)

	def type_check(self, row, col, update_fun, value, name):
		if type(row) is not int or row < 0:
			raise ValueError('row must be an integer greater than 0')
		if type(col) is not int or col < 0:
			raise ValueError('col must be an integer greater than 0')
		if not hasattr(update_fun, '__call__'):
			raise TypeError("update_fun must be a function")
		if not (type(value) is int or type(value) is float):
			raise TypeError("value must be an int or float")
		if type(name) is not str:
			raise TypeError("name must be a str")

class Dock(widgets.QDockWidget):
	def __init__(self, parent_window):
		#widgets.QDockWidget.__init__(self)
		super(Dock, self).__init__()
		self.controls = widgets.QWidget()
		self.setWidget( self.controls)
		self.controls_grid = widgets.QGridLayout(self.controls)

		self.buttons = []
		self.text_boxes = []
		self.values = {}

		self.parent_window = parent_window


	def add_button(self, row, col, update_fun, name):
		button = Button(row, col, update_fun, name)
		self.buttons.extend([button])
		self.controls_grid.addWidget(button.button, button.row, button.col)

	def add_textbox(self, row, col, name, value, update_fun=None):
		self.values[name] = value

		if update_fun is None:
			text_box = TextBox(row, col, value, name, update_fun, self.parent_window)
		else:
			update_fun = partial(update_fun, self.parent_window, name)
			text_box = TextBox(row, col, value, name, update_fun, self.parent_window)

		self.text_boxes.extend([text_box])
		self.controls_grid.addWidget(text_box.line_edit, text_box.row, 
			text_box.col)
		self.controls_grid.addWidget(text_box.label, text_box.row, 
			text_box.col+1)

	def add_toolbar(self, row, col, canvas):
		self.toolbar = NavigationToolbar(canvas, self)
		self.controls_grid.addWidget( self.toolbar, row, col)

class Window(widgets.QMainWindow):
	def __init__(self, rows, cols, update_fun):
		#widgets.QMainWindow.__init__(self)
		super(Window, self).__init__()

		self.figs = []
		self.axes = []
		self.fig_updaters = []
		self.fig_index = 0

		self.add_page(rows, cols, update_fun)

	def close_event(self, event):
		plt.close('all')
		event.accept()

	def add_page(self, rows, cols, fig_updater):
		fig, ax  = plt.subplots(rows, cols)
		canvas  = FigureCanvasQTAgg(fig)

		self.figs.extend([fig])
		self.axes.extend([ax])
		self.fig_updaters.extend([fig_updater])

		if len(self.figs) == 1:
			self.canvas = canvas
			self.setCentralWidget(self.canvas)

	def add_dock(self):
		self.dock = Dock(self)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.dock)

		self.dock.add_button(0, 0, self.prev_page, 'Previous Page')
		self.dock.add_button(0, 1, self.next_page, 'Next Page')
		self.dock.add_button(0, 2, self._update_figs, 'Update Figures')
		self.dock.add_toolbar(0, 3, self.canvas)

		return self.dock

	def next_page(self):
		self.dock.toolbar.home()
		self.fig_index = (self.fig_index + 1) % len(self.figs) 
		self.canvas = FigureCanvasQTAgg(self.figs[self.fig_index])
		self.dock.add_toolbar(0, 3, self.canvas)
		self.setCentralWidget(self.canvas)

	def prev_page(self):
		self.dock.toolbar.home()
		self.fig_index = (self.fig_index - 1) % len(self.figs) 
		self.canvas = FigureCanvasQTAgg(self.figs[self.fig_index])
		self.dock.add_toolbar(0, 3, self.canvas)
		self.setCentralWidget(self.canvas)

	def _update_figs(self):
		([fig_update(ax, self.dock.values) 
			for fig_update, ax in zip(self.fig_updaters, self.axes)])

		[fig.canvas.draw() for fig in self.figs]

	def show(self):
		self._update_figs()
		super(Window, self).show()
		sys.exit(app.exec_())