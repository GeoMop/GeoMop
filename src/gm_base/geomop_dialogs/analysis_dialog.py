"""Analysis dialog.
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os
import sys
import subprocess
import tempfile
from PyQt5 import QtWidgets, QtGui, QtCore
from .dialogs import AFormDialog, UiFormDialog
from gm_base.geomop_analysis import Analysis
from gm_base import icon


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

        if purpose == AnalysisDialog.PURPOSE_EDIT:
            self.ui.refreshButton.clicked.connect(self._handle_refreshButton)
            self.ui.layersFileEditButton.clicked.connect(self._handle_layersFileEditButton)
            self.ui.flowInputEditButton.clicked.connect(self._handle_flowInputEditButton)
            self.ui.scriptMakeButton.clicked.connect(self._handle_scriptMakeButton)

    def _handle_refreshButton(self):
        self.analysis.sync_files()
        self._update_files()

    def _handle_layersFileEditButton(self):
        editor_path = os.path.join("LayerEditor", "layer_editor.py")
        file = self.ui.layersFileComboBox.currentText()
        self._start_editor(editor_path, file)

    def _handle_flowInputEditButton(self):
        editor_path = os.path.join("ModelEditor", "model_editor.py")
        file = self.ui.flowInputComboBox.currentText()
        self._start_editor(editor_path, file)

    def _start_editor(self, editor_path, file):
        """Starts editor with selected file."""
        geomop_root = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
        args = [sys.executable, os.path.join(geomop_root, editor_path)]
        if file:
            args.append(os.path.join(self.analysis.analysis_dir, file))

        with tempfile.TemporaryFile(mode='w+') as fd_err:
            try:
                proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=fd_err, cwd=self.analysis.analysis_dir)
            except OSError as e:
                self._start_editor_error_dialog("Error in starting editor:\n{}: {}".format(e.__class__.__name__, e))
            else:
                try:
                    proc.wait(1)
                except subprocess.TimeoutExpired:
                    pass
                else:
                    if proc.returncode != 0:
                        fd_err.seek(0)
                        err_text = fd_err.read()
                        if not err_text:
                            err_text = "returncode == {}".format(proc.returncode)
                        self._start_editor_error_dialog("Error in editor:\n{}".format(err_text))

    def _start_editor_error_dialog(self, error_text):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setText(error_text)
        msg_box.exec()

    def _handle_scriptMakeButton(self):
        """Generate default Flow execution script."""
        defaul_script_name = "analysis.py"
        script_path = os.path.join(self.analysis.analysis_dir, defaul_script_name)

        # script content
        flow_input_file = self.ui.flowInputComboBox.currentText()
        if len(flow_input_file) == 0:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Warning")
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText("First select Flow123d input file.")
            msg_box.exec()
            return
        script = (
            "gen = VariableGenerator(Variable=Struct())\n"
            "flow = Flow123dAction(Inputs=[gen], YAMLFile='{}')\n"
            "pipeline = Pipeline(ResultActions=[flow])\n"
        ).format(flow_input_file)

        # confirm overwrite
        if os.path.exists(script_path):
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Confirmation")
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Cancel)
            button = QtWidgets.QPushButton('&Overwrite')
            msg_box.addButton(button, QtWidgets.QMessageBox.YesRole)
            msg_box.setDefaultButton(button)
            msg_box.setText('Script file: "{}" already exists, do you want to overwrite it?'
                            .format(defaul_script_name))
            msg_box.exec()
            if msg_box.clickedButton() != button:
                return

        # save file
        try:
            with open(script_path, 'w') as fd:
                fd.write(script)
        except Exception as e:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setIcon(QtWidgets.QMessageBox.Critical)
            msg_box.setText("Unable to save script: {0}".format(e))
            msg_box.exec()
            return

        self._handle_refreshButton()

        # select generated file
        ind = self.ui.scriptComboBox.findText(defaul_script_name)
        if ind >= 0:
            self.ui.scriptComboBox.setCurrentIndex(ind)

    def _update_files(self):
        """Updates comboboxs according to actual directory content."""
        # keep selected files
        flowInputText = self.ui.flowInputComboBox.currentText()
        layersFileText = self.ui.layersFileComboBox.currentText()
        scriptText = self.ui.scriptComboBox.currentText()

        # fill file comboboxs
        self.ui.flowInputComboBox.clear()
        self.ui.flowInputComboBox.addItems([file.file_path for file in self.analysis.files])

        self.ui.layersFileComboBox.clear()
        self.ui.layersFileComboBox.addItems([file.file_path for file in self.analysis.layers_files])

        self.ui.scriptComboBox.clear()
        self.ui.scriptComboBox.addItems([file.file_path for file in self.analysis.script_files])

        # select files
        ind = self.ui.flowInputComboBox.findText(flowInputText)
        if ind < 0:
            for file in self.analysis.files:
                if file.selected:
                    ind = self.ui.flowInputComboBox.findText(file.file_path)
                    break
            if (ind < 0) and (len(self.analysis.files) > 0):
                ind = 0
        self.ui.flowInputComboBox.setCurrentIndex(ind)

        ind = self.ui.layersFileComboBox.findText(layersFileText)
        if ind < 0:
            for file in self.analysis.layers_files:
                if file.selected:
                    ind = self.ui.layersFileComboBox.findText(file.file_path)
                    break
            if (ind < 0) and (len(self.analysis.layers_files) > 0):
                ind = 0
        self.ui.layersFileComboBox.setCurrentIndex(ind)

        ind = self.ui.scriptComboBox.findText(scriptText)
        if ind < 0:
            for file in self.analysis.script_files:
                if file.selected:
                    ind = self.ui.scriptComboBox.findText(file.file_path)
                    break
            if (ind < 0) and (len(self.analysis.script_files) > 0):
                ind = 0
        self.ui.scriptComboBox.setCurrentIndex(ind)

    def valid(self):
        valid = True
        return valid

    def get_data(self):
        return dict()

    def set_data(self, data=None):
        if data:
            self._update_files()

    def accept(self):
        """Handles a confirmation."""
        super(AnalysisDialog, self).accept()

        #self.analysis.flow123d_version = self.ui.f123d_version_combo_box.currentText()
        self.analysis.flow123d_version = ""

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
        if self.purpose == AnalysisDialog.PURPOSE_EDIT:
            # set selected files
            for file in self.analysis.files:
                file.selected = file.file_path == self.ui.flowInputComboBox.currentText()

            for file in self.analysis.layers_files:
                file.selected = file.file_path == self.ui.layersFileComboBox.currentText()

            for file in self.analysis.script_files:
                file.selected = file.file_path == self.ui.scriptComboBox.currentText()

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

        # name
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.addRow(self.nameLabel, self.nameLineEdit)
        if dialog.purpose == AnalysisDialog.PURPOSE_EDIT:
            self.nameLineEdit.setReadOnly(True)
            self.nameLineEdit.setText(self.analysis.name)

        # directory
        if dialog.purpose == AnalysisDialog.PURPOSE_EDIT:
            self.dirLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.dirLabel.setObjectName("dirLabel")
            self.dirLabel.setText("Directory:")
            self.dirPathLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.dirPathLabel.setObjectName("dirPathLabel")
            self.dirPathLabel.setText(self.analysis.analysis_dir)
            self.formLayout.addRow(self.dirLabel, self.dirPathLabel)

        # remove button box
        self.mainVerticalLayout.removeWidget(self.buttonBox)

        # self.f123d_version_label = QtWidgets.QLabel("Flow123d version: ")
        # self.f123d_version_combo_box = QtWidgets.QComboBox()
        # flow123d_versions = dialog.flow123d_versions
        # if not dialog.flow123d_versions:
        #     flow123d_versions = [dialog.analysis.flow123d_version]
        # self.f123d_version_combo_box.addItems(sorted(flow123d_versions, reverse=True))
        # index = self.f123d_version_combo_box.findText(dialog.analysis.flow123d_version)
        # index = 0 if index == -1 else index
        # self.f123d_version_combo_box.setCurrentIndex(index)
        # self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
        #                           self.f123d_version_label)
        # self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
        #                           self.f123d_version_combo_box)

        if dialog.purpose != AnalysisDialog.PURPOSE_ADD:
            # separator
            sep = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            sep.setText("")
            self.formLayout.addRow(sep)

            # layers file
            self.layersFileLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.layersFileLabel.setText("Layers file:")
            self.layersFileComboBox = QtWidgets.QComboBox(self.mainVerticalLayoutWidget)
            self.layersFileEditButton = QtWidgets.QPushButton()
            self.layersFileEditButton.setText("Edit")
            self.layersFileEditButton.setIcon(icon.get_app_icon("le-geomap"))
            self.layersFileEditButton.setToolTip('Edit in Layer Editor')
            self.layersFileEditButton.setMaximumWidth(100)
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(self.layersFileComboBox)
            layout.addWidget(self.layersFileEditButton)
            self.formLayout.addRow(self.layersFileLabel, layout)

            # flow input
            self.flowInputLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.flowInputLabel.setText("Flow123d input:")
            self.flowInputComboBox = QtWidgets.QComboBox(self.mainVerticalLayoutWidget)
            self.flowInputEditButton = QtWidgets.QPushButton()
            self.flowInputEditButton.setText("Edit")
            self.flowInputEditButton.setIcon(icon.get_app_icon("me-geomap"))
            self.flowInputEditButton.setToolTip('Edit in Model Editor')
            self.flowInputEditButton.setMaximumWidth(100)
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(self.flowInputComboBox)
            layout.addWidget(self.flowInputEditButton)
            self.formLayout.addRow(self.flowInputLabel, layout)

            # script file
            self.scriptLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
            self.scriptLabel.setText("Analysis script:")
            self.scriptComboBox = QtWidgets.QComboBox(self.mainVerticalLayoutWidget)
            self.scriptMakeButton = QtWidgets.QPushButton()
            self.scriptMakeButton.setText("Make script")
            self.scriptMakeButton.setToolTip('Generate default Flow execution')
            self.scriptMakeButton.setMaximumWidth(100)
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(self.scriptComboBox)
            layout.addWidget(self.scriptMakeButton)
            self.formLayout.addRow(self.scriptLabel, layout)

            self.refreshButton = QtWidgets.QPushButton()
            self.refreshButton.setText("Refresh files")
            self.refreshButton.setToolTip('Refresh files according to actual directory content.')
            self.refreshButton.setMaximumWidth(120)
            self.mainVerticalLayout.addWidget(self.refreshButton)

        self.mainVerticalLayout.addStretch(1)

        # add button box
        self.mainVerticalLayout.addWidget(self.buttonBox)

        return dialog


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
