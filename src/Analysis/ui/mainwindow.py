"""Main Qt window.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from ui import panels

class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, model_editor):
        """Initialize the class."""
        super(MainWindow, self).__init__()

        self.setMinimumSize(960, 660)

        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self._model_editor = model_editor
        self.setCentralWidget(self._hsplitter)
        # splitters
        self._vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)
        self.diagramScene = panels.Diagram(self._vsplitter)
        self.diagramView =QtWidgets.QGraphicsView(self.diagramScene,self._vsplitter)
        
        self.diagramView.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding))
        self.diagramView.setMinimumSize(QtCore.QSize(500, 500))
 

        self._hsplitter.insertWidget(0, self.diagramView)
