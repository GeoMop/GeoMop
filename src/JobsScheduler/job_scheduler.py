"""Start script that initializes main window """

import os
import sys
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "lib")
sys.path.insert(1, __lib_dir__)

import os
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


class JobsScheduler:
    """Jobs Scheduler main class"""

    def __init__(self):
        """Initialization of UI"""
        
        # main window
        self._app = QtWidgets.QApplication(sys.argv)
        self._vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._mainwindow = QtWidgets.QMainWindow()
        self._mainwindow.setCentralWidget(self._vsplitter)

        # menu
            # file
        menu_bar = self._mainwindow.menuBar()
        self._file_menu = menu_bar.addMenu('&File')

        # main window show
        self._mainwindow.show()

    def main(self):
        """Main entry point"""
        self._app.exec_()

if __name__ == "__main__":
    JobsScheduler().main()
