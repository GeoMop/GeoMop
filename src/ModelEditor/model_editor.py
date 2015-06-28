"""Start script that inicialize main window """

import sys
sys.path.insert(1, '../lib')

from data.meconfig import MEConfig as cfg
import panels.yaml_editor
import panels.tree
import panels.info_panel
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

class ModelEditor:
    """Model editor main class"""
    
    def __init__(self):        
        #main window
        self._app = QtWidgets.QApplication(sys.argv)
        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._mainwindow = QtWidgets.QMainWindow()
        self._mainwindow.setCentralWidget(self._hsplitter)
        self._mainwindow.setWindowTitle("GeoMop Model Editor")
        
        #load config
        cfg.init(self._mainwindow)
        
        #menu
        #file
        menubar = self._mainwindow.menuBar()
        self._file_menu = menubar.addMenu('&File')
        
        self._open_file_action= QtWidgets.QAction('&Open File ...', self._mainwindow)        
        self._open_file_action.setShortcut('Ctrl+O')
        self._open_file_action.setStatusTip('Open model yaml file')
        self._open_file_action.triggered.connect(self._open_file)
        self._file_menu.addAction(self._open_file_action)
        
        self._save_file_action= QtWidgets.QAction('&Save File', self._mainwindow)        
        self._save_file_action.setShortcut('Ctrl+S')
        self._save_file_action.setStatusTip('Save model yaml file')
        self._save_file_action.triggered.connect(self._save_file)
        self._file_menu.addAction(self._save_file_action)
        
        self._save_as_action= QtWidgets.QAction('Save &As ...', self._mainwindow)        
        self._save_as_action.setShortcut('Ctrl+A')
        self._save_as_action.setStatusTip('Save model yaml file')
        self._save_as_action.triggered.connect(self._save_as)
        self._file_menu.addAction(self._save_as_action)
        
        self._recent = self._file_menu.addMenu('Open &Recent Files')
        self._recent_group = QtWidgets.QActionGroup( self._mainwindow, exclusive=True)
        self._update_recent_files(0)

        self._exit_action = QtWidgets.QAction('&Exit', self._mainwindow)        
        self._exit_action.setShortcut('Ctrl+Q')
        self._exit_action.setStatusTip('Exit application')
        self._exit_action.triggered.connect(QtWidgets.qApp.quit)
        self._file_menu.addAction(self._exit_action)
        
        #Settings
        self._settings_menu = menubar.addMenu('&Settings')
        self._format = self._settings_menu.addMenu('&Format')
        self._format_group = QtWidgets.QActionGroup( self._mainwindow, exclusive=True)
        for format in cfg.format_files:
            fm = self._format_group.addAction(QtWidgets.QAction(format,  self._mainwindow, checkable=True))
            self._format.addAction(fm)
            fm.setChecked( cfg.curr_format_file == format)
        self._format_group.triggered.connect(self._format_checked)   
        
        #spliters
        self._vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)        
        self._editor = panels.yaml_editor.YamlEditorWidget(self._vsplitter)
        self._tree = panels.tree.TreeWidget()
        self._info = panels.info_panel.InfoPanelWidget()
        self._vsplitter.addWidget(self._editor)
        self._vsplitter.addWidget(self._info)
        self._hsplitter.insertWidget(0, self._tree)

        #show
        self._mainwindow.show()

    def _open_file(self):
        """open file menu action"""
        from os.path import expanduser
        home = expanduser("~")
        yaml_file = QtWidgets.QFileDialog.getOpenFileName(
            self._mainwindow, "Choose Yaml Model File", home,"Yaml Files (*.yaml)")
        if yaml_file[0]:
            cfg.open_file(yaml_file[0])
            self._editor.reload()
            self._tree.reload()
            self._update_recent_files

    def _open_recent(self, action):
        """open recent file menu action"""
        cfg.open_file(action.text())
        self._editor.reload()
        self._tree.reload()
        self._update_recent_files

    def _save_file(self):
        """save file menu action"""
        cfg.yaml_text = self._editor.text()
        cfg.save_file()
        
    def _save_as(self):
        """save file menu action"""
        cfg.yaml_text = self._editor.text()
        yaml_file = QtWidgets.QFileDialog.getSaveFileName(
            self._mainwindow, "Set Yaml Model File", cfg.curr_file,"Yaml Files (*.yaml)") 

        if yaml_file[0]:
            cfg.save_as(yaml_file[0]) 
            self._update_recent_files()   
        
    def _format_checked(self):
        """format checked file menu action"""
        action=self._format_group.checkedAction()
        cfg.curr_format_file = action.text()
        cfg.update_format()
        
    def _update_recent_files(self, from_row = 1):
        """update recent file in menu"""
        for action in  self._recent_group.actions():
            self._recent_group.removeAction(action)
        if len(cfg.config.recent_files) < from_row+1:
            self._recent.setEnabled(False)
            return
        self._recent.setEnabled(True)
        for i in range(from_row, len(cfg.config.recent_files)):
            rf = self._recent_group.addAction(QtWidgets.QAction(cfg.config.recent_files[i],  self._mainwindow, checkable=True))
            self._recent.addAction(rf)
        self._recent_group.triggered.connect(self._open_recent)  

    def main(self):
        """go"""        
        self._app.exec_()

if __name__ == "__main__":
    ModelEditor().main()
