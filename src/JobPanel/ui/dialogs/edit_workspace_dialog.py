"""Dialog for setting workspace in settings.
.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""

import os
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from gm_base.geomop_analysis import Analysis

class SetWorkspaceDialog():
    def __init__(self, parent, data, title='Choose workspace'):
        """Initializes the class."""

        self.data = data
        self.value = data.workspaces.get_path()

        if self.value is None:
            curr_dir = ''
        else:
            curr_dir = str(os.path.normpath(self.value))

        sel_dir = QtWidgets.QFileDialog.getExistingDirectory(parent, title, curr_dir)

        if not sel_dir:
            sel_dir = curr_dir
        elif sys.platform == "win32":
            sel_dir = sel_dir.replace('/', '\\')

        self.value = sel_dir

        self.data.reload_workspace(self.value)
        if not Analysis.exists(self.data.workspaces.get_path(), self.data.config.analysis):
            self.data.config.analysis = None
        self.data.config.save()

