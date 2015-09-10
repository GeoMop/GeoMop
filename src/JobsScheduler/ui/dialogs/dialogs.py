# -*- coding: utf-8 -*-
"""
Basic dialogs templates
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import uuid


class AbstractFormDialog(QtWidgets.QDialog):
    """
    Form dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
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
    # Default dialog purpose
    purpose = PURPOSE_ADD

    # Default Copy name prefix
    COPY_PREFIX = "Copy of"

    # Custom accept signal
    accepted = QtCore.pyqtSignal(dict, list)

    def accept(self):
        super(AbstractFormDialog, self).accept()
        self.accepted.emit(self.purpose, self.get_data())

    def set_purpose(self, purpose=PURPOSE_ADD, data=None):
        self.set_data(data)
        self.purpose = purpose
        self.setObjectName(purpose["objectName"])
        self.setWindowTitle(purpose["windowTitle"])
        self.ui.titleLabel.setText(purpose["title"])
        self.ui.subtitleLabel.setText(purpose["subtitle"])

    def _connect_slots(self):
        """
        Connect generic slots for dialog
        (must be called after UI setup in child)
        """
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def get_data(self):
        """
        Get data from form fields as list.
        (To be overridden in child)
        """
        pass

    def set_data(self, data=None):
        """
        Set data to form fields from list.
        (To be overridden in child)
        """
        pass


class UiFormDialog(object):
    """
    UI of basic form dialog.
    """
    def setup_ui(self, dialog):
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
        title_font = QtGui.QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_font.setWeight(75)
        self.titleLabel.setFont(title_font)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setText("Title")
        self.titleLabel.setSizePolicy(sizePolicy)
        # self.titleLabel.setWordWrap(True)
        self.mainVerticalLayout.addWidget(self.titleLabel)

        # subtitle label
        self.subtitleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        subtitle_font = QtGui.QFont()
        subtitle_font.setWeight(50)
        self.subtitleLabel.setFont(subtitle_font)
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


class AbstractPresetsDialog(QtWidgets.QDialog):
    """
    Presets Dialog executive code with bindings and other functionality.
    """
    presets = list()
    presets_changed = QtCore.pyqtSignal(list)

    def _reload_view(self, presets):
        self.ui.presets.clear()
        if presets:
            for row_id, row in enumerate(presets):
                QtWidgets.QTreeWidgetItem(self.ui.presets)
                for col_id, item in enumerate(row[0:3]):
                    self.ui.presets.topLevelItem(row_id).setText(col_id,
                                                                 str(item))

    def _handle_add_preset_action(self):
        self.presets_dlg.set_purpose(self.presets_dlg.PURPOSE_ADD)
        self.presets_dlg.show()

    def _handle_edit_preset_action(self):
        if self.presets:
            self.presets_dlg.set_purpose(self.presets_dlg.PURPOSE_EDIT)
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            self.presets_dlg.set_data(list(self.presets[index]))
            self.presets_dlg.show()

    def _handle_copy_preset_action(self):
        if self.presets:
            self.presets_dlg.set_purpose(self.presets_dlg.PURPOSE_COPY)
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            data = list(self.presets[index])
            data[0] = None
            data[1] = self.presets_dlg.COPY_PREFIX + " " + data[1]
            self.presets_dlg.set_data(data)
            self.presets_dlg.show()

    def _handle_delete_preset_action(self):
        if self.presets:
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            self.presets.pop(index)
            self.presets_changed.emit(self.presets)

    def handle_presets_dialog(self, purpose, data):
        if purpose != self.presets_dlg.PURPOSE_EDIT:
            data[0] = str(uuid.uuid4())
            self.presets.append(data)
        else:
            for i, item in enumerate(self.presets):
                if item[0] == data[0]:
                    self.presets[i] = data
        self.presets_changed.emit(self.presets)

    def _connect_slots(self):
        """
        Connect generic slots for dialog
        (must be called after UI setup in child)
        """
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.presets_changed.connect(self._reload_view)
        self.ui.btnAdd.clicked.connect(self._handle_add_preset_action)
        self.ui.btnEdit.clicked.connect(self._handle_edit_preset_action)
        self.ui.btnCopy.clicked.connect(self._handle_copy_preset_action)
        self.ui.btnDelete.clicked.connect(self._handle_delete_preset_action)
        self.presets_dlg.accepted.connect(self.handle_presets_dialog)


class UiPresetsDialog(object):
    """
    UI of basic presets dialog.
    """
    def setup_ui(self, dialog):
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

        self.presets = QtWidgets.QTreeWidget(dialog)
        self.presets.setAlternatingRowColors(True)
        self.presets.setObjectName("presets")
        self.presets.setHeaderLabels(["Id", "Name", "Description"])
        self.presets.setColumnHidden(0, True)

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
        # add buttons to layout
        self.horizontalLayout.addLayout(self.buttonLayout)

        # add presets and buttons layout to main
        self.mainVerticalLayout.addLayout(self.horizontalLayout)

        # button box (order of of buttons is set by system default)
        self.buttonBox = QtWidgets.QDialogButtonBox(
            self.mainVerticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.mainVerticalLayout.addWidget(self.buttonBox)

        # resize layout to fit dialog
        dialog.setLayout(self.mainVerticalLayout)
