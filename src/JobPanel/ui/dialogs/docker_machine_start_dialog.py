"""
Dialog for starting Docker Machine.
"""

from PyQt5 import QtWidgets, QtCore

import subprocess


class DockerMachineStartDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Docker Machine Starting...")

        mainVerticalLayout = QtWidgets.QVBoxLayout(self)

        # label
        label = QtWidgets.QLabel("Docker Machine Starting...", self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        mainVerticalLayout.addWidget(label)

        # button
        button = QtWidgets.QPushButton("Terminate")
        button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        button.clicked.connect(self.reject)
        mainVerticalLayout.addWidget(button)
        mainVerticalLayout.setAlignment(button, QtCore.Qt.AlignHCenter)

        self.setMinimumSize(320, 150)

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._check_docker)

        self._running_counter = 0

    def exec(self):
        if not self._start_docker_machine():
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setIcon(QtWidgets.QMessageBox.Critical)
            msg_box.setText("Unable to start Docker Machine.")
            msg_box.exec()

            return QtWidgets.QDialog.Rejected

        if self._is_docker_machine_running():
            return QtWidgets.QDialog.Accepted

        self._timer.start(1000)

        return super().exec()

    def _start_docker_machine(self):
        try:
            subprocess.check_output(["dockerd.bat"], stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            return False
        return True

    def _is_docker_machine_running(self):
        try:
            subprocess.check_output(["docker", "ps"], stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            return False
        return True

    def _check_docker(self):
        if self._is_docker_machine_running():
            self._running_counter += 1

        if self._running_counter >= 5:
            self._timer.stop()
            self.accept()

    def reject(self):
        self._timer.stop()
        super().reject()
