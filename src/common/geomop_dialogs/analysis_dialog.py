"""Analysis dialog.
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os
from PyQt5 import QtWidgets, QtGui

from geomop_analysis import Analysis

from .dialogs import AFormDialog, UiFormDialog
from geomop_analysis import ANALYSIS_MAIN_FILE


class AnalysisDialog(AFormDialog):
    """
    Analysis dialog.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddAnalysisDialog",
                       windowTitle="Create new Analysis",
                       title="Add new Analysis",
                       subtitle="Please select details for new Analysis.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditAnalysisDialog",
                        windowTitle="Edit Analysis",
                        title="Edit Analysis",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyAnalysis",
                        windowTitle="Copy Analysis",
                        title="Copy Analysis",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, purpose=None, config=None, analysis=None):
        super().__init__(parent)

        self.config = config

        if purpose is None:
            purpose = AnalysisDialog.PURPOSE_ADD
        self.purpose = purpose

        if analysis is None:
            assert purpose == AnalysisDialog.PURPOSE_ADD, "Analysis has to be set if purpose is not add."
            analysis = Analysis()
        self.analysis = analysis
        self.flow123d_versions = FLOW123D_VERSION_LIST

        # setup specific UI
        self.ui = UiAnalysisDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(purpose)
        if purpose == AnalysisDialog.PURPOSE_EDIT:
            self.set_data(analysis)

        # connect slots
        super()._connect_slots()

    def valid(self):
        valid = True
        return valid

    def get_data(self):
        return dict()

    def set_data(self, data=None):
        if data:
            # check files
            for i in range(self.ui.filesLayout.count()):
                checkbox = self.ui.filesLayout.itemAt(i).widget()
                if checkbox.file.file_path in data.files:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)

            # fill params
            for __, edit_widget in self.ui.paramWidgets:
                if edit_widget.param.name in data.params:
                    edit_widget.setText(data.params[edit_widget.param.name])

            self.ui.update_params()

    def accept(self):
        """Handles a confirmation."""
        super(AnalysisDialog, self).accept()

        self.analysis.flow123d_version = self.ui.f123d_version_combo_box.currentText()

        if self.purpose == AnalysisDialog.PURPOSE_ADD:
            # name
            name = self.ui.nameLineEdit.text()
            path = os.path.join(self.config.workspace, name)
            if os.path.exists(path):
                QtWidgets.QMessageBox.critical(
                    self, 'Name is not unique',
                    "Can't create analysis. The selected analysis name already exists."
                )
                return
            os.mkdir(path)
            self.analysis.name = name
            self.analysis.workspace = self.config.workspace
            self.analysis.analysis_dir = path
            self.analysis.save()
            self.config.analysis = name
            self.config.save()
        if self.purpose == AnalysisDialog.PURPOSE_EDIT:
            # get all files
            for i in range(self.ui.filesLayout.count()):
                checkbox = self.ui.filesLayout.itemAt(i).widget()

                # find the file in analysis and update selected status
                gen = (f for f in self.analysis.files if f.file_path == checkbox.file.file_path)
                try:
                    file = next(gen)
                except StopIteration:
                    # file not found
                    continue
                file.selected = checkbox.isChecked()

            # get all params
            for i in range(self.ui.paramsLayout.count()):
                widget = self.ui.paramsLayout.itemAt(i).widget()

                # find the parameter in analysis
                gen = (p for p in self.analysis.params if p.name == widget.param.name)
                try:
                    param = next(gen)
                except StopIteration:
                    # parameter not found
                    continue
                param.value = widget.text()

            self.analysis.save()


class UiAnalysisDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        self.analysis = dialog.analysis

        # form layout

        # row 0
        if dialog.purpose == AnalysisDialog.PURPOSE_ADD:
            self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.nameLabel.setObjectName("nameLabel")
            self.nameLabel.setText("Name:")
            self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                      self.nameLabel)
            self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
            self.nameLineEdit.setObjectName("nameLineEdit")
            self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                      self.nameLineEdit)
        elif dialog.purpose == AnalysisDialog.PURPOSE_EDIT:
            self.dirLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.dirLabel.setObjectName("dirLabel")
            self.dirLabel.setText("Analysis Directory:")
            self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                      self.dirLabel)
            self.dirPathLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.dirPathLabel.setObjectName("dirPathLabel")
            self.dirPathLabel.setText(self.analysis.analysis_dir)
            self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                      self.dirPathLabel)

        # remove button box
        self.mainVerticalLayout.removeWidget(self.buttonBox)

        self.f123d_version_label = QtWidgets.QLabel("Flow123d version: ")
        self.f123d_version_combo_box = QtWidgets.QComboBox()
        flow123d_versions = dialog.flow123d_versions
        if not dialog.flow123d_versions:
            flow123d_versions = [dialog.analysis.flow123d_version]
        self.f123d_version_combo_box.addItems(sorted(flow123d_versions, reverse=True))
        index = self.f123d_version_combo_box.findText(dialog.analysis.flow123d_version)
        index = 0 if index == -1 else index
        self.f123d_version_combo_box.setCurrentIndex(index)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.f123d_version_label)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.f123d_version_combo_box)

        if dialog.purpose != AnalysisDialog.PURPOSE_ADD:
            # divider
            self.formDivider = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
            self.formDivider.setObjectName("formDivider")
            self.formDivider.setFrameShape(QtWidgets.QFrame.HLine)
            self.formDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
            self.mainVerticalLayout.addWidget(self.formDivider)

            # font
            labelFont = QtGui.QFont()
            labelFont.setPointSize(11)
            labelFont.setWeight(65)

            # files label
            self.filesLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.filesLabel.setObjectName("filesLabel")
            self.filesLabel.setFont(labelFont)
            self.filesLabel.setText("Files")
            self.mainVerticalLayout.addWidget(self.filesLabel)

            self.filesLayout = QtWidgets.QVBoxLayout()
            self.filesLayout.setContentsMargins(0, 5, 0, 5)
            self.mainVerticalLayout.addLayout(self.filesLayout)

            for file in self.analysis.files:
                checkbox = QtWidgets.QCheckBox()
                checkbox.setChecked(True)
                checkbox.file = file
                checkbox.setText(file.file_path)
                checkbox.stateChanged.connect(self.update_params)
                self.filesLayout.addWidget(checkbox)

            # params label
            self.paramsLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.paramsLabel.setObjectName("paramsLabel")
            self.paramsLabel.setFont(labelFont)
            self.paramsLabel.setText("Parameters")
            self.mainVerticalLayout.addWidget(self.paramsLabel)

            self.paramsLayout = QtWidgets.QFormLayout()
            self.paramsLayout.setContentsMargins(0, 5, 0, 5)
            self.mainVerticalLayout.addLayout(self.paramsLayout)

            # create GUI components for all analysis params
            self.paramWidgets = []
            for i, param in enumerate(self.analysis.params):
                label = QtWidgets.QLabel()
                label.setText(param.name)
                label.param = param
                edit = QtWidgets.QLineEdit()
                edit.param = param
                self.paramWidgets.append((label, edit))
                self.paramsLayout.setWidget(i, 0, label)
                self.paramsLayout.setWidget(i, 1, edit)

            self.update_params()

        self.mainVerticalLayout.addStretch(1)

        # add button box
        self.mainVerticalLayout.addWidget(self.buttonBox)

        return dialog

    def update_params(self, sender=None):
        """Hide or show parameters based on currently checked files."""
        params = []
        for i in range(self.filesLayout.count()):
            checkbox = self.filesLayout.itemAt(i).widget()
            if checkbox.isChecked():
                params.extend(checkbox.file.params)
        params = set(params)  # each param only once

        # set visibility for all widgets
        for i in range(self.paramsLayout.count()):
            widget = self.paramsLayout.itemAt(i).widget()
            widget.include_in_data = widget.param.name in params
            widget.setVisible(widget.include_in_data)


IST_FOLDER = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "resources", "ist")


def list_flow123d_versions():
    """Get a list of flow123d version files without extentions."""
    from os import listdir
    from os.path import isfile, join
    version_list = []
    for file_name in sorted(listdir(IST_FOLDER)):
        if (isfile(join(IST_FOLDER, file_name)) and
                file_name[-5:].lower() == ".json"):
            version_list.append(file_name[:-5])
    # reverse sorting 9 - 0
    return version_list[::-1]


FLOW123D_VERSION_LIST = list_flow123d_versions()
