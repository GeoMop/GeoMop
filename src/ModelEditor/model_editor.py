"""Start script that inicialize main window """

import os
import sys
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

from data.meconfig import MEConfig as cfg
from ui.dialogs.json_editor import JsonEditorDlg
from ui import panels
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from data import Position
from data import CursorType
import icon
from ui.menus import MainEditMenu, MainFileMenu, MainSettingsMenu


class ModelEditor:
    """Model editor main class"""

    def __init__(self):
        # main window
        self._app = QtWidgets.QApplication(sys.argv)       
        self._mainwindow = QtWidgets.QMainWindow()
        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self._mainwindow)
        self._mainwindow.setCentralWidget(self._hsplitter)        

        # load config
        cfg.init(self._mainwindow)
        self._update_document_name()
        
        # tab
        self._tab = QtWidgets.QTabWidget( self._hsplitter)
        self._info = panels.InfoPanelWidget(self._tab)
        self._err = panels.ErrorWidget(self._tab)
        self._debug_tab = panels.DebugPanelWidget(self._tab)
        self._tab.addTab(self._info, "Structure Info")
        self._tab.addTab(self._err, "Messages")
        self._tab.addTab(self._debug_tab, "Debug")

        # splitters
        self._vsplitter = QtWidgets.QSplitter(
            QtCore.Qt.Vertical, self._hsplitter)
        self._editor = panels.YamlEditorWidget(self._vsplitter)
        self._tree = panels.TreeWidget(self._vsplitter)
        self._vsplitter.addWidget(self._editor)
        self._vsplitter.addWidget(self._tab)
        self._hsplitter.insertWidget(0, self._tree)

        # Menu bar
        menubar = self._mainwindow.menuBar()
        self._file_menu = MainFileMenu(self._mainwindow, self)
        self.update_recent_files(0)
        self._edit_menu = MainEditMenu(self._mainwindow, self._editor)
        self._settings_menu = MainSettingsMenu(self._mainwindow, self)
        menubar.addMenu(self._file_menu)
        menubar.addMenu(self._edit_menu)
        menubar.addMenu(self._settings_menu)

        # status bar
        self._column = QtWidgets.QLabel(self._mainwindow)
        self._column.setFrameStyle(QtWidgets.QFrame.StyledPanel)

        self._reload_icon = QtWidgets.QLabel(self._mainwindow)
        self._reload_icon.setPixmap(icon.get_pixmap("refresh", 16))
        self._reload_icon.setVisible(False)
        self._reload_icon_timer = QtCore.QTimer(self._mainwindow)
        self._reload_icon_timer.timeout.connect(self._hide_reload_icon)

        self._status = self._mainwindow.statusBar()
        self._status.addPermanentWidget(self._reload_icon)
        self._status.addPermanentWidget(self._column)
        self._mainwindow.setStatusBar(self._status)
        self._status.showMessage("Ready", 5000)

        # signals
        self._err.itemSelected.connect(self._item_selected)
        self._tree.itemSelected.connect(self._item_selected)
        self._editor.nodeChanged.connect(self._node_changed)
        self._editor.cursorChanged.connect(self._cursor_changed)
        self._editor.structureChanged.connect(self._structure_changed)
        self._editor.errorMarginClicked.connect(self._error_margin_clicked)
        self._editor.elementChanged.connect(self._on_element_changed)

        # show
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
        """Click tree item action mark relative area in editor"""
        self._editor.setFocus()
        self._editor.mark_selected(start_column, start_row, end_column, end_row)

    def _error_margin_clicked(self, line):
        """Click error icon in margin"""
        self._tab.setCurrentIndex(self._tab.indexOf(self._err))
        self._err.select_error(line)

    def _reload(self):
        """reload panels after structure changes"""
        self._reload_icon.setVisible(True)
        self._reload_icon.update()
        self._editor.setUpdatesEnabled(False)
        cfg.update()
        self._editor.setUpdatesEnabled(True)
        self._editor.reload()
        self._tree.reload()
        self._err.reload()
        line, index = self._editor.getCursorPosition()
        self._reload_node(line+1, index+1)        
        self._reload_icon_timer.start(700)

    def _hide_reload_icon(self):
        """Hides the reload icon."""
        self._reload_icon.setVisible(False)

    def _reload_node(self, line, index):
        """reload info after changing node selection"""
        node = cfg.get_data_node(Position(line, index))
        self._editor.set_new_node(node)
        if node is not None:
            cursor_type = self._editor.cursor_type_position
            self._info.update_from_node(node, cursor_type)
        self._debug_tab.show_data_node(node)

    def _on_element_changed(self, new_cursor_type, old_cursor_type):
        """Updates info_text if cursor_type has changed."""
        if self._editor.pred_parent is not None:
            self._info.update_from_node(self._editor.pred_parent, 
                                        CursorType.key.value)
            return
        line, index = self._editor.getCursorPosition()
        node = cfg.get_data_node(Position(line + 1, index + 1))
        if node is not None:
            self._info.update_from_node(node, new_cursor_type)

    def new_file(self):
        """new file menu action"""
        if not self._save_old_file():
            return
        cfg.new_file()
        self._reload()
        self.update_recent_files(0)
        self._update_document_name()
        self._status.showMessage("New file is opened", 5000)

    def open_file(self):
        """open file menu action"""
        if not self._save_old_file():
            return
        yaml_file = QtWidgets.QFileDialog.getOpenFileName(
            self._mainwindow, "Choose Yaml Model File",
            cfg.config.last_data_dir, "Yaml Files (*.yaml)")
        if yaml_file[0]:
            cfg.open_file(yaml_file[0])
            self._reload()
            self.update_recent_files()
            self._update_document_name()
            self._status.showMessage("File '" + yaml_file[0] + "' is opened", 5000)

    def import_file(self):
        """import con file menu action"""
        if not self._save_old_file():
            return
        con_file = QtWidgets.QFileDialog.getOpenFileName(
            self._mainwindow, "Choose Con Model File",
            cfg.config.last_data_dir, "Con Files (*.con)")
        if con_file[0]:
            cfg.import_file(con_file[0])
            self._reload()
            self.update_recent_files()
            self._update_document_name()
            self._status.showMessage("File '" + con_file[0] + "' is imported", 5000)

    def open_recent(self, action):
        """open recent file menu action"""
        if action.text() == cfg.curr_file:
            return
        if not self._save_old_file():
            return
        cfg.open_recent_file(action.text())
        self._reload()
        self.update_recent_files()
        self._update_document_name()
        self._status.showMessage("File '" + action.text() + "' is opened", 5000)

    def save_file(self):
        """save file menu action"""
        if cfg.curr_file is None:
            return self.save_as()
        cfg.update_yaml_file(self._editor.text())
        cfg.save_file()
        self._status.showMessage("File is saved", 5000)

    def save_as(self):
        """save file menu action"""
        cfg.update_yaml_file(self._editor.text())
        if cfg.curr_file is None:
            new_file = cfg.config.last_data_dir + os.path.sep + "NewFile.yaml"
        else:
            new_file = cfg.curr_file
        yaml_file = QtWidgets.QFileDialog.getSaveFileName(
            self._mainwindow, "Set Yaml Model File",
            new_file, "Yaml Files (*.yaml)")

        if yaml_file[0]:
            cfg.save_as(yaml_file[0])
            self.update_recent_files()
            self._update_document_name()
            self._status.showMessage("File is saved", 5000)
            return True
        return False

    def transform(self, file):
        """Run transformation according rules in set file"""
        cfg.update_yaml_file(self._editor.text())
        cfg.transform(file)
        # synchronize cfg document with editor text
        self._editor.setText(cfg.document, keep_history=True)
        self._reload()

    def edit_transformation_file(self, file):
        """edit transformation rules in file"""
        text = cfg.get_transformation_text(file)
        if text is not None:
            import data.meconfig
            dlg = JsonEditorDlg(data.meconfig.__transformation_dir__, file,
                                "Transformation rules:", text, self._mainwindow)
            dlg.exec_()

    def select_format(self, filename):
        """Selects format file by filename."""
        if cfg.curr_format_file == filename:
            return
        cfg.curr_format_file = filename
        cfg.update_format()
        self._reload()
        self._status.showMessage("Format of file is changed", 5000)

    def edit_format(self):
        """Open selected format file in Json Editor"""
        text = cfg.get_curr_format_text()
        if text is not None:
            import data.meconfig
            dlg = JsonEditorDlg(data.meconfig.__format_dir__, cfg.curr_format_file,
                                "Format", text, self._mainwindow)
            dlg.exec_()

    def update_recent_files(self, from_row=1):
        self._file_menu.update_recent_files(from_row)

    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Model Editor"
        if cfg.curr_file is None:
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
                self._mainwindow, 'Confirmation',
                "The document has unsaved changes, do you want to save it?",
                (QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                 QtWidgets.QMessageBox.Abort))
            if reply == QtWidgets.QMessageBox.Abort:
                return False
            if reply == QtWidgets.QMessageBox.Yes:
                if cfg.curr_file is None:
                    return self.save_as()
                else:
                    self.save_file()
        return True

    def main(self):
        """go"""
        self._app.exec_()

if __name__ == "__main__":
    ModelEditor().main()
