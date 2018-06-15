"""Module contains an edit menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QAction

from gm_base.geomop_dialogs import AnalysisDialog
from gm_base.geomop_analysis import Analysis, InvalidAnalysis


class AnalysisMenu(QMenu):
    """Menu with analyses."""

    def __init__(self, parent, config, title='&Analysis', flow123d_versions=None):
        """Initializes the class."""
        super(AnalysisMenu, self).__init__(parent)
        self.flow123d_versions = flow123d_versions
        self.config = config
        self.analysis_name = None
        self._actions = []
        self._create_analysis_action = QAction('&Create', self)
        self._create_analysis_action.triggered.connect(self._create_analysis)
        self._analysis_settings_action = QAction('&Edit', self)
        self._analysis_settings_action.triggered.connect(self._show_analysis_settings)
        self.addAction(self._create_analysis_action)
        self.addAction(self._analysis_settings_action)
        self.setTitle(title)

    def _create_analysis(self):
        """Handle creation of a new analysis."""
        if self.config.get_path() is None:
            QtWidgets.QMessageBox.information(
                self, 'No Workspace',
                'Please select workspace in Settings before creating an analysis.')
        else:
            dialog = AnalysisDialog(self, AnalysisDialog.PURPOSE_ADD,
                           config=self.config)            
            if QtWidgets.QDialog.Accepted == dialog.exec_():
                self.config.save(0, dialog.analysis.name)

    def _show_analysis_settings(self):
        """Show analysis settings dialog."""
        # get analysis to edit
        dialog = AnalysisSelectDialog(self, self.config)
        if dialog.exec_():
            try:
                analysis = Analysis.open(self.config.get_path(), dialog.analysis_name, sync_files=True)
            except InvalidAnalysis:
                QtWidgets.QMessageBox.critical(
                        self, 'Analysis not found',
                        'Analysis "{an_name}" was not found in the current workspace.'.format(
                            an_name=self.analysis_name)
                    )
            else:
                AnalysisDialog(self, AnalysisDialog.PURPOSE_EDIT,
                               config=self.config,
                               analysis=analysis).exec_()


class AnalysisSelectDialog(QtWidgets.QDialog):
    def __init__(self, parent, config):
        """Initializes the class."""
        super(AnalysisSelectDialog, self).__init__(parent)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)

        button_box.accepted.connect(self.accept)

        form_layout = QtWidgets.QFormLayout()
        analysis_label = QtWidgets.QLabel("Analysis: ")
        self.analysis_combo_box = QtWidgets.QComboBox()
        self.analysis_combo_box.addItems(Analysis.list_analyses_in_workspace(config.get_path()))
        self.analysis_combo_box.setCurrentIndex(0)
        form_layout.addRow(analysis_label, self.analysis_combo_box)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowTitle('Select analysis')
        #self.setMinimumSize(ChangeISTDialog.MINIMUM_WIDTH, ChangeISTDialog.MINIMUM_HEIGHT)

    def accept(self):
        """Handles a confirmation."""
        self.analysis_name = self.analysis_combo_box.currentText()
        super(AnalysisSelectDialog, self).accept()

