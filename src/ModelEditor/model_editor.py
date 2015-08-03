"""Start script that inicialize main window """

import sys
sys.path.insert(1, '../lib')
import os
from data.meconfig import MEConfig as cfg
from dialogs.json_editor import JsonEditorDlg
import panels.yaml_editor
import panels.tree
import panels.info_panel
import panels.error_tab
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from data.data_node import Position

class ModelEditor:
    """Model editor main class"""

    def __init__(self):
        #main window
        self._app = QtWidgets.QApplication(sys.argv)
        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._mainwindow = QtWidgets.QMainWindow()
        self._mainwindow.setCentralWidget(self._hsplitter)

        #load config
        cfg.init(self._mainwindow)
        self._update_document_name()

        #menu
        #file
        menubar = self._mainwindow.menuBar()
        self._file_menu = menubar.addMenu('&File')

        self._new_file_action = QtWidgets.QAction(
            '&New File ...', self._mainwindow)
        self._new_file_action.setShortcut('Ctrl+N')
        self._new_file_action.setStatusTip('New model yaml file')
        self._new_file_action.triggered.connect(self._new_file)
        self._file_menu.addAction(self._new_file_action)

        self._open_file_action = QtWidgets.QAction(
            '&Open File ...', self._mainwindow)
        self._open_file_action.setShortcut('Ctrl+O')
        self._open_file_action.setStatusTip('Open model yaml file')
        self._open_file_action.triggered.connect(self._open_file)
        self._file_menu.addAction(self._open_file_action)

        self._save_file_action = QtWidgets.QAction(
            '&Save File', self._mainwindow)
        self._save_file_action.setShortcut('Ctrl+S')
        self._save_file_action.setStatusTip('Save model yaml file')
        self._save_file_action.triggered.connect(self._save_file)
        self._file_menu.addAction(self._save_file_action)

        self._save_as_action = QtWidgets.QAction(
            'Save &As ...', self._mainwindow)
        self._save_as_action.setShortcut('Ctrl+A')
        self._save_as_action.setStatusTip('Save model yaml file as')
        self._save_as_action.triggered.connect(self._save_as)
        self._file_menu.addAction(self._save_as_action)

        self._recent_file_signal_connect = False
        self._recent = self._file_menu.addMenu('Open &Recent Files')
        self._recent_group = QtWidgets.QActionGroup(
            self._mainwindow, exclusive=True)
        self._update_recent_files(0)
        
        self._file_menu.addSeparator()
        
        self._import_file_action = QtWidgets.QAction(
            '&import File ...', self._mainwindow)
        self._import_file_action.setShortcut('Ctrl+I')
        self._import_file_action.setStatusTip('Import model from old con formated file')
        self._import_file_action.triggered.connect(self._import_file)
        self._file_menu.addAction(self._import_file_action)
        
        self._file_menu.addSeparator()

        self._exit_action = QtWidgets.QAction('&Exit', self._mainwindow)
        self._exit_action.setShortcut('Ctrl+Q')
        self._exit_action.setStatusTip('Exit application')
        self._exit_action.triggered.connect(QtWidgets.qApp.quit)
        self._file_menu.addAction(self._exit_action)

        #Settings
        self._settings_menu = menubar.addMenu('&Settings')
        self._format = self._settings_menu.addMenu('&Format')
        self._format_group = QtWidgets.QActionGroup(
            self._mainwindow, exclusive=True)
        for frm in cfg.format_files:
            faction = self._format_group.addAction(QtWidgets.QAction(
                frm, self._mainwindow, checkable=True))
            faction.setStatusTip('Choose format file for current document')
            self._format.addAction(faction)
            faction.setChecked(cfg.curr_format_file == frm)
        self._format_group.triggered.connect(self._format_checked)
        
        self._format.addSeparator()
        
        self._edit_format_action = QtWidgets.QAction(
            '&Edit Format File ...', self._mainwindow)
        self._edit_format_action.setShortcut('Ctrl+E')
        self._edit_format_action.setStatusTip('Edit format file in Json Editor')
        self._edit_format_action.triggered.connect( self._edit_format)
        self._format.addAction(self._edit_format_action)
        
        self._transformation = self._settings_menu.addMenu('&Transformation')
        pom_lamda = lambda name: lambda: self._transform(name)
        for frm in cfg.transformation_files:
            faction = QtWidgets.QAction(frm + " ...", self._mainwindow)
            faction.setStatusTip('Transfor format of current document')
            self._transformation.addAction(faction)
            faction.triggered.connect(pom_lamda(frm))
            
        self._edit_transformation = self._settings_menu.addMenu('&Edit Transformation Rules')
        pom_lamda = lambda name: lambda: self._edit_transformation_file(name)
        for frm in cfg.transformation_files:
            faction = QtWidgets.QAction(frm, self._mainwindow)
            faction.setStatusTip('Open transformation file')
            self._edit_transformation.addAction(faction)
            faction.triggered.connect(pom_lamda(frm))
        
        #tab
        self._tab = QtWidgets.QTabWidget()
        self._info = panels.info_panel.InfoPanelWidget()        
        self._err = panels.error_tab.ErrorWidget()
        self._tab.addTab(self._info,"Structure Info");  
        self._tab.addTab(self._err,"Messages");

        #spliters
        self._vsplitter = QtWidgets.QSplitter(
            QtCore.Qt.Vertical, self._hsplitter)
        self._editor = panels.yaml_editor.YamlEditorWidget(self._vsplitter)       
        self._tree = panels.tree.TreeWidget()
        self._vsplitter.addWidget(self._editor)
        self._vsplitter.addWidget(self._tab)
        self._hsplitter.insertWidget(0, self._tree)

        # status bar
        self._column = QtWidgets.QLabel()
        self._column.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self._status = self._mainwindow.statusBar()
        self._status.setSizeGripEnabled(False)
        self._status.addPermanentWidget(self._column)
        self._status.showMessage("Ready", 5000)
        
        # signals
        self._err.itemSelected.connect(self._item_selected)
        self._tree.itemSelected.connect(self._item_selected)
        self._editor.nodeChanged.connect(self._node_changed)
        self._editor.cursorChanged.connect(self._cursor_changed)
        self._editor.structureChanged.connect(self._structure_changed)
        self._editor.errorMarginClicked.connect(self._error_margin_clicked)
        #show
        self._mainwindow.show()
        self._editor.setFocus()
    
    def _cursor_changed(self, line, column):
        """Editor node change signal"""
        self._column.setText("Line: {:5d}  Pos: {:3d}".format(line, column))
    
    def _node_changed(self, line, column):
        """Editor node change signal"""
        self._reload_node(line, column)
        
    def _structure_changed(self, line, column):
        """Editor structure change signal"""
        if cfg.update_yaml_file(self._editor.text()):
            self._reload()
        else:
            self._reload_node(line, column)            
    
    def _item_selected(self, start_column, start_row, end_column, end_row):
        """Click tree item action mark relative arrea in editor"""
        self._editor.setFocus()
        self._editor.mark_selected(start_column, start_row, end_column, end_row)

    def _error_margin_clicked(self, line):
        """Click error icon in margin"""
        self._tab.setCurrentIndex(self._tab.indexOf(self._err))
        self._err.select_error(line)

    def _reload(self):
        """reload panels after structure changes"""
        cfg.update()
        self._editor.reload()
        self._tree.reload()
        self._err. reload()
        line, index = self._editor.getCursorPosition()
        self._reload_node(line+1, index+1)
        self._status.showMessage("Document structure is reloaded", 5000)

    def _reload_node(self, line, index):
        """reload info after changing node selection"""
        node = cfg.get_data_node(Position(line, index))
        self._editor.set_new_node(node)
        if node is not None:
            self._info.setHtml(node.info_text)
        
    def _new_file(self):
        """new file menu action"""
        if not self._save_old_file():
            return
        cfg.new_file()
        self._reload()
        self._update_recent_files(0)
        self._update_document_name()
        self._status.showMessage("New file is opened", 5000)

    def _open_file(self):
        """open file menu action"""
        if not self._save_old_file():
            return
        yaml_file = QtWidgets.QFileDialog.getOpenFileName(
            self._mainwindow, "Choose Yaml Model File",
            cfg.config.last_data_dir, "Yaml Files (*.yaml)")
        if yaml_file[0]:
            cfg.open_file(yaml_file[0])
            self._reload()
            self._update_recent_files()
            self._update_document_name()
            self._status.showMessage("File '" + yaml_file[0] +"' is opened", 5000)

    def _import_file(self):
        """import con file menu action"""
        if not self._save_old_file():
            return
        con_file = QtWidgets.QFileDialog.getOpenFileName(
            self._mainwindow, "Choose Con Model File",
            cfg.config.last_data_dir, "Con Files (*.con)")
        if con_file[0]:
            cfg.import_file(con_file[0])
            self._reload()
            self._update_recent_files()
            self._update_document_name()
            self._status.showMessage("File '" + con_file[0] +"' is imported", 5000)

    def _open_recent(self, action):
        """open recent file menu action"""
        if action.text() == cfg.curr_file:
            return
        if not self._save_old_file():
            return
        cfg.open_recent_file(action.text())
        self._reload()
        self._update_recent_files()
        self._update_document_name()
        self._status.showMessage("File '" + action.text() +"' is opened", 5000)

    def _save_file(self):
        """save file menu action"""
        if cfg.curr_file == None:
            return self._save_as()
        cfg.update_yaml_file(self._editor.text())
        cfg.save_file()
        self._status.showMessage("File is saved", 5000)

    def _save_as(self):
        """save file menu action"""
        cfg.update_yaml_file(self._editor.text())
        if cfg.curr_file == None:
            new_file = cfg.config.last_data_dir + os.path.sep + "NewFile.yaml"
        else:
            new_file = cfg.curr_file
        yaml_file = QtWidgets.QFileDialog.getSaveFileName(
            self._mainwindow, "Set Yaml Model File",
            new_file, "Yaml Files (*.yaml)")

        if yaml_file[0]:
            cfg.save_as(yaml_file[0])
            self._update_recent_files()
            self._update_document_name()
            self._status.showMessage("File is saved", 5000)
            return True
        return False

    def _transform(self,  file):
        """Run transformation accoding rules in set file"""
        cfg.update_yaml_file(self._editor.text())
        cfg.transform( file)
        self._reload()
        
    def _edit_transformation_file(self,  file):
        """edit transformation rules in file"""
        text=cfg.get_transformation_text(file)
        if text is not None:
            import data.meconfig
            dlg = JsonEditorDlg(data.meconfig.__transformation_dir__, file, 
                                "Transformation rules:", text, self._mainwindow )
            dlg.exec_()

    def _format_checked(self):
        """format checked file menu action"""
        action = self._format_group.checkedAction()
        if cfg.curr_format_file == action.text():
            return
        cfg.curr_format_file = action.text()
        cfg.update_format()
        self._reload()
        self._status.showMessage("Format of file is changed", 5000)

    def  _edit_format(self):
        """Open selected format file in Json Editor"""
        text=cfg.get_curr_format_text()
        if text is not None:
            import data.meconfig
            dlg = JsonEditorDlg(data.meconfig.__format_dir__, cfg.curr_format_file, 
                                            "Format", text, self._mainwindow )
            dlg.exec_()

    def _update_recent_files(self, from_row=1):
        """update recent file in menu"""
        if self._recent_file_signal_connect:
            self._recent_group.triggered.disconnect()
            self._recent_file_signal_connect = False
        for action in  self._recent_group.actions():
            self._recent_group.removeAction(action)
        if len(cfg.config.recent_files) < from_row+1:
            self._recent.setEnabled(False)
            return
        self._recent.setEnabled(True)
        for i in range(from_row, len(cfg.config.recent_files)):
            raction = self._recent_group.addAction(QtWidgets.QAction(
                cfg.config.recent_files[i], self._mainwindow, checkable=True))
            self._recent.addAction(raction)
        self._recent_group.triggered.connect(self._open_recent)
        self._recent_file_signal_connect = True

    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Model Editor"
        if cfg.curr_file == None:
            title += " - New File"
        else:
            title += " - " + cfg.curr_file
        self._mainwindow.setWindowTitle(title)

    def _save_old_file(self):
        """
        If file not saved, display confirmation dialeg and if is needed, do it

        return: False if action have to be aborted
        """
        cfg.update_yaml_file(self._editor.text())
        if cfg.changed:
            reply = QtWidgets.QMessageBox.question(
                self._mainwindow, 'Comfirmation',
                "The document has unsaved changes, do you want to save it?",
                (QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                 QtWidgets.QMessageBox.Abort))
            if reply == QtWidgets.QMessageBox.Abort:
                return False
            if reply == QtWidgets.QMessageBox.Yes:
                if cfg.curr_file == None:
                    return self._save_as()
                else:
                    self._save_file()
        return True

    def main(self):
        """go"""
        self._app.exec_()

if __name__ == "__main__":
    ModelEditor().main()
