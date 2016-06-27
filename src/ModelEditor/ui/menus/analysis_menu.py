"""Module contains an edit menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QAction

from geomop_dialogs import AnalysisDialog
from geomop_analysis import Analysis


class AnalysisMenu(QMenu):
    """Menu with analyses."""

    def __init__(self, parent, config, title='&Analysis', flow123d_versions=None):
        """Initializes the class."""
        super(AnalysisMenu, self).__init__(parent)
        self.flow123d_versions = flow123d_versions
        self.config = config
        self._group = QtWidgets.QActionGroup(self, exclusive=True)
        self._group.triggered.connect(self._analysis_selected)
        self._actions = []
        self._create_analysis_action = QAction('&Create', self)
        self._create_analysis_action.triggered.connect(self._create_analysis)
        self._analysis_settings_action = QAction('&Edit', self)
        self._analysis_settings_action.triggered.connect(self._show_analysis_settings)
        self.addAction(self._create_analysis_action)
        self.addAction(self._analysis_settings_action)
        self.addSeparator()
        self.aboutToShow.connect(self.reload_analysis)
        self.setTitle(title)

    def reload_analysis(self):
        """Reload all analysis from current workspace."""
        # remove old actions
        for action in self._actions:
            self.removeAction(action)
            self._group.removeAction(action)
        self._actions = []
        # find analyses in workspace
        if not self.config.workspace:
            return
        for analysis_name in Analysis.list_analyses_in_workspace(self.config.workspace):
            action = QtWidgets.QAction(analysis_name, self, checkable=True)
            action.setChecked(self.config.analysis == analysis_name)
            self.addAction(action)
            self._group.addAction(action)
            self._actions.append(action)

        for action in self._actions:
            self.addAction(action)

    def _analysis_selected(self):
        """Handle analysis selection."""
        action = self._group.checkedAction()
        self.config.analysis = action.text()
        self.config.save()

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
        if Analysis.current is None:
            QtWidgets.QMessageBox.information(
                self, 'No Analysis',
                'Please select analysis to edit.')
        else:
            AnalysisDialog(self, AnalysisDialog.PURPOSE_EDIT,
                           config=self.config,
                           analysis=Analysis.current).exec_()
