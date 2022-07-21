import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QPlainTextEdit, QDialog, QVBoxLayout, QPushButton


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        QtCore.QCoreApplication.processEvents()

class ComputingInfoDlg(QDialog):
    def __init__(self, logging_level, parent=None):
        super(ComputingInfoDlg, self).__init__(parent)
        self.setWindowTitle("Computing...")
        self.setModal(True)
        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging_level)

        self.exit_btn = QPushButton("Please Wait...")
        self.exit_btn.setDisabled(True)

        layout = QVBoxLayout()

        layout.addWidget(logTextBox.widget)
        layout.addWidget(self.exit_btn)
        self.setLayout(layout)
        self.exit_btn.clicked.connect(self.close)

