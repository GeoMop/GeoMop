import sys
from PyQt5.QtWidgets import QApplication, QWidget
from main_widget import MainWidget


if __name__ == "__main__":
    app = QApplication(sys.argv )
    w = MainWidget()
    w.resize(400, 600)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())