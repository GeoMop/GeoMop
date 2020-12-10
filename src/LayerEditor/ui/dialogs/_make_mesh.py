"""
Dialog for making mesh.
"""

import os
from PyQt5 import QtCore, QtGui, QtWidgets
from LayerEditor.leconfig import cfg

class MakeMeshDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Make mesh")

        grid = QtWidgets.QGridLayout(self)

        # edit for process output
        self._output_edit = QtWidgets.QTextEdit()
        self._output_edit.setReadOnly(True)
        self._output_edit.setFont(QtGui.QFont("monospace"))
        grid.addWidget(self._output_edit, 0, 0, 4, 6)

        # label for showing status
        self._status_label = QtWidgets.QLabel()
        self._set_status("Ready")
        self._status_label.setMaximumHeight(40)
        grid.addWidget(self._status_label, 4, 0, 1, 1)

        # checkbox for apply step size
        self._step_checkbox = QtWidgets.QCheckBox("Mesh step:")
        self._step_checkbox.setMaximumWidth(110)
        self._step_checkbox.stateChanged.connect(self._step_checkbox_changed)
        grid.addWidget(self._step_checkbox, 5, 0)

        # edit for setting step size
        self._step_edit = QtWidgets.QLineEdit()
        self._step_edit.setText("1.0")
        self._step_edit.setValidator(QtGui.QDoubleValidator())
        self._step_edit.setMinimumWidth(100)
        self._step_edit.setMaximumWidth(200)
        self._step_edit.setEnabled(False)
        grid.addWidget(self._step_edit, 5, 1)

        # process
        self._proc = QtCore.QProcess(self)
        self._proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._read_proc_output)
        self._proc.started.connect(self._proc_started)
        self._proc.finished.connect(self._proc_finished)
        self._proc.error.connect(self._proc_error)

        # buttons
        self._start_button = QtWidgets.QPushButton("Start", self)
        self._start_button.clicked.connect(self._start)
        grid.addWidget(self._start_button, 5, 3)
        self._kill_button = QtWidgets.QPushButton("Kill", self)
        self._kill_button.clicked.connect(self._proc.kill)
        self._kill_button.setEnabled(False)
        grid.addWidget(self._kill_button, 5, 4)
        self._close_button = QtWidgets.QPushButton("Close", self)
        self._close_button.clicked.connect(self.reject)
        grid.addWidget(self._close_button, 5, 5)

        self.setLayout(grid)

        self.setMinimumSize(500, 300)
        self.resize(700, 500)

    def _proc_started(self):
        self._start_button.setEnabled(False)
        self._kill_button.setEnabled(True)

        self._step_checkbox.setEnabled(False)
        self._step_edit.setEnabled(False)

        self._set_status("Running")

    def _proc_finished(self):
        self._start_button.setEnabled(True)
        self._kill_button.setEnabled(False)

        self._step_checkbox.setEnabled(True)
        if self._step_checkbox.isChecked():
            self._step_edit.setEnabled(True)

        self._set_status("Ready")

    def _proc_error(self, error):
        if error == QtCore.QProcess.FailedToStart:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setIcon(QtWidgets.QMessageBox.Critical)
            msg_box.setText("Failed to start: {} \nwith arguments: {}".format(self._proc.program(), self._proc.arguments()))
            msg_box.exec()

    def _step_checkbox_changed(self):
        if self._step_checkbox.isChecked():
            self._step_edit.setEnabled(True)
        else:
            self._step_edit.setEnabled(False)

    def _start(self):
        args = []
        geometry_bat = os.path.join(cfg.geomop_root, "bin", "geometry.bat")
        if os.path.exists(geometry_bat):
            cmd = geometry_bat
        else:
            cmd = "python3"
            args.append(os.path.join(cfg.geomop_root, "Geometry", "geometry.py"))
        if self._step_checkbox.isChecked():
            args.append("--mesh-step")
            args.append(self._step_edit.text())
        args.append("--filename_base")
        args.append(os.path.splitext(cfg.curr_file)[0])

        self._output_edit.clear()
        self._proc.start(cmd, args)

        # write serialized data to stdin of process
        self._proc.write(cfg.le_serializer.save(cfg).encode())
        self._proc.closeWriteChannel()

    def _set_status(self, status):
        self._status_label.setText("Status: {}".format(status))

    def _read_proc_output(self):
        self._output_edit.moveCursor(QtGui.QTextCursor.End)
        self._output_edit.insertPlainText(str(self._proc.readAllStandardOutput(), encoding='utf-8'))
        self._output_edit.moveCursor(QtGui.QTextCursor.End)

    def reject(self):
        if self._proc.state() == QtCore.QProcess.Running:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Confirmation")
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Cancel)
            button = QtWidgets.QPushButton('&Kill')
            msg_box.addButton(button, QtWidgets.QMessageBox.YesRole)
            msg_box.setDefaultButton(button)
            msg_box.setText("Process running, do you want to kill it?")
            msg_box.exec()

            if msg_box.clickedButton() == button:
                self._proc.kill()
            else:
                return
        super().reject()
