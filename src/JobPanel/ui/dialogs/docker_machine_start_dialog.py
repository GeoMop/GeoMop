"""
Dialog for starting Docker Machine.
"""

from PyQt5 import QtWidgets, QtCore


class DockerMachineStartDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Docker Machine Starting...")

        mainVerticalLayout = QtWidgets.QVBoxLayout(self)

        # label
        label = QtWidgets.QLabel("Docker Machine Starting...", self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        mainVerticalLayout.addWidget(label)

        self.setMinimumSize(320, 100)

        self._close_enabled = False

        # process
        self._proc = QtCore.QProcess(self)
        self._proc.finished.connect(self._proc_finished)
        self._proc.error.connect(self._proc_finished)
        self._proc.start("docker-machine start")

    def _proc_finished(self):
        self._close_enabled = True
        self.close()

    def reject(self):
        if self._close_enabled:
            super().reject()
