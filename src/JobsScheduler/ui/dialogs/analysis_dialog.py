"""Analysis dialog.
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5 import QtWidgets, QtGui

from geomop_project import Analysis

from .dialogs import AFormDialog, UiFormDialog


class AnalysisDialog(AFormDialog):
    """
    Analysis dialog.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddAnalysisDialog",
                       windowTitle="Job Scheduler - Add new Analysis",
                       title="Add new Analysis",
                       subtitle="Please select details for new Analysis.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditAnalysisDialog",
                        windowTitle="Job Scheduler - Edit Analysis",
                        title="Edit Analysis",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyAnalysis",
                        windowTitle="Job Scheduler - Copy Analysis",
                        title="Copy Analysis",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, project=None):
        super().__init__(parent)

        assert project is not None, "No project provided for analysis"
        self.project = project

        # setup specific UI
        self.ui = UiAnalysisDialog()
        self.ui.setup_ui(self)

        # preset purpose
        analysis = project.get_current_analysis()
        if analysis is not None:
            self.set_data(analysis)
            self.set_purpose(self.PURPOSE_EDIT)
        else:
            self.set_purpose(self.PURPOSE_ADD)

        # connect slots
        super()._connect_slots()

    def valid(self):
        valid = True
        return valid

    def get_data(self):
        files = []
        params = {}

        # get all files
        for i in range(self.ui.filesLayout.count()):
            checkbox = self.ui.filesLayout.itemAt(i).widget()
            if checkbox.isChecked():
                files.append(checkbox.file.file_path)

        # get all params
        for i in range(self.ui.paramsLayout.count()):
            widget = self.ui.paramsLayout.itemAt(i).widget()
            if widget.include_in_data:
                params[widget.param.name] = widget.text()

        analysis = Analysis(files=files,
                            params=params)
        return analysis.__dict__

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


class UiAnalysisDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        self.project = dialog.project

        # form layout

        # row 0

        self.dirLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.dirLabel.setObjectName("dirLabel")
        self.dirLabel.setText("Project Directory:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.dirLabel)
        self.dirPathLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.dirPathLabel.setObjectName("dirPathLabel")
        self.dirPathLabel.setText(self.project.project_dir)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.dirPathLabel)

        # remove button box
        self.mainVerticalLayout.removeWidget(self.buttonBox)

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

        for file in self.project.files:
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

        # create GUI components for all project params
        self.paramWidgets = []
        for i, param in enumerate(self.project.params):
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
