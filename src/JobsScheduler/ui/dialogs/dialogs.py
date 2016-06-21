# -*- coding: utf-8 -*-
"""
Basic application dialog templates, other dialogs should inherit from those to
maintain UI consistency.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import uuid
from abc import abstractmethod
from PyQt5 import QtCore, QtGui, QtWidgets

from ui.data.preset_data import Id


class AFormDialog(QtWidgets.QDialog):
    """
    Abstract form dialog with abstract data manipulation interface.
    """
    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddDialog",
                       windowTitle="Job Scheduler - Add",
                       title="Add",
                       subtitle="Please select details.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="Edit Dialog",
                        windowTitle="Job Scheduler - Edit",
                        title="Edit",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyDialog",
                        windowTitle="Job Scheduler - Copy",
                        title="Copy",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_DELETE = dict(purposeType="PURPOSE_DELETE",
                          objectName="DeleteDialog",
                          windowTitle="Job Scheduler - Delete",
                          title="Delete",
                          subtitle="This should not happen.")

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
            self.accepted.emit(self.purpose, self.get_data())

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
        self.setObjectName(purpose["objectName"])
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
        self.mainVerticalLayoutWidget.setObjectName("mainVerticalLayoutWidget")
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(
            self.mainVerticalLayoutWidget)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")

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
    presets_changed = QtCore.pyqtSignal(dict)

    def reload_view(self, data):
        self.ui.presets.clear()
        if data:
            for key in data:
                row = QtWidgets.QTreeWidgetItem(self.ui.presets)
                row.setText(0, str(key))
                row.setText(1, data[key].get_name())
                row.setText(2, data[key].get_description())
            self.ui.presets.resizeColumnToContents(1)
            self.ui.presets.resizeColumnToContents(2)

    def _handle_add_preset_action(self):
        self.create_dialog()
        self.presets_dlg.exec_add()

    def _handle_edit_preset_action(self):
        if self.presets and self.ui.presets.currentItem():
            key = self.ui.presets.currentItem().text(0)
            preset = self.presets[key]
            data = {
                "preset": preset
            }
            self.create_dialog()
            self.presets_dlg.exec_edit(data)

    def _handle_copy_preset_action(self):
        if self.presets and self.ui.presets.currentItem():
            key = self.ui.presets.currentItem().text(0)
            preset = copy.deepcopy(self.presets[key])
            preset.name = self.presets_dlg.\
                PURPOSE_COPY_PREFIX + " " + preset.name
            data = {
                "key": key,
                "preset": preset
            }
            self.create_dialog()
            self.presets_dlg.exec_copy(data)

    def _handle_delete_preset_action(self):
        if self.presets and self.ui.presets.currentItem():
            key = self.ui.presets.currentItem().text(0)
            self.presets.pop(key)  # delete by key
            self.presets_changed.emit(self.presets)

    def handle_presets_dialog(self, purpose, data):
        if purpose == self.presets_dlg.PURPOSE_EDIT:
            self.presets.pop(data['old_name'])
        preset = data['preset']
        self.presets[preset.name] = preset
        self.presets_changed.emit(self.presets)

    def connect_slots(self):
        """
        Connect generic slots for dialog
        (must be called after UI setup in child)
        :return: None
        """
        self.presets_changed.connect(self.reload_view)
        self.ui.btnAdd.clicked.connect(self._handle_add_preset_action)
        self.ui.btnEdit.clicked.connect(self._handle_edit_preset_action)
        self.ui.btnCopy.clicked.connect(self._handle_copy_preset_action)
        self.ui.btnDelete.clicked.connect(self._handle_delete_preset_action)
        self.ui.btnClose.clicked.connect(self.reject)

    def create_dialog(self):
        if self.presets is not None:
            excluded_names = [preset.name for __, preset in self.presets.items()]
        else:
            excluded_names = []
        # set custom dialog
        self.presets_dlg = self.DlgClass(parent=self, excluded_names=excluded_names)
        self.presets_dlg.accepted.connect(self.handle_presets_dialog)


class UiPresetsDialog:
    """
    UI of basic presets dialog.
    """

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
        self.presets.setHeaderLabels(["Id", "Name", "Description"])
        self.presets.setColumnHidden(0, True)
        self.presets.setSortingEnabled(True)

        # add presets to layout
        self.horizontalLayout.addWidget(self.presets)

        # buttons
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")

        self.btnAdd = QtWidgets.QPushButton(dialog)
        self.btnAdd.setText("&Add")
        self.btnAdd.setObjectName("btnAdd")
        self.buttonLayout.addWidget(self.btnAdd)

        self.btnEdit = QtWidgets.QPushButton(dialog)
        self.btnEdit.setText("&Edit")
        self.btnEdit.setObjectName("btnEdit")
        self.buttonLayout.addWidget(self.btnEdit)

        self.btnCopy = QtWidgets.QPushButton(dialog)
        self.btnCopy.setText("&Copy")
        self.btnCopy.setObjectName("btnCopy")
        self.buttonLayout.addWidget(self.btnCopy)

        self.btnDelete = QtWidgets.QPushButton(dialog)
        self.btnDelete.setText("&Delete")
        self.btnDelete.setObjectName("btnDelete")
        self.buttonLayout.addWidget(self.btnDelete)

        spacerItem = QtWidgets.QSpacerItem(20, 40,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.buttonLayout.addItem(spacerItem)

        self.btnClose = QtWidgets.QPushButton(dialog)
        self.btnClose.setText("C&lose")
        self.btnClose.setObjectName("btnClose")
        self.buttonLayout.addWidget(self.btnClose)

        # add buttons to layout
        self.horizontalLayout.addLayout(self.buttonLayout)

        # add presets and buttons layout to main
        self.mainVerticalLayout.addLayout(self.horizontalLayout)

        # resize layout to fit dialog
        dialog.setLayout(self.mainVerticalLayout)
        return dialog
