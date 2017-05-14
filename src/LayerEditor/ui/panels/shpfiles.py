"""
Tree widget panel

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

class ShpFiles(QtWidgets.QTableWidget):
    """Widget displays the config file structure in table.

    pyqtSignals:
        * :py:attr:`background_changed() <itemSelected>`
    """

    background_changed = QtCore.pyqtSignal()
    """Signal is sent whenbackground settings was changes.
    """

    def __init__(self, data, parent=None):
        """Initialize the class."""
        super(ShpFiles, self).__init__(parent)
        
        self.data = data
        self.setMinimumSize(250, 400)
        self.setMaximumWidth(450)
        self.setColumnCount(3)
        
        labels = ['File/Attr. value', 'Show',  'Set off']
        self.setHorizontalHeaderLabels(labels)


    def reload(self):
        """Start of reload data from config."""
        pass
