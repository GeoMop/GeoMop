"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt


class MessageDialog(QWidget):

    MESSAGE_ON_EXIT = ("Jobs are being stopped...\n\n"
                       "Application will be closed when\n"
                       "all jobs have been stopped.")

    #MESSAGE_ON_RESUME = "Jobs are resuming..."

    def __init__(self, parent, message):
        self.can_close = False
        self.force_close = False
        super(MessageDialog, self).__init__(parent)

        self.setWindowTitle("Please wait")
        label = QLabel(message)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.setAlignment(label, Qt.AlignHCenter)
        button = QPushButton("Force close")
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.clicked.connect(self.set_force_close)
        layout.addWidget(button)
        layout.setAlignment(button, Qt.AlignHCenter)
        self.setLayout(layout)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(250, 160)

    def set_force_close(self):
        self.force_close = True

    def closeEvent(self, event):
        if self.can_close:
            event.accept()
            return
        event.ignore()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = MessageDialog(None, MessageDialog.MESSAGE_ON_EXIT)
    dialog.show()
    sys.exit(app.exec_())
