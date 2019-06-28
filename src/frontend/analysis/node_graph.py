"""
Start script that initializes main window and runs APP.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""


import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.chdir("../")
temp = os.getcwd()
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(os.getcwd()))))
os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5.QtWidgets import QApplication, QWidget
from frontend.analysis.widgets.main_widget import MainWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWidget()
    w.resize(1000, 720)
    w.move(300, 50)
    w.setWindowTitle('Analysis')
    w.show()

    sys.exit(app.exec_())
