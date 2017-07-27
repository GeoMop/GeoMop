"""Main Qt window.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from ui import panels
from leconfig import cfg
from ui.menus.tools import ToolsMenu
from ui.menus.edit import EditMenu
from ui.menus.file import MainFileMenu
import icon

class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, layer_editor):
        """Initialize the class."""
        super(MainWindow, self).__init__()
        self._layer_editor = layer_editor

        self.setMinimumSize(960, 660)

       # splitters
        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.setCentralWidget(self._hsplitter)
        self._vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)
        self._vsplitter.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)        

        # left pannels
        self.layers = panels.Layers(self._vsplitter)
        self._vsplitter.addWidget(self.layers)        
        self.shp = panels.ShpFiles(cfg.diagram.shp, self._vsplitter)
        self._vsplitter.addWidget(self.shp)     
        if cfg.diagram.shp.is_empty():
            self.shp.hide()   
        
        # scene
        self.diagramScene = panels.Diagram(self._hsplitter)
        self.diagramView =QtWidgets.QGraphicsView(self.diagramScene,self._hsplitter)
        self.diagramView.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.diagramView.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.diagramView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.diagramView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  
        self.diagramView.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self._hsplitter.addWidget(self.diagramView) 
        
        self._hsplitter.setSizes([300, 760])
        
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
        self.shp.background_changed.connect(self.background_changed)
        self.shp.item_removed.connect(self.del_background_item)
        self.layers.viewInterfacesChanged.connect(self.refresh_view_data)
        self.layers.editInterfaceChanged.connect(self.refresh_curr_data)

    def refresh_all(self):
        """For new data"""
        self.diagramScene.set_data()
        self.refresh_view_data()

    def paint_new_data(self):
        """Propagate new diagram scene to canvas"""
        self.diagramScene.set_data()
        self.display_all()
        
    def refresh_curr_data(self, old_i, new_i):
        """Propagate new diagram scene to canvas"""
        if old_i == new_i:
            return        
        self.refresh_view_data(old_i)
        self.refresh_view_data(new_i)
        self.diagramScene.release_data(old_i)
        self.diagramScene.set_data()        
        
    def refresh_view_data(self, i):
        """Propagate new views (static, not edited diagrams) 
        scene to canvas. i is changed view."""
        self.diagramScene.update_view(i)
        
    def refresh_diagram_shp(self):
        """refresh diagrams shape files background layer"""
        self.diagramScene.refresh_shp_backgrounds()
        if not cfg.diagram.shp.is_empty():
            if not self.shp.isVisible(): 
                self.shp.show()
            self.shp.reload()
        else:
            self.shp.hide()            
                
        if cfg.diagram.first_shp_object():
            self.display_all()
        else:
            self._move()
        
    def _cursor_changed(self, x, y):
        """Editor node change signal"""
        self._column.setText("x: {:5f}  y: {:5f}".format(x, -y))
        
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
        
    def background_changed(self):
        """Background display shapefile paramaters was changed and
        shp items should be repainted"""
        self.diagramScene.refresh_shp_backgrounds()
        
    def del_background_item(self,  idx_item):
        """Remove backgroun item"""
        obj = cfg.diagram.shp.datas[idx_item].shpdata.object
        obj.release_background()        
        self.diagramScene.removeItem(obj)
        del cfg.diagram.shp.datas[idx_item]
    
