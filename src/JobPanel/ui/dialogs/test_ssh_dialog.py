from PyQt5 import QtWidgets,  QtCore, QtGui


class TestSSHDialog(QtWidgets.QDialog):
    """Dialog for test ssh connection."""

    def __init__(self, parent, ssh, frontend_service):
        """Initializes the class."""
        super(TestSSHDialog, self).__init__(parent)

        message1 = "Test ssh connection ({0})".format(ssh.get_description())
        self._main_label = QtWidgets.QLabel(message1, self)
        self._main_label.setMinimumSize(400, 40)
        self._log = QtWidgets.QTextEdit(self)
        self._log.setReadOnly(True)
        self._log.setMinimumSize(600, 300)

        self._button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        self._button_box.rejected.connect(self.reject)

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self._main_label)
        main_layout.addWidget(self._log)
        main_layout.addWidget(self._button_box)
       
        self.finished = False
        self.test_answer = frontend_service.ssh_test(ssh)
        self.res_data = None
        
        self.log_timer = QtCore.QTimer()
        self.log_timer.timeout.connect(self._handle_messages)
        self.log_timer.start(100)
        
    def reject(self):
        """Handles a canceling."""
        if not self.finished:
            self.log_timer.stop()
            self.finished = True
        super(TestSSHDialog, self).reject()
        
    def _handle_messages(self):
        """add error to error label"""
        finished = False
        if len(self.test_answer) > 0:
            res = self.test_answer[0]
            if "error" in res:
                self._log.setTextColor(QtCore.Qt.red)
                self._log.append("Error in communication with Backend.\nTry restart frontend.")
            else:
                self.res_data = res["data"]
                if len(res["data"]["errors"]) > 0:
                    self._log.setTextColor(QtCore.Qt.red)
                    for err in res["data"]["errors"]:
                        self._log.append("Error: {}".format(err))
                else:
                    self._log.setTextColor(QtCore.Qt.black)
                    self._log.append("Successful steps:")
                    self._log.setTextColor(QtCore.Qt.darkGreen)
                    for step in res["data"]["successful_steps"]:
                        self._log.append(step)

                    self._log.setTextColor(QtCore.Qt.black)
                    if "version" in res["data"]["installation_info"]:
                        self._log.append("GeoMop version: {}".format(res["data"]["installation_info"]["version"]))
                    if "revision" in res["data"]["installation_info"]:
                        self._log.append("GeoMop revision: {}".format(res["data"]["installation_info"]["revision"]))
                    self._log.append("Executables on remote:")
                    if "executables" in res["data"]["installation_info"]:
                        for executable in res["data"]["installation_info"]["executables"]:
                            self._log.append(executable["name"])
            finished = True

        if finished:
            self._button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Close")
            self.log_timer.stop()
            self.finished = True
            self._log.setFontWeight(QtGui.QFont.Bold)
            if (self.res_data is None) or (len(self.res_data["errors"]) > 0):
                self._log.setTextColor(QtCore.Qt.red)
                self._log.append("Test finished with errors")
            else:
                self._log.setTextColor(QtCore.Qt.darkGreen)
                self._log.append("Test finished without errors")
