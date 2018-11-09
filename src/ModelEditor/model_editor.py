"""Start script that initializes the main window.

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import argparse
import os
import signal
import sys

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QMessageBox
import PyQt5.QtCore as QtCore

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import gm_base.icon as icon
from ModelEditor.meconfig import MEConfig as cfg
from ModelEditor.ui.dialogs.json_editor import JsonEditorDlg
from ModelEditor.ui import MainWindow
from ModelEditor.util import constants
from ModelEditor.ui.dialogs.new_file_dialog import NewFileDialog
import subprocess

RELOAD_INTERVAL = 5000
"""interval for file time checjing in ms"""

class ModelEditor:
    """Model editor main class"""

    def __init__(self):
        # load config
        cfg.init(None)

        # main window
        self._app = QtWidgets.QApplication(sys.argv)
        #print("Model app: ", str(self._app))
        self._app.setWindowIcon(icon.get_app_icon("me-geomap"))
        self.mainwindow = MainWindow(self)
        cfg.main_window = self.mainwindow

        # set default values
        self._update_document_name()

        # show
        self.mainwindow.show()
        
        self.reloader_timer = QtCore.QTimer()
        """timer for file time checking in ms"""
        self.reloader_timer.timeout.connect(self.check_file)
        self.reloader_timer.start(RELOAD_INTERVAL)
        
    def check_file(self):
        """timer for file time checking in ms"""
        if self.mainwindow.isActiveWindow():
            if cfg.confront_file_timestamp():
                self.mainwindow.reload()

    def new_file(self):
        """new file menu action"""
        if not self.save_old_file():
            return

        dialog = NewFileDialog(self.mainwindow, cfg.config.data_dir)
        if dialog.exec_() == dialog.Rejected:
            return

        cfg.new_file()
        cfg.save_as(dialog.get_file_name())
        self.mainwindow.reload()
        self.mainwindow.update_recent_files(0)
        self._update_document_name()
        self.mainwindow.info.update_from_data({'record_id': cfg.root_input_type['id']}, False)
        self.mainwindow.show_status_message("New file is opened")

    def open_file(self):
        """open file menu action"""
        if not self.save_old_file():
            return
        yaml_file = QtWidgets.QFileDialog.getOpenFileName(
            self.mainwindow, "Choose Yaml Model File",
            cfg.config.data_dir, "Yaml Files (*.yaml)")
        if yaml_file[0]:
            cfg.open_file(yaml_file[0])
            self.mainwindow.reload()
            self.mainwindow.update_recent_files()
            self._update_document_name()
            self.mainwindow.show_status_message("File '" + yaml_file[0] + "' is opened")
            
    def open_set_file(self, file):
        """open set file"""
        cfg.open_file(file)
        self.mainwindow.reload()
        self.mainwindow.update_recent_files()
        self._update_document_name()
        self.mainwindow.show_status_message("File '" + file + "' is opened")
            
    def open_window(self):
        """open new instance of model editor"""
        subprocess.Popen([sys.executable, __file__])

    def import_file(self):
        """import con file menu action"""
        if not self.save_old_file():
            return
        con_file = QtWidgets.QFileDialog.getOpenFileName(
            self.mainwindow, "Choose Con Model File",
            cfg.config.data_dir, "Con Files (*.con)")
        if con_file[0]:
            cfg.import_file(con_file[0])
            self.mainwindow.reload()
            self.mainwindow.update_recent_files()
            self._update_document_name()
            self.mainwindow.show_status_message("File '" + con_file[0] + "' is imported")

    def open_recent(self, action):
        """open recent file menu action"""
        if action.data() == cfg.curr_file:
            return
        if not self.save_old_file():
            return
        cfg.open_recent_file(action.data())
        self.mainwindow.reload()
        self.mainwindow.update_recent_files()
        self._update_document_name()
        self.mainwindow.show_status_message("File '" + action.data() + "' is opened")

    def save_file(self):
        """save file menu action"""
        if cfg.curr_file is None:
            return self.save_as()
        if cfg.confront_file_timestamp():
            return
        cfg.update_yaml_file(self.mainwindow.editor.text())
        cfg.save_file()
        self.mainwindow.show_status_message("File is saved")

    def save_as(self):
        """save file menu action"""
        if cfg.confront_file_timestamp():
            return
        cfg.update_yaml_file(self.mainwindow.editor.text())
        if cfg.curr_file is None:
            if cfg.imported_file_name is not None:
                new_file = cfg.imported_file_name
            else:
                new_file = cfg.config.data_dir + os.path.sep + "NewFile.yaml"
        else:
            new_file = cfg.curr_file
        dialog = QtWidgets.QFileDialog(self.mainwindow, 'Save as YAML File', new_file,
                                       "YAML Files (*.yaml)")
        dialog.setDefaultSuffix('.yaml')
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setOption(QtWidgets.QFileDialog.DontConfirmOverwrite, False)
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            cfg.save_as(file_name)
            self.mainwindow.update_recent_files()
            self._update_document_name()
            self.mainwindow.show_status_message("File is saved")
            return True
        return False

    def transform(self, to_version):
        """Run transformation to version to_version."""
        cfg.update_yaml_file(self.mainwindow.editor.text())
        cfg.transform(to_version)
        # synchronize cfg document with editor text
        self.mainwindow.editor.setText(cfg.document, keep_history=True)
        self.mainwindow.reload()

    def transform_get_version_list(self):
        """Returns list of versions available to transformation."""
        return cfg.transform_get_version_list()

    def edit_transformation_file(self, file):
        """edit transformation rules in file"""
        text = cfg.get_transformation_text(file)
        if text is not None:
            dlg = JsonEditorDlg(cfg.transformation_dir, file,
                                "Transformation rules:", text, self.mainwindow)
            dlg.exec_()

    def select_format(self, filename):
        """Selects format file by filename."""
        if cfg.curr_format_file == filename:
            return
        cfg.curr_format_file = filename
        cfg.update_format()
        self.mainwindow.reload()
        self.mainwindow.show_status_message("Format of file is changed")

    def edit_format(self):
        """Open selected format file in Json Editor"""
        text = cfg.get_curr_format_text()
        if text is not None:
            dlg = JsonEditorDlg(cfg.format_dir, cfg.curr_format_file,
                                "Format", text, self.mainwindow)
            dlg.exec_()

    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Model Editor"
        if cfg.curr_file is None:
            title += " - New File"
        else:
            title += " - " + cfg.curr_file
        self.mainwindow.setWindowTitle(title)

    def save_old_file(self):
        """
        If file not saved, display confirmation dialeg and if is needed, do it

        return: False if action have to be aborted
        """
        cfg.update_yaml_file(self.mainwindow.editor.text())
        if cfg.changed:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Confirmation")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
            msg_box.setDefaultButton(QMessageBox.Abort)
            msg_box.setText("The document has unsaved changes, do you want to save it?")
            reply = msg_box.exec_()

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
        self._app.exec()


def main():
    """ModelEditor application entry point."""
    parser = argparse.ArgumentParser(description='ModelEditor')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('file', help='Yaml file', default=None,  nargs='?')
    args = parser.parse_args()

    if args.debug:
        cfg.config.__class__.DEBUG_MODE = True

    # logging
    if not args.debug:
        from gm_base.geomop_util.logging import log_unhandled_exceptions

        def on_unhandled_exception(type_, exception, tback):
            """Unhandled exception callback."""
            # pylint: disable=unused-argument
            from gm_base.geomop_dialogs import GMErrorDialog
            if model_editor is not None:
                err_dialog = None
                # display message box with the exception
                if model_editor.mainwindow is not None:
                    err_dialog = GMErrorDialog(model_editor.mainwindow)

                # try to reload editor to avoid inconsistent state
                if callable(model_editor.mainwindow.reload):
                    try:
                        model_editor.mainwindow.reload()
                    except:
                        if err_dialog is not None:
                            err_dialog.open_error_dialog("Application performed invalid operation!",
                                                         error=exception)
                            sys.exit(1)

                if err_dialog is not None:
                    err_dialog.open_error_dialog("Unhandled Exception!", error=exception)

        log_unhandled_exceptions(constants.CONTEXT_NAME, on_unhandled_exception)

    # enable Ctrl+C from console to kill the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # launch the application
    model_editor = ModelEditor()
    if args.file is not None:
        model_editor.open_set_file(args.file)
    model_editor.main()
    sys.exit(0)


if __name__ == "__main__":
    main()
