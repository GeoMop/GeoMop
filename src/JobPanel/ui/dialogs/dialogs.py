# -*- coding: utf-8 -*-
"""
Basic application dialog templates, other dialogs should inherit from those to
maintain UI consistency.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
from abc import abstractmethod
from PyQt5 import QtCore, QtGui, QtWidgets

class AFormContainer():
    """
    Abstract form dialog with abstract data manipulation interface.
    """
    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddDialog",
                       windowTitle="Job Panel - Add",
                       title="Add",
                       subtitle="Please select details.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="Edit Dialog",
                        windowTitle="Job Panel - Edit",
                        title="Edit",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyDialog",
                        windowTitle="Job Panel - Copy",
                        title="Copy",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_DELETE = dict(purposeType="PURPOSE_DELETE",
                          objectName="DeleteDialog",
                          windowTitle="Job Panel - Delete",
                          title="Delete",
                          subtitle="This should not happen.")

    # default Copy name prefix
    PURPOSE_COPY_PREFIX = "Copy of"
    # default dialog purpose
    purpose = None

    def __init__(self, old_name=None):
        """initialize"""
        self.old_name = old_name

    @abstractmethod
    def first_focus(self):
        """
        Get focus to first property
        """
        return NotImplemented

    def valid(self):
        """
        Validates input fields and returns True if valid. Otherwise points
        out problems with form.
        (To be overridden in child)
        :return: None
        """        
        data = self.get_data()
        errors = data['preset'].validate(self.excluded, self.permitted)
        self.ui.validator.colorize(errors)
        return len(errors)==0

    def set_purpose(self, purpose=PURPOSE_ADD, data=None):
        """
        Sets the purpose of the dialog. Used for default data labels and
        accept handling.
        :param purpose: Dialog purpose. (ADD/EDIT/COPY)
        :param data: Data to be pre filled if None dialog is cleared.
        :return: None
        """
        self.set_data(data)
        self.purpose = purpose

    def exec_with_purpose(self, purpose, data):
        """
        Executes dialog with given purpose and data.
        :param purpose: Purpose of the dialog. (ADD/EDIT/COPY)
        :param data: Data to be pre filled in dialog.
        :return: dialog.exec()
        """
        self.set_purpose(purpose)
        self.set_data(data, is_edit=(purpose == self.PURPOSE_EDIT))

    def exec_add(self):
        """
        Convenience method for add purpose.
        :return: dialog.exec()
        """
        self.exec_with_purpose(self.PURPOSE_ADD, None)

    def exec_edit(self, data):
        """
        Convenience method for edit purpose.
        :param data: Data to be pre filled in dialog.
        :return: dialog.exec()
        """
        self.exec_with_purpose(self.PURPOSE_EDIT, data)

    def exec_copy(self, data):
        """
        Convenience method for copy purpose.
        :param data: Data to be pre filled in dialog.
        :return: dialog.exec()
        """
        return self.exec_with_purpose(self.PURPOSE_COPY, data)

    @abstractmethod
    def get_data(self):
        """
        Gets data from form fields. Used by accept signal.
        (To be overridden in child)
        :return: Dialog preset
        """
        return NotImplemented

    @abstractmethod
    def set_data(self, data=None):
        """
        Set data to form fields.
        (To be overridden in child)
        :param data: Preset data to be used.
        :return: None
        """
        return NotImplemented

class AFormDialog(QtWidgets.QDialog):
    """
    Abstract form dialog with abstract data manipulation interface.
    """
    # purposes of dialog by action
    PURPOSE_ADD = AFormContainer.PURPOSE_ADD
    PURPOSE_EDIT = AFormContainer.PURPOSE_EDIT
    PURPOSE_COPY = AFormContainer.PURPOSE_COPY
    PURPOSE_DELETE = AFormContainer.PURPOSE_DELETE
    # default Copy name prefix
    PURPOSE_COPY_PREFIX = "Copy of"
    # default dialog purpose
    purpose = None

    # custom accept signal
    accepted = QtCore.pyqtSignal(dict, dict)

    def __init__(self, old_name=None):
        """initialize"""
        super(AFormDialog, self).__init__()        
        self.old_name = old_name

    def accept(self):
        """
        Accepts the form if all data fields are valid.
        :return: None
        """
        if self.valid():
            super().accept()

    @abstractmethod
    def valid(self):
        """
        Validates input fields and returns True if valid. Otherwise points
        out problems with form.
        (To be overridden in child)
        :return: None
        """
        return NotImplemented

    def set_purpose(self, purpose=PURPOSE_ADD, data=None):
        """
        Sets the purpose of the dialog. Used for default data labels and
        accept handling.
        :param purpose: Dialog purpose. (ADD/EDIT/COPY)
        :param data: Data to be pre filled if None dialog is cleared.
        :return: None
        """
        self.set_data(data)
        self.purpose = purpose
        self.setWindowTitle(purpose["windowTitle"])
        self.ui.titleLabel.setText(purpose["title"])
        self.ui.subtitleLabel.setText(purpose["subtitle"])

    def _connect_slots(self):
        """
        Connects generic slots for dialog.
        (must be called after UI setup in child)
        :return: None
        """
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def exec_with_purpose(self, purpose, data):
        """
        Executes dialog with given purpose and data.
        :param purpose: Purpose of the dialog. (ADD/EDIT/COPY)
        :param data: Data to be pre filled in dialog.
        :return: dialog.exec()
        """
        self.set_purpose(purpose)
        self.set_data(data, is_edit=(purpose == self.PURPOSE_EDIT))
        return self.exec()

    def exec_add(self):
        """
        Convenience method for add purpose.
        :return: dialog.exec()
        """
        return self.exec_with_purpose(self.PURPOSE_ADD, None)

    def exec_edit(self, data):
        """
        Convenience method for edit purpose.
        :param data: Data to be pre filled in dialog.
        :return: dialog.exec()
        """
        return self.exec_with_purpose(self.PURPOSE_EDIT, data)

    def exec_copy(self, data):
        """
        Convenience method for copy purpose.
        :param data: Data to be pre filled in dialog.
        :return: dialog.exec()
        """
        return self.exec_with_purpose(self.PURPOSE_COPY, data)

    @abstractmethod
    def get_data(self):
        """
        Gets data from form fields. Used by accept signal.
        (To be overridden in child)
        :return: Dialog preset
        """
        return NotImplemented

    @abstractmethod
    def set_data(self, data=None):
        """
        Set data to form fields.
        (To be overridden in child)
        :param data: Preset data to be used.
        :return: None
        """
        return NotImplemented


class UiFormDialog:
    """
    UI of basic form dialog.
    """

    def setup_ui(self, dialog):
        """
        Setup UI on passed dialog.
        :param dialog: All UI components are attached to this dialog.
        :return: Decorated dialog
        """
        # dialog properties
        dialog.setObjectName("FormDialog")
        dialog.setWindowTitle("Form dialog")
        dialog.setModal(True)

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(
            self.mainVerticalLayoutWidget)

        # labels
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                           QtWidgets.QSizePolicy.Maximum)

        # title label
        self.titleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        titleFont = QtGui.QFont()
        titleFont.setPointSize(15)
        titleFont.setBold(True)
        titleFont.setWeight(75)
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setText("Title")
        self.titleLabel.setSizePolicy(sizePolicy)
        # self.titleLabel.setWordWrap(True)
        self.mainVerticalLayout.addWidget(self.titleLabel)

        # subtitle label
        self.subtitleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        subtitleFont = QtGui.QFont()
        subtitleFont.setWeight(50)
        self.subtitleLabel.setFont(subtitleFont)
        self.subtitleLabel.setObjectName("subtitleLabel")
        self.subtitleLabel.setText("Subtitle text")
        self.subtitleLabel.setSizePolicy(sizePolicy)
        # self.subtitleLabel.setWordWrap(True)
        self.mainVerticalLayout.addWidget(self.subtitleLabel)

        # divider
        self.headerDivider = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.headerDivider.setObjectName("headerDivider")
        self.headerDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.headerDivider)

        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 5, 0, 5)

        # add form to main layout
        self.mainVerticalLayout.addLayout(self.formLayout)

        # button box (order of of buttons is set by system default)
        self.buttonBox = QtWidgets.QDialogButtonBox(
            self.mainVerticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Close | QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.mainVerticalLayout.addWidget(self.buttonBox)

        # resize layout to fit dialog
        dialog.setLayout(self.mainVerticalLayout)
        return dialog


class APresetsDialog(QtWidgets.QDialog):
    """
    Abstract preset dialog.
    """
    presets = dict()
    
    def __init__(self, parent, presets, subdlg_class):        
        super().__init__(parent)        
        self.presets = presets
        """data"""
        excluded_names = [preset.name for __, preset in self.presets.items()]
        self.presets_dlg = subdlg_class(parent=self, excluded_names=excluded_names)
        """dialog with selected preset"""
        self.new_data = False
        """in subdialog is new data"""
        self.subdialog = self.presets_dlg.form
        """subdialog form"""
        self.last_selected = None
        """Last selected item for reverse operation""" 
        self.reload_data = True
        """Reload data during reload"""
        self.ui.setup_ui(self)
        self.reload_view( presets)
        self.connect_slots()

    def reload_view(self, data, first=True, new_sel=False):
        """
        Reload view.
        
        parameters:
        :param bool first: is selected first row
        :param string new_sel: is selected row with set key
        """
        # not reload view during delete
        reload_data = self.reload_data
        self.reload_data = False
        self.ui.presets.clear()
        self.reload_data = True
        self.reload_data = reload_data
        if data:
            for key in data:
                row = QtWidgets.QTreeWidgetItem(self.ui.presets)
                row.setText(0, str(key))
                row.setText(1, data[key].get_name())
                if first or key==new_sel:
                    first = False
                    self.ui.presets.setCurrentItem(row)
            if first:
                self._handle_add_preset_action()
            else:
                self._handle_item_changed()
            self.ui.presets.resizeColumnToContents(1)
        else:
            self.presets_dlg.edit_enable(False)
            
    def _handle_item_changed(self):
        """item changet signal function in presets list""" 
        if not self.reload_data:
            return
        if self.presets:
            if self.ui.presets.currentItem():
                if not self._test_opened("PURPOSE_EDIT"):
                    return
                key = self.ui.presets.currentItem().text(0)
                preset = copy.deepcopy(self.presets[key])
                preset.demangle_secret()
                data = {
                    "preset": preset
                }
                self.presets_dlg.exec_edit(data)
                self.presets_dlg.first_focus()
            else:
                self._handle_add_preset_action()
 
    def _handle_add_preset_action(self):
        if not self._test_opened("PURPOSE_ADD"):
            return
        self.presets_dlg.exec_add()
        self.presets_dlg.first_focus()

    def _handle_save_preset_action(self):
        if not self.presets_dlg.valid(): 
            QtWidgets.QMessageBox.critical(
                        self, 'Data is invalid',
                        'Please fix invalid data before saving'
                    )
            return False
        data = self.presets_dlg.get_data()
        if self.presets_dlg.purpose == self.presets_dlg.PURPOSE_EDIT:
            self.presets.pop(data['old_name'])
        preset = copy.deepcopy(data['preset'])
        preset.mangle_secret()
        self.presets[preset.name] = preset
        self.presets.save() 
        if self.presets_dlg.purpose == self.presets_dlg.PURPOSE_EDIT:
            name = self.ui.presets.currentItem().text(0)
        else:
            name = preset.name
        self.presets_dlg.set_purpose(self.presets_dlg.PURPOSE_EDIT, data)
        self.new_data=False
        self.reload_data = False
        self.reload_view(self.presets, False, name)
        self.reload_data = True
        return True
        

    def _handle_copy_preset_action(self):
        if self.presets and self.ui.presets.currentItem():
            key = self.ui.presets.currentItem().text(0)
            if not self._test_opened("PURPOSE_COPY"):
                return            
            preset = copy.deepcopy(self.presets[key])
            preset.name = self.presets_dlg.\
                PURPOSE_COPY_PREFIX + " " + preset.name
            preset.demangle_secret()
            data = {
                "key": key,
                "preset": preset
            }
            self.presets_dlg.exec_copy(data)
            self.presets_dlg.first_focus()

    def _handle_delete_preset_action(self):
        if self.presets and self.ui.presets.currentItem():
            key = self.ui.presets.currentItem().text(0)
            self.presets.pop(key)  # delete by key
            self.reload_view(self.presets)
            
    def _handle_restore_preset_action(self):
        if self.presets:
            if self.ui.presets.currentItem():
                key = self.ui.presets.currentItem().text(0)
                preset = copy.deepcopy(self.presets[key])
                preset.demangle_secret()
                data = {
                    "preset": preset
                }
                self.presets_dlg.exec_edit(data)
                self.presets_dlg.first_focus()

    def _test_opened(self, new_purpose):
        """
        test if in subdialog changed presset and 
        if is offer action to user and do it
        :return: if next action could be done return False
        """
        if not self.new_data:
            if self.last_selected is not None and \
                self.presets_dlg. is_dirty():
                msg = QtWidgets.QMessageBox()
                msg.setText("Editing record is not saved.")
                msg.setInformativeText("Do you want to save new record?")
                msg.setStandardButtons(QtWidgets.QMessageBox.Save |  \
                    QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Reset)
                msg.button(QtWidgets.QMessageBox.Discard).setText("Discard changes")
                msg.button(QtWidgets.QMessageBox.Reset).setText("Keep record")
                msg.setDefaultButton(QtWidgets.QMessageBox.Save);
                ret = msg.exec_()
                if ret==QtWidgets.QMessageBox.Save:
                    if not self._handle_save_preset_action():
                        self.reload_data = False
                        self.ui.presets.setCurrentItem(self.last_selected)
                        self.reload_data = True
                        return False
                elif ret==QtWidgets.QMessageBox.Reset:
                    self.reload_data = False
                    self.ui.presets.setCurrentItem(self.last_selected)
                    self.reload_data = True
                    return False
        else:            
            msg = QtWidgets.QMessageBox()
            msg.setText("New data record is not saved.")
            msg.setInformativeText("Do you want to save new record?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Save |  \
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Reset)
            msg.button(QtWidgets.QMessageBox.Discard).setText("Discard changes")
            msg.button(QtWidgets.QMessageBox.Reset).setText("Keep record")
            msg.setDefaultButton(QtWidgets.QMessageBox.Save);
            ret = msg.exec_()
            if ret==QtWidgets.QMessageBox.Save: 
                if not self._handle_save_preset_action():
                    self.reload_data = False
                    self.ui.presets.setCurrentItem(self.last_selected)
                    self.reload_data = True
                    return False
            elif ret==QtWidgets.QMessageBox.Reset:
                self.reload_data = False
                self.ui.presets.setCurrentItem(None)
                self.reload_data = True
                return False
        self.last_selected = self.ui.presets.currentItem()
        if new_purpose!=AFormDialog.PURPOSE_EDIT['purposeType']:
            self.ui.presets.setCurrentItem(None)
            self.new_data=True
        else:
            self.new_data=False
        self.last_selected = self.ui.presets.currentItem()
        return True    
    
    def _handle_close_action(self):
        """Close dialog"""
        if not self._test_opened("PURPOSE_EDIT"):
            return
        self.reject()

    def connect_slots(self):
        """
        Connect generic slots for dialog
        (must be called after UI setup in child)
        :return: None
        """
        self.ui.presets.itemSelectionChanged.connect(self._handle_item_changed)
        self.ui.btnAdd.clicked.connect(self._handle_add_preset_action)
        self.ui.btnSave.clicked.connect(self._handle_save_preset_action)
        self.ui.btnCopy.clicked.connect(self._handle_copy_preset_action)
        self.ui.btnDelete.clicked.connect(self._handle_delete_preset_action)
        self.ui.btnRestore.clicked.connect(self._handle_restore_preset_action)
        self.ui.btnClose.clicked.connect(self._handle_close_action)

class UiPresetsDialog:
    """
    UI of basic presets dialog.
    """
    def __init__(self):        
        self.subdialog = None
        """Selected preset panel"""

    def setup_ui(self, dialog):
        """
        Setup UI on passed dialog.
        :param dialog: All UI components are attached to this dialog.
        :return: Decorated dialog
        """
        # dialog properties
        dialog.setObjectName("PresetsDialog")
        dialog.setWindowTitle("Presets dialog")
        dialog.setModal(True)

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.mainVerticalLayoutWidget.setObjectName("mainVerticalLayoutWidget")
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(
            self.mainVerticalLayoutWidget)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 5, 0, 5)

        # presets tree widget
        self.presets = QtWidgets.QTreeWidget(dialog)
        self.presets.setAlternatingRowColors(True)
        self.presets.setObjectName("presets")
        self.presets.setHeaderLabels(["Id", "Name"])
        self.presets.setColumnHidden(0, True)
        self.presets.setSortingEnabled(True)
        self.presets.sortByColumn(1, QtCore.Qt.AscendingOrder)

        # add presets to layout
        self.horizontalLayout.addWidget(self.presets)

        # buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")

        self.btnAdd = QtWidgets.QPushButton(dialog)
        self.btnAdd.setText("&Add")
        self.btnAdd.setObjectName("btnAdd")
        self.buttonLayout.addWidget(self.btnAdd)

        self.btnSave = QtWidgets.QPushButton(dialog)
        self.btnSave.setText("&Save")
        self.btnSave.setObjectName("btnSave")
        self.buttonLayout.addWidget(self.btnSave)

        self.btnCopy = QtWidgets.QPushButton(dialog)
        self.btnCopy.setText("&Copy")
        self.btnCopy.setObjectName("btnCopy")
        self.buttonLayout.addWidget(self.btnCopy)

        self.btnDelete = QtWidgets.QPushButton(dialog)
        self.btnDelete.setText("&Delete")
        self.btnDelete.setObjectName("btnDelete")
        self.buttonLayout.addWidget(self.btnDelete)

        self.btnRestore = QtWidgets.QPushButton(dialog)
        self.btnRestore.setText("&Restore")
        self.btnRestore.setObjectName("btnRestore")
        self.buttonLayout.addWidget(self.btnRestore)

        spacerItem = QtWidgets.QSpacerItem(20, 40,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)

        self.btnClose = QtWidgets.QPushButton(dialog)
        self.btnClose.setText("C&lose")
        self.btnClose.setObjectName("btnClose")
        self.buttonLayout.addWidget(self.btnClose)

        # add buttons to layout
        self.horizontalLayout.addLayout(dialog.subdialog)

        # add presets and buttons layout to main
        self.mainVerticalLayout.addLayout(self.horizontalLayout)
        
        # add buttons to layout
        self.mainVerticalLayout.addLayout(self.buttonLayout)

        # resize layout to fit dialog
        dialog.setLayout(self.mainVerticalLayout)
        return dialog
