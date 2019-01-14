"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""


import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PyQt5.QtWidgets import QApplication, QWidget
from new_diagram.main_widget import MainWidget


if __name__ == "__main__":
    app = QApplication(sys.argv )
    w = MainWidget()
    w.resize(400, 600)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())