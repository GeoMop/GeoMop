"""Main Qt window.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from ui import panels
from leconfig import cfg
from ui import data
from ui.menus.tools import ToolsMenu
from ui.menus.edit import EditMenu
from ui.menus.file import MainFileMenu
import icon

class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, layer_editor):
        """Initialize the class."""
        super(MainWindow, self).__init__()

        self.setMinimumSize(960, 660)

        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self._layer_editor = layer_editor
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

        if not diagram.shp.is_empty():
            self.shp = panels.ShpFiles(diagram.shp, self._hsplitter)
            self._hsplitter.insertWidget(0, self.shp)
            self.shp.reload()
        
        # Menu bar
        self._menu = self.menuBar()
        self._tools_menu = ToolsMenu(self, self.diagramScene)
        self._edit_menu = EditMenu(self, self.diagramScene)
        self._file_menu = MainFileMenu(self,  layer_editor)
        
        self._menu.addMenu(self._file_menu)
        self._menu.addMenu(self._tools_menu)
        self._menu.addMenu(self._edit_menu)
        
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

    def refresh_diagram_data(self):
        """Propagate new diagram scene to canvas"""
        self.diagramScene.set_data(cfg.diagram)
        self.display_all()
        
    def refresh_diagram_shp(self):
        """refresh diagrams shape files background layer"""
        self.diagramScene.refresh_shp_backgrounds()
        if cfg.diagram.first_shp_object():
            self.display_all()
        else:
            self._move()
        
    def _cursor_changed(self, line, column):
        """Editor node change signal"""
        self._column.setText("x: {:5f}  y: {:5f}".format(line, column))
        
    def _move(self):
        """zooming and moving"""
        view_rect = self.diagramView.rect()
        self._display(view_rect)
    
    def display_all(self):
        """Display all diagram"""
        view_rect = self.diagramView.rect()
        rect = cfg.diagram.rect
        if (view_rect.width()/rect.width())>(view_rect.height()/rect.height()):
            # resize acoording height
            cfg.diagram.zoom = view_rect.height()/rect.height()
            cfg.diagram.y = rect.top()
            cfg.diagram.x = rect.left()+(view_rect.width()/cfg.diagram.zoom-rect.width())/2
        else:
            cfg.diagram.zoom = view_rect.width()/rect.width()
            cfg.diagram.x = rect.left()
            cfg.diagram.y = rect.top()+(view_rect.height()/cfg.diagram.zoom-rect.height())/2
        self._display(view_rect)
        
    def _display(self, view_rect):
        """moving"""
        self.diagramView.setSceneRect(
            cfg.diagram.x, 
            cfg.diagram.y, 
            view_rect.width()/cfg.diagram.zoom, 
            view_rect.height()/cfg.diagram.zoom)
        transform = QtGui.QTransform(cfg.diagram.zoom, 0, 0,cfg.diagram.zoom, 0, 0)
        self.diagramView.setTransform(transform)
    
