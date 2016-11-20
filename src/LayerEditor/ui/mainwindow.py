"""Main Qt window.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from ui import panels
from ui import data
import icon

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
        
        diagram = data.Diagram()
        self.diagramScene = panels.Diagram(diagram, self._vsplitter)
        self.diagramView =QtWidgets.QGraphicsView(self.diagramScene,self._vsplitter)
        self.diagramView.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.diagramView.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.diagramView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.diagramView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        
        #self.diagramView.setSizePolicy(
        #    QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
        #    QtWidgets.QSizePolicy.Expanding))
       # self.diagramView.setMinimumSize(QtCore.QSize(500, 500)) 

        self._hsplitter.insertWidget(0, self.diagramView)
        
        # status bar
        self._column = QtWidgets.QLabel(self)
        self._column.setFrameStyle(QtWidgets.QFrame.StyledPanel)

        self._reload_icon = QtWidgets.QLabel(self)
        self._reload_icon.setPixmap(icon.get_pixmap("refresh", 16))
        self._reload_icon.setVisible(False)
        self._reload_icon_timer = QtCore.QTimer(self)
        self._reload_icon_timer.timeout.connect(lambda: self._reload_icon.setVisible(False))

        self._status = self.statusBar()
        self._status.addPermanentWidget(self._reload_icon)
        self._status.addPermanentWidget(self._column)
        self.setStatusBar(self._status)
        self._status.showMessage("Ready", 5000)
        
        # signals        
        self.diagramScene.cursorChanged.connect(self._cursor_changed)
        self.diagramScene.possChanged.connect(self._move)
        
        # self.diagramView.scale(10, 10)
        self.data = None

    def set_diagram_data(self, diagram):
        """Propagate new diagram scene to canvas"""
        self.data = diagram
        self.diagramScene.set_data(diagram)       
        self._move()
        
    def _cursor_changed(self, line, column):
        """Editor node change signal"""
        self._column.setText("x: {:5f}  y: {:5f}".format(line, column))
        
    def _move(self):
        """zooming and moving"""
        view_rect = self.diagramView.rect()
        self.diagramView.setSceneRect(
            self.data.x, 
            self.data.y, 
            view_rect.width()/self.data.zoom, 
            view_rect.height()/self.data.zoom)
        transform = QtGui.QTransform(self.data.zoom, 0, 0, self.data.zoom, 0, 0)
        self.diagramView.setTransform(transform)
