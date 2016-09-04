"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


class MessageDialog(QWidget):

    MESSAGE_ON_EXIT = ("Jobs are being paused...\n\n"
                       "Application will be closed when\n"
                       "all jobs have been paused.")

    MESSAGE_ON_RESUME = "Jobs are resuming..."

    def __init__(self, parent, message):
        self.can_close = False
        super(MessageDialog, self).__init__(parent)

        self.setWindowTitle("Please wait")
        label = QLabel(message)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(220, 100)

    def closeEvent(self, event):
        if self.can_close:
            event.accept()
            return
        event.ignore()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = CloseDialog(None)
    dialog.show()
    sys.exit(app.exec_())
