from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')


class Plotter:

    def __init__(self, canvas):
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.canvas = canvas.TKCanvas

    def draw_figure(self, canvas, figure):
        tkcanvas = FigureCanvasTkAgg(figure, canvas)
        tkcanvas.draw()
        tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        return tkcanvas

    def first_draw(self):
        self.axis = self.fig.add_subplot(111)
        self.line = self.axis.plot([], [])[0]
        self.tkcanvas = self.draw_figure(self.canvas, self.fig)
        self.axis.set_xlabel('Frequency [MHz]')
        self.axis.set_ylabel(r'$S_{12}$ [dBm]')

    def update_data(self, xs, ys ):

        self.line.set_data( xs, ys ) # update data

        # print("Plotting {} data".format(i_max-i_min))

        self.axis.relim()  # scale the y scale
        self.axis.autoscale_view()  # scale the y scale
        self.tkcanvas.draw()