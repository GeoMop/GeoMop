from PyQt5 import QtWidgets,  QtCore, QtGui


class TestSSHDialog(QtWidgets.QDialog):
    """Dialog to enter shh password."""

    def __init__(self, parent, ssh, frontend_service):
        """Initializes the class."""
        super(TestSSHDialog, self).__init__(parent)

        message1 = "Test ssh connection ({0})".format(ssh.get_description())
        self._main_label = QtWidgets.QLabel(message1, self)
        self._main_label.setMinimumSize(400, 40)
        #message2 = "Errors:"
        #self._error_label = QtWidgets.QLabel(message2, self)
        self._error = QtWidgets.QListWidget(self)
        #self._error.resize(400,60)
        self._error.setMinimumSize(400, 300)
        self._error.itemDoubleClicked.connect(self._error_item_clicked)       
        #message3 = "Log:"
        #self._log_label = QtWidgets.QLabel(message3, self)
        # self._log = QtWidgets.QListWidget(self)
        # self._log.resize(400,260)
        # self._log.itemDoubleClicked.connect(self._log_item_clicked)
        
        self._button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        self._button_box.rejected.connect(self.reject)

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self._main_label)
        #main_layout.addWidget(self._error_label)
        main_layout.addWidget(self._error)
        #main_layout.addWidget(self._log_label)
        #main_layout.addWidget(self._log)
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
                self._error.addItem("Error in communication with Backend.\nTry restart frontend.")
                self._error.setCurrentRow(self._error.count() - 1, QtCore.QItemSelectionModel.NoUpdate)
            else:
                self.res_data = res["data"]
                if len(res["data"]["errors"]) > 0:
                    for err in res["data"]["errors"]:
                        self._error.addItem("Error: {}".format(err))
                        item = self._error.item(self._error.count() - 1)
                        item.setForeground(QtGui.QColor(255, 0, 0))
                    self._error.setCurrentRow(self._error.count() - 1, QtCore.QItemSelectionModel.NoUpdate)
                else:
                    self._error.addItem("Successful steps:")
                    for step in res["data"]["successful_steps"]:
                        self._error.addItem(step)
                        item = self._error.item(self._error.count() - 1)
                        item.setForeground(QtGui.QColor(0, 128, 0))

                    self._error.setCurrentRow(self._error.count() - 1, QtCore.QItemSelectionModel.NoUpdate)
                    self._error.addItem("Executables on remote:")
                    for executable in res["data"]["executables"]:
                        self._error.addItem(executable)
                    self._error.setCurrentRow(self._error.count() - 1, QtCore.QItemSelectionModel.NoUpdate)
            finished = True

        # i = 0
        # while True:
        #     mess = self.test.get_next_error()
        #     if mess is None:
        #         break
        #     i += 1
        #     self._error.addItem(mess)
        # if i>0:
        #     i = 0
        #     self._error.setCurrentRow(self._error.count()-1, QtCore.QItemSelectionModel.NoUpdate)
        # while True:
        #     mess = self.test.get_next_log()
        #     if mess is None:
        #         break
        #     i += 1
        #     if mess.endswith("..."):
        #         self._log.addItem(mess)
        #     else:
        #         self._log.addItem("- " + mess)
        #         if mess.endswith("!!!"):
        #             item = self._log.item(self._log.count()-1)
        #             item.setForeground(QtGui.QColor(255,0,0))
        #     if i>0:
        #         self._log.setCurrentRow(self._log.count()-1, QtCore.QItemSelectionModel.NoUpdate)
        if finished:
            self._button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Close")
            self.log_timer.stop()
            self.finished = True
            if len(self.res_data["errors"]) > 0:
                self._error.addItem("Test finished with {0} errors".format(len(self.res_data["errors"])))
                item = self._error.item(self._error.count()-1)
                item.setForeground(QtGui.QColor(255, 0, 0))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            else:
                self._error.addItem("Test finished without errors")
                item = self._error.item(self._error.count()-1)
                item.setForeground(QtGui.QColor(0, 128, 0))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            
    def _error_item_clicked(self, item):
        """error item is clicked"""
        self._list_item_clicked(self._error, item)
        
    # def _log_item_clicked(self, item):
    #     """log item is clicked"""
    #     self._list_item_clicked(self._log, item)
 
    def _copy(self, txt, list=None):
        """copy item text to clicbord (if txt is None copy all lines)"""
        if txt is None:
            if list is None:
                return
            txt = ""
            for i in range(0, list.count()):
                item = list.item(i)
                txt += item.text() + "\n"
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard )
        clipboard.setText(txt, mode=clipboard.Clipboard)

    def _list_item_clicked(self, list, item):
        """double click standart action"""
        menu =  QtWidgets.QMenu()
        action1 = menu.addAction("Copy line to clipboard")
        action1.triggered.connect( lambda: self._copy(item.text()))
        action2 = menu.addAction("Copy all content to clipboard")
        action2.triggered.connect( lambda: self._copy(None, list))
        menu.exec_(QtGui.QCursor.pos() - QtCore.QPoint(20, 10))
 
