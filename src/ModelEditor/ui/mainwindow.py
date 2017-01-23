"""Main Qt window.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

import icon
from helpers import LineAnalyzer
from meconfig import cfg
from ui import panels
from ui.menus import MainEditMenu, MainFileMenu, MainSettingsMenu, AnalysisMenu
from util import CursorType
from geomop_util import Position


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self, model_editor):
        """Initialize the class."""
        super(MainWindow, self).__init__()

        self.setMinimumSize(960, 660)

        self._hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self._model_editor = model_editor
        self.setCentralWidget(self._hsplitter)

        # tabs
        self._tab = QtWidgets.QTabWidget(self._hsplitter)
        self._tab.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self._tab.setMinimumSize(600, 200)
        self._tab.sizeHint = lambda: QtCore.QSize(700, 250)

        self.info = panels.InfoPanelWidget(self._tab)
        """info panel"""
        self.err = panels.ErrorWidget(self._tab)
        """error message panel"""
        self._tab.addTab(self.info, "Structure Info")
        self._tab.addTab(self.err, "Messages")

        # debug panel
        if cfg.config.DEBUG_MODE:
            self.debug_tab = panels.DebugPanelWidget(self._tab)
            self._tab.addTab(self.debug_tab, "Debug")

        # splitters
        self._vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self._hsplitter)
        self.editor = panels.YamlEditorWidget(self._vsplitter)
        """main editor component"""
        self.tree = panels.TreeWidget(self._vsplitter)
        """tree data display widget"""
        self._vsplitter.addWidget(self.editor)
        self._vsplitter.addWidget(self._tab)
        self._hsplitter.insertWidget(0, self.tree)

        # Menu bar
        self._menu = self.menuBar()
        self._file_menu = MainFileMenu(self, self._model_editor)
        self.update_recent_files(0)
        self._edit_menu = MainEditMenu(self, self.editor)
        self._settings_menu = MainSettingsMenu(self, self._model_editor)
        self._analysis_menu = AnalysisMenu(self, cfg.config, flow123d_versions=cfg.format_files)
        self._menu.addMenu(self._file_menu)
        self._menu.addMenu(self._edit_menu)
        self._menu.addMenu(self._analysis_menu)
        self._menu.addMenu(self._settings_menu)

        # status bar
        self._column = QtWidgets.QLabel(self)
        self._column.setFrameStyle(QtWidgets.QFrame.StyledPanel)

        self._reload_icon = QtWidgets.QLabel(self)
        self._reload_icon.setPixmap(icon.get_pixmap("refresh", 16))
        self._reload_icon.setVisible(False)
        self._reload_icon_timer = QtCore.QTimer(self)
        self._reload_icon_timer.timeout.connect(lambda: self._reload_icon.setVisible(False))

        self._analysis_label = QtWidgets.QLabel(self)
        cfg.config.observers.append(self)

        self._status = self.statusBar()
        self._status.addPermanentWidget(self._reload_icon)
        self._status.addPermanentWidget(self._analysis_label)
        self._status.addPermanentWidget(self._column)
        self.setStatusBar(self._status)
        self._status.showMessage("Ready", 5000)

        # signals
        self.err.itemSelected.connect(self._item_selected)
        self.tree.itemSelected.connect(self._item_selected)
        self.editor.nodeChanged.connect(self._reload_node)
        self.editor.cursorChanged.connect(self._cursor_changed)
        self.editor.structureChanged.connect(self._structure_changed)
        self.editor.errorMarginClicked.connect(self._error_margin_clicked)
        self.editor.elementChanged.connect(lambda new, old: self._update_info(new))
        self.editor.nodeSelected.connect(self._on_node_selected)

        # initialize components
        self._update_info(None)
        self.config_changed()

        # set focus
        self.editor.setFocus()

    def reload(self):
        """reload panels after structure changes"""
        self._reload_icon.setVisible(True)
        self._reload_icon.update()
        self.editor.setUpdatesEnabled(False)
        cfg.update()
        self.editor.setUpdatesEnabled(True)
        self.editor.reload()
        self.tree.reload()
        self.err.reload()
        line, index = self.editor.getCursorPosition()
        self._reload_node(line+1, index+1)
        self._reload_icon_timer.start(700)

    def show_status_message(self, message, duration=5000):
        """Show a message in status bar for the given duration (in ms)."""
        self._status.showMessage(message, duration)

    def update_recent_files(self, from_row=1):
        """Update recently opened files."""
        self._file_menu.update_recent_files(from_row)

    def _item_selected(self, start_line, start_column, end_line, end_column):
        """Handle when an item is selected from tree or error tab.

        :param int start_line: line where the selection starts
        :param int start_column: column where the selection starts
        :param int end_line: line where the selection ends
        :param int end_column: column where the selection ends
        """
        self.editor.setFocus()

        # remove empty line and whitespaces at the end of selection
        if end_line > start_line and end_line > 1:
            last_line_text = self.editor.text(end_line-1)
            if end_column > len(last_line_text):
                end_column = len(last_line_text) + 1
            last_line_text_selected = last_line_text[:end_column-1]
            if LineAnalyzer.is_empty(last_line_text_selected):
                end_line -= 1
                end_line_text = self.editor.text(end_line-1)
                end_column = len(end_line_text)

        # select in reversed order - move cursor to the beginning of selection
        self.editor.mark_selected(end_line, end_column, start_line, start_column)

    def _reload_node(self, line, index):
        """reload info after changing node selection"""
        node = cfg.get_data_node(Position(line, index))
        self.editor.set_new_node(node)
        cursor_type = self.editor.cursor_type_position
        self._update_info(cursor_type)
        if cfg.config.DEBUG_MODE:
            self.debug_tab.show_data_node(node)

    def _cursor_changed(self, line, column):
        """Editor node change signal"""
        self._column.setText("Line: {:5d}  Pos: {:3d}".format(line, column))

    def _structure_changed(self, line, column):
        """Editor structure change signal"""
        if cfg.update_yaml_file(self.editor.text()):
            self.reload()
        else:
            self._reload_node(line, column)

    def _error_margin_clicked(self, line):
        """Click error icon in margin"""
        self._tab.setCurrentIndex(self._tab.indexOf(self.err))
        self.err.select_error(line)

    def _update_info(self, cursor_type):
        """Update the info panel."""
        if self.editor.pred_parent is not None:
            self.info.update_from_node(self.editor.pred_parent,
                                       CursorType.parent.value)
            return
        if self.editor.curr_node is not None:
            self.info.update_from_node(self.editor.curr_node, cursor_type)
            return

        # show root input type info by default
        self.info.update_from_data({'record_id': cfg.root_input_type['id']})
        return

    def _on_node_selected(self, line, column):
        """Handles nodeSelected event from editor."""
        node = cfg.get_data_node(Position(line, column))
        self.tree.select_data_node(node)

    def closeEvent(self, event):
        """Performs actions before app is closed."""
        # prompt user to save changes (if any)
        if not self._model_editor.save_old_file():
            return event.ignore()

        # back up clipboard
        try:
            # pyperclip in try/except block - throws exception on Win XP
            import pyperclip
            clipboard = QtWidgets.QApplication.clipboard()
            pyperclip.copy(clipboard.text())
        except Exception:
            cfg.logger.error("Could not persist clipboard contents on application exit.")
        super(MainWindow, self).closeEvent(event)

    def config_changed(self):
        """Handle changes of config."""
        analysis = cfg.config.analysis or '(No Analysis)'
        self._analysis_label.setText(analysis)
        self.editor.set_line_endings(cfg.config.line_endings)

