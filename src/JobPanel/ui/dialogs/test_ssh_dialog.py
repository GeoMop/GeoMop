from PyQt5 import QtWidgets,  QtCore, QtGui
from ui.ssh_test import SshTester


class TestSSHDialog(QtWidgets.QDialog):
    """Dialog to enter shh password."""

    def __init__(self, parent, ssh, data):
        """Initializes the class."""
        super(TestSSHDialog, self).__init__(parent)

        message1 = "Test ssh connection ({0})".format(ssh.get_description())
        self._main_label = QtWidgets.QLabel(message1, self)
        self._main_label.setMinimumSize(400, 40)
        message2 = "Errors:" 
        self._error_label = QtWidgets.QLabel(message2, self)
        self._error = QtWidgets.QListWidget(self)
        self._error.resize(400,60)        
        message3 = "Log:"
        self._log_label = QtWidgets.QLabel(message3, self)
        self._log = QtWidgets.QListWidget(self)
        self._log.resize(400,260)       
        
        self._button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        self._button_box.rejected.connect(self.reject)

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self._main_label)
        main_layout.addWidget(self._error_label)
        main_layout.addWidget(self._error)
        main_layout.addWidget(self._log_label)
        main_layout.addWidget(self._log)
        main_layout.addWidget(self._button_box)
       
        self.finished = False
        self.test = SshTester(ssh, data)
        self.test.start()
        
        self.log_timer = QtCore.QTimer()
        self.log_timer.timeout.connect(self._handle_messages)
        self.log_timer.start(500)
        
    def reject(self):
        """Handles a canceling."""
        if not self.finished:
            self.log_timer.stop()
            self.finished = True
            self.test.stop()
        super(TestSSHDialog, self).reject()      
        
    def _handle_messages(self):
        """add error to error label"""
        finished = self.test.finished()
        i = 0
        while True:
            mess = self.test.get_next_error()
            if mess is None:
                break
            i += 1
            self._error.addItem(mess)
        if i>0:
            i = 0
            self._error.setCurrentRow(self._error.count()-1, QtCore.QItemSelectionModel.NoUpdate)
        while True:
            mess = self.test.get_next_log()
            if mess is None:
                break
            i += 1
            if mess.endswith("..."):            
                self._log.addItem(mess)
            else:
                self._log.addItem("   " + mess)
                if mess.endswith("!!!"):
                    item = self._log.item(self._log.count()-1)
                    item.setForeground(QtGui.QColor(255,0,0))
            if i>0:
                self._log.setCurrentRow(self._log.count()-1, QtCore.QItemSelectionModel.NoUpdate)
        if finished:
            self._button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Close")
            self.log_timer.stop()
            self.finished = True
 
