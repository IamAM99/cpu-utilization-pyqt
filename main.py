"""A PyQt5 app to show the CPU utilization.
Author: Mohammad Arabzadeh
"""

import os
import sys
import psutil
import subprocess
import matplotlib
from time import sleep
from collections import deque
from PyQt5 import uic, QtCore
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

matplotlib.use("Qt5Agg")

Form = uic.loadUiType(os.path.join(os.getcwd(), "mainwindow.ui"))[0]


def get_cpu_model() -> str:
    """Get the CPU model of the current computer.

    Returns
    -------
    str
        CPU model name.
    """
    # get cpu info
    model: str = subprocess.check_output("lscpu", shell=True).decode()

    # get the model name
    model = model[model.find("Model name:") :].partition(":")[2]

    # strip spaces from the left
    model = model.partition("\n")[0].lstrip()

    return model


class CpuPercentThread(QtCore.QThread):
    """CPU utilization percentage worker thread.
    """

    cpu_percent = QtCore.pyqtSignal(float)

    def __init__(self, window):
        QtCore.QThread.__init__(self, parent=window)

    def run(self):
        """Get the CPU utilization percentage every 1 second.
        """
        while True:
            sleep(1)
            self.cpu_percent.emit(psutil.cpu_percent())


class MainWindow(QMainWindow, Form):
    """Main PyQt5 window
    """

    time_interval = 60  # seconds
    line_colors = "C0"

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("CPU Utilization")

        # initialize plot 'x' and 'y'
        self.x = list(range(self.time_interval))  # x
        self.cpu_percent = deque([0] * self.time_interval)  # y

        # initialize the plot
        self.matplotlib_init()
        self.line = self.ax.plot(self.x, self.cpu_percent, lw=0.8)[0]

        # start the matplotlib thread
        self.thread = CpuPercentThread(window=self)
        self.thread.cpu_percent.connect(self.update_plot)
        self.thread.start()

    def matplotlib_init(self):
        """Initialize matplotlib figure
        """
        # initialize a canvas
        self.fig = Figure()
        self.ax = self.fig.add_axes([0, 0.03, 0.999, 0.87])
        self.canvas = FigureCanvas(self.fig)

        # set frame color
        for spine in self.ax.spines.values():
            spine.set_edgecolor(self.line_colors)

        # set title text
        self.fig.text(0, 0.95, "CPU", ha="left", fontsize=22)
        self.fig.text(0.999, 0.95, get_cpu_model(), ha="right", fontsize=11)

        # set top text
        self.fig.text(0, 0.91, "% Utilization", ha="left", fontsize=9, color="gray")
        self.fig.text(0.999, 0.91, "100%", ha="right", fontsize=9, color="gray")

        # set bottom text
        self.fig.text(0, 0, "60 seconds", ha="left", fontsize=9, color="gray")
        self.fig.text(0.999, 0, "0", ha="right", fontsize=9, color="gray")

        # set xticks
        xticks = list(range(0, self.time_interval, 5))
        self.ax.set_xticks(xticks)
        for line in self.ax.get_xticklines():
            line.set_visible(False)
        for label in self.ax.get_xticklabels():
            label.set_visible(False)

        # set yticks
        yticks = list(range(0, 100, 10))
        self.ax.set_yticks(yticks)
        for line in self.ax.get_yticklines():
            line.set_visible(False)
        for label in self.ax.get_yticklabels():
            label.set_visible(False)

        # set grids
        self.ax.grid(color=self.line_colors, alpha=0.1)

        # set ax limits
        self.ax.set_ylim([0, 100])
        self.ax.set_xlim([0, self.time_interval - 1])

        # show figure on the window
        plt_container = QVBoxLayout(self.matplotlib_container)
        plt_container.addWidget(self.canvas)

    def update_plot(self, val: float):
        """Update the matplotlib figure.

        Parameters
        ----------
        val : float
            New value to add to the plot.
        """
        # update self.cpu_percent
        self.cpu_percent.popleft()
        self.cpu_percent.append(val)

        # update the canvas
        self.line.set_data(self.x, self.cpu_percent)
        self.ax.collections.clear()
        self.ax.fill_between(
            self.x, self.cpu_percent, color=self.line_colors, alpha=0.1
        )
        self.canvas.draw()

        # update current utilization
        self.current_utilization.setText(
            f"Current Utilization: {self.cpu_percent[-1]}%"
        )
        self.current_utilization.adjustSize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
