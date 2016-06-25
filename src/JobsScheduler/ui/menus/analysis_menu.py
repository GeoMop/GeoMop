"""Module contains an edit menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QAction

from geomop_dialogs import AnalysisDialog
from geomop_analysis import Analysis, InvalidAnalysis


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
        if not self.config.workspace:
            QtWidgets.QMessageBox.information(
                self, 'No Workspace',
                'Please select workspace in Settings before creating an analysis.')
        else:
            AnalysisDialog(self, AnalysisDialog.PURPOSE_ADD,
                           config=self.config).exec_()

    def _show_analysis_settings(self):
        """Show analysis settings dialog."""
        try:
            analysis = Analysis.open(self.config.workspace, self.analysis_name)
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
