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
    # get cpu info
    model = subprocess.check_output("lscpu", shell=True).decode()

    # get the model name
    model = model[model.find("Model name:") :].partition(":")[2]

    # strip spaces from the left
    model = model.partition("\n")[0].lstrip()

    return model


class CpuPercentThread(QtCore.QThread):
    cpu_percent = QtCore.pyqtSignal(float)

    def __init__(self, window):
        QtCore.QThread.__init__(self, parent=window)

    def run(self):
        while True:
            sleep(1)
            self.cpu_percent.emit(psutil.cpu_percent())


class MainWindow(QMainWindow, Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # cpu model name
        self.cpu_model_name.setText(get_cpu_model())
        self.cpu_model_name.adjustSize()

        # initialize the plot
        self.matplotlib_init()
        self.cpu_percent = deque([0] * 10)
        self.line = self.ax.plot(list(range(10)), self.cpu_percent, lw=2)[0]
        self.ax.set_xlim([0, 9])

        # start the matplotlib thread
        self.thread = CpuPercentThread(window=self)
        self.thread.cpu_percent.connect(self.update_plot)
        self.thread.start()

    def matplotlib_init(self):
        # initialize a canvas
        self.fig = Figure()
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvas(self.fig)

        # show figure on the window
        plt_container = QVBoxLayout(self.matplotlib_container)
        plt_container.addWidget(self.canvas)

    def update_plot(self, val):
        # update self.cpu_percent
        self.cpu_percent.popleft()
        self.cpu_percent.append(val)

        # update the canvas
        self.line.set_data(list(range(10)), self.cpu_percent)
        self.ax.set_ylim([min(self.cpu_percent), max(self.cpu_percent)])
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

