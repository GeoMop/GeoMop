"""Analysis dialog.
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os
import sys
import subprocess
import tempfile
import re
from PyQt5 import QtWidgets, QtGui, QtCore
from gm_base.geomop_analysis import Analysis, InvalidAnalysis
from gm_base import icon
from gm_base.global_const import GEOMOP_INTERNAL_DIR_NAME


class AddAnalysisDialog(QtWidgets.QDialog):
    re_name = re.compile("^[a-zA-Z0-9]([a-zA-Z0-9]|[_-])*$")

    def __init__(self, parent, config):
        super().__init__(parent)

        self.config = config

        self.analysis_name = ""

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout = QtWidgets.QFormLayout()
        analysis_label = QtWidgets.QLabel("Analysis name:")
        self.analysis_line_edit = QtWidgets.QLineEdit()
        form_layout.addRow(analysis_label, self.analysis_line_edit)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle('Add analysis')
        self.setMinimumSize(300, 100)

    def accept(self):
        """Handles a confirmation."""
        analysis = Analysis()
        analysis.flow123d_version = "2.2.0"

        name = self.analysis_line_edit.text()
        if not self.re_name.match(name):
            QtWidgets.QMessageBox.critical(
                self, 'Name has bad format',
                'Analysis name may contains only letters, digits, "_" and "-".')
            return
        path = os.path.join(self.config.workspace, name)
        if os.path.exists(path):
            QtWidgets.QMessageBox.critical(
                self, 'Name is not unique',
                "Can't create analysis. The selected analysis name already exists.")
            return
        os.mkdir(path)
        analysis.name = name
        analysis.workspace = self.config.workspace
        analysis.analysis_dir = path
        analysis.save()
        self.config.save(0, analysis.name)

        self.analysis_name = name

        super().accept()


class AnalysisDialog(QtWidgets.QDialog):
    """
    Analysis dialog.
    """
    def __init__(self, parent=None, config=None):
        super().__init__(parent)

        self.config = config

        self.last_selected = None

        self.setWindowTitle("Analyses")

        self.analysis = None
        self.flow123d_versions = FLOW123D_VERSION_LIST

        # setup specific UI
        self.ui = UiAnalysisDialog()
        self.ui.setup_ui(self)

        self.ui.analysisListTreeWidget.itemSelectionChanged.connect(self._handle_item_changed)
        self.ui.btnAdd.clicked.connect(self._handle_add_analysis_action)
        self.ui.btnSave.clicked.connect(self._handle_save_analysis_action)
        self.ui.btnRestore.clicked.connect(self._handle_restore_analysis_action)
        self.ui.btnClose.clicked.connect(self._handle_close_action)

        self.set_data(None)

        self.ui.refreshButton.clicked.connect(self._handle_refreshButton)
        self.ui.layersFileEditButton.clicked.connect(self._handle_layersFileEditButton)
        self.ui.flowInputEditButton.clicked.connect(self._handle_flowInputEditButton)
        self.ui.scriptMakeButton.clicked.connect(self._handle_scriptMakeButton)

        self._analysis_list_reload()

    def _analysis_list_reload(self, preferred_analysis=""):
        self.ui.analysisListTreeWidget.blockSignals(True)
        self.ui.analysisListTreeWidget.clear()
        self.ui.analysisListTreeWidget.blockSignals(False)
        to_select = None
        workspace_path = self.config.get_path()
        for name in sorted(os.listdir(workspace_path)):
            name_path = os.path.join(workspace_path, name)
            if not os.path.isdir(name_path):
                continue
            if name == GEOMOP_INTERNAL_DIR_NAME:
                continue
            row = QtWidgets.QTreeWidgetItem(self.ui.analysisListTreeWidget)
            row.setText(0, name)
            if Analysis.is_analysis(name_path):
                if name == preferred_analysis or not to_select:
                    to_select = row
            else:
                row.setFlags(QtCore.Qt.NoItemFlags)

        self.ui.analysisListTreeWidget.resizeColumnToContents(0)

        if to_select:
            self.ui.analysisListTreeWidget.setCurrentItem(to_select)

    def _show_analysis(self):
        self.set_data(self.analysis)

    def _is_data_changed(self):
        sel_file = ""
        for file in self.analysis.files:
            if file.selected:
                sel_file = file.file_path
                break
        if sel_file != self.ui.flowInputComboBox.currentText():
            return True

        sel_file = ""
        for file in self.analysis.layers_files:
            if file.selected:
                sel_file = file.file_path
                break
        if sel_file != self.ui.layersFileComboBox.currentText():
            return True

        sel_file = ""
        for file in self.analysis.script_files:
            if file.selected:
                sel_file = file.file_path
                break
        if sel_file != self.ui.scriptComboBox.currentText():
            return True

        if self.analysis.flow123d_version != self.ui.flowVersionComboBox.currentText():
            return True

        return False

    def _handle_item_changed(self):
        currentItem = self.ui.analysisListTreeWidget.currentItem()
        if currentItem:
            if self.analysis and self._is_data_changed():
                if not self._confirm_save():
                    self.ui.analysisListTreeWidget.blockSignals(True)
                    self.ui.analysisListTreeWidget.setCurrentItem(self.last_selected)
                    self.ui.analysisListTreeWidget.blockSignals(False)
                    return
            analysis_name = currentItem.text(0)
            self.analysis = None
            try:
                self.analysis = Analysis.open(self.config.get_path(), analysis_name, sync_files=True)
            except InvalidAnalysis:
                QtWidgets.QMessageBox.critical(
                    self, 'Analysis not found',
                    'Analysis "{}" was not found in the current workspace.'.format(analysis_name))
            self._show_analysis()
            self.last_selected = currentItem

    def _handle_add_analysis_action(self):
        if self.analysis and self._is_data_changed():
            if not self._confirm_save():
                return
            self._update_files(False)

        dialog = AddAnalysisDialog(self, config=self.config)
        if dialog.exec():
            self._analysis_list_reload(dialog.analysis_name)

    def _handle_save_analysis_action(self):
        self.analysis.flow123d_version = self.ui.flowVersionComboBox.currentText()

        # set selected files
        for file in self.analysis.files:
            file.selected = file.file_path == self.ui.flowInputComboBox.currentText()

        for file in self.analysis.layers_files:
            file.selected = file.file_path == self.ui.layersFileComboBox.currentText()

        for file in self.analysis.script_files:
            file.selected = file.file_path == self.ui.scriptComboBox.currentText()

        self.analysis.save()

    def _handle_restore_analysis_action(self):
        self._update_files(False)

    def _handle_close_action(self):
        self.reject()

    def _confirm_save(self):
        """Return True if it is possible to continue."""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Analyses")
        msg.setText('Analysis "{}" has been changed.\n'
                    "Do you want to save it?".format(self.analysis.name))
        msg.setStandardButtons(QtWidgets.QMessageBox.Save |
                               QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Reset)
        msg.button(QtWidgets.QMessageBox.Discard).setText("Discard changes")
        msg.button(QtWidgets.QMessageBox.Reset).setText("Keep record")
        msg.setDefaultButton(QtWidgets.QMessageBox.Save)
        ret = msg.exec()
        if ret == QtWidgets.QMessageBox.Save:
            self._handle_save_analysis_action()
            return True
        elif ret == QtWidgets.QMessageBox.Reset:
            return False
        return True

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
        flow_version = self.ui.flowVersionComboBox.currentText()
        if flow_input_file == "" or flow_version == "":
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Warning")
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText("First select Flow123d input file and version.")
            msg_box.exec()
            return
        script = (
            "gen = VariableGenerator(Variable=Struct())\n"
            "flow = Flow123dAction(Inputs=[gen], YAMLFile='{}', Executable='flow123d_{}')\n"
            "pipeline = Pipeline(ResultActions=[flow])\n"
        ).format(flow_input_file, flow_version)

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

    def _update_files(self, keep_selected = True):
        """Update comboboxes according to actual directory content and version."""
        # keep selected files
        if keep_selected:
            flowInputText = self.ui.flowInputComboBox.currentText()
            layersFileText = self.ui.layersFileComboBox.currentText()
            scriptText = self.ui.scriptComboBox.currentText()
            flowVersionText = self.ui.flowVersionComboBox.currentText()
        else:
            flowInputText = ""
            layersFileText = ""
            scriptText = ""
            flowVersionText = ""

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

        # select version
        ind = self.ui.flowVersionComboBox.findText(flowVersionText)
        if ind < 0:
            ind = self.ui.flowVersionComboBox.findText(self.analysis.flow123d_version)
            if ind < 0:
                ind = 0
        self.ui.flowVersionComboBox.setCurrentIndex(ind)

    def set_data(self, data=None):
        if data:
            self._update_files(False)

            analysis = data
            self.ui.nameValueLabel.setText(analysis.name)
            self.ui.dirPathLabel.setText(analysis.analysis_dir)
            self.analysis_edit_enable(True)
        else:
            self.ui.nameValueLabel.clear()
            self.ui.dirPathLabel.clear()
            self.ui.flowInputComboBox.clear()
            self.ui.layersFileComboBox.clear()
            self.ui.scriptComboBox.clear()
            self.analysis_edit_enable(False)

    def analysis_edit_enable(self, enable=True):
        self.ui.nameValueLabel.setEnabled(enable)
        self.ui.flowInputComboBox.setEnabled(enable)
        self.ui.flowVersionComboBox.setEnabled(enable)
        self.ui.layersFileComboBox.setEnabled(enable)
        self.ui.scriptComboBox.setEnabled(enable)
        self.ui.layersFileEditButton.setEnabled(enable)
        self.ui.flowInputEditButton.setEnabled(enable)
        self.ui.scriptMakeButton.setEnabled(enable)
        self.ui.refreshButton.setEnabled(enable)
        self.ui.btnSave.setEnabled(enable)
        self.ui.btnRestore.setEnabled(enable)

    def reject(self):
        if self.analysis and self._is_data_changed():
            if not self._confirm_save():
                return

        super().reject()


class UiAnalysisDialog:
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        # dialog properties
        dialog.setModal(True)

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.mainVerticalLayoutWidget.setObjectName("mainVerticalLayoutWidget")
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.mainVerticalLayoutWidget)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")

        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 5, 0, 5)

        # add form to main layout
        self.mainVerticalLayout.addLayout(self.formLayout)

        # dialog properties
        dialog.resize(680, 510)

        # name
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.nameValueLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameValueLabel.setObjectName("nameValueLabel")
        self.formLayout.addRow(self.nameLabel, self.nameValueLabel)

        # directory
        self.dirLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.dirLabel.setObjectName("dirLabel")
        self.dirLabel.setText("Directory:")
        self.dirPathLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.dirPathLabel.setObjectName("dirPathLabel")
        self.formLayout.addRow(self.dirLabel, self.dirPathLabel)

        # separator
        sep = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        sep.setText("")
        self.formLayout.addRow(sep)

        # layers file
        self.layersFileLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.layersFileLabel.setText("Layers file:")
        self.layersFileComboBox = QtWidgets.QComboBox(self.mainVerticalLayoutWidget)
        self.layersFileComboBox.setMinimumWidth(150)
        self.layersFileEditButton = QtWidgets.QPushButton()
        self.layersFileEditButton.setText("Edit")
        self.layersFileEditButton.setIcon(icon.get_app_icon("le-geomap"))
        self.layersFileEditButton.setToolTip('Edit in Layer Editor')
        self.layersFileEditButton.setMaximumWidth(100)
        self.layersFileEditButton.setMinimumWidth(100)
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
        self.flowInputEditButton.setMinimumWidth(100)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.flowInputComboBox)
        layout.addWidget(self.flowInputEditButton)
        self.formLayout.addRow(self.flowInputLabel, layout)

        # flow version
        self.flowVersionLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.flowVersionLabel.setText("Flow123d version:")
        self.flowVersionComboBox = QtWidgets.QComboBox(self.mainVerticalLayoutWidget)
        self.flowVersionComboBox.addItems(FLOW123D_VERSION_LIST)
        sep = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        sep.setMaximumWidth(100)
        sep.setMinimumWidth(100)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.flowVersionComboBox)
        layout.addWidget(sep)
        self.formLayout.addRow(self.flowVersionLabel, layout)

        # script file
        self.scriptLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.scriptLabel.setText("Analysis script:")
        self.scriptComboBox = QtWidgets.QComboBox(self.mainVerticalLayoutWidget)
        self.scriptMakeButton = QtWidgets.QPushButton()
        self.scriptMakeButton.setText("Make script")
        self.scriptMakeButton.setToolTip('Generate default Flow execution')
        self.scriptMakeButton.setMaximumWidth(100)
        self.scriptMakeButton.setMinimumWidth(100)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.scriptComboBox)
        layout.addWidget(self.scriptMakeButton)
        self.formLayout.addRow(self.scriptLabel, layout)

        self.refreshButton = QtWidgets.QPushButton()
        self.refreshButton.setText("Refresh files")
        self.refreshButton.setToolTip('Refresh files according to actual directory content.')
        self.refreshButton.setMaximumWidth(120)
        self.mainVerticalLayout.addWidget(self.refreshButton)

        spacerItem = QtWidgets.QSpacerItem(10, 100,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.mainVerticalLayout.addItem(spacerItem)

        self.mainVerticalLayout.addStretch(1)

        # analysis list tree widget
        self.analysisListTreeWidget = QtWidgets.QTreeWidget(dialog)
        self.analysisListTreeWidget.setAlternatingRowColors(True)
        self.analysisListTreeWidget.setHeaderLabels(["Name"])
        self.analysisListTreeWidget.setSortingEnabled(True)
        self.analysisListTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

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

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addWidget(self.analysisListTreeWidget)
        self.horizontalLayout.addWidget(self.mainVerticalLayoutWidget)

        self.superMainVerticalLayout = QtWidgets.QVBoxLayout(dialog)
        self.superMainVerticalLayout.addLayout(self.horizontalLayout)
        self.superMainVerticalLayout.addLayout(self.buttonLayout)
        dialog.setLayout(self.superMainVerticalLayout)

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


#FLOW123D_VERSION_LIST = list_flow123d_versions()
FLOW123D_VERSION_LIST = ["2.2.0", "3.0.0", "3.1.0"]
