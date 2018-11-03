"""
Start script that inicialize main window
"""
import sys
import os
import signal
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from LayerEditor.ui import MainWindow
from LayerEditor.leconfig import cfg
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from LayerEditor.ui.dialogs.set_diagram import SetDiagramDlg
from LayerEditor.ui.dialogs.make_mesh import MakeMeshDlg


style_sheet =\
"""
QLineEdit[status="modified"] {
    /* light orange */
    background-color: #FFCCAA                    
}
QLineEdit[status="error"] {
    /* light red */
    background-color: #FFAAAA                   
}
QLabel[status="error"] {
    /* light red */
    background-color: #FFAAAA                   
}
"""


class LayerEditor:
    """Analyzis editor main class"""
    
    def __init__(self, app, input_file=None):
        self._app = app
        # load config
        cfg.init()
        cfg.geomop_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        self.mainwindow = MainWindow(self)
        cfg.set_main(self.mainwindow)

        assert not cfg.changed()
        if input_file is None:
            self.exit = not self.new_file()
        else:
            self.open_file(False, input_file)
            self.exit = False

        # if ret!=QtWidgets.QDialog.Accepted:
        #     if not self.open_file():
        #         self.mainwindow.close()
        #         self.mainwindow._layer_editor = None
        #         del self.mainwindow
        #         self.exit = True
        #         return
        
        # set default values
        self.mainwindow.paint_new_data()
        self._update_document_name()

    def exec(self):
        """
        Show main window and start event loop.
        """
        if self.exit:
            return
        self.mainwindow.show()
        self._app.exec()

    def new_file(self):
        """
        New file action handler.
        return close if no file is created nor openned.
        """
        if not self.save_old_file():
            return

        init_dlg = SetDiagramDlg()
        accepted = init_dlg.exec_()
        if init_dlg.closed:
            return False

        if not accepted:
            if not self.open_file(False):
                return False
        else:
            cfg.new_file()
            self.mainwindow.refresh_all()
            self.mainwindow.paint_new_data()
        self._update_document_name()
        return True

    def open_file(self, checked, in_file=None):
        """
        open file menu action
        handler for triggered signal.
        """
        if not self.save_old_file():
            return False
        if in_file is None:
            in_file, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.mainwindow, "Choose Json Geometry File",
                cfg.config.data_dir, "Json Files (*.json)")
        if in_file:
            cfg.open_file(in_file)
            self._update_document_name()
            self.mainwindow.show_status_message("File '{}' is opened.".format(in_file))
            return True
        return False
            
    def add_shape_file(self):
        """open set file"""
        shp_file = QtWidgets.QFileDialog.getOpenFileName(
            self.mainwindow, "Choose Yaml Model File",
            cfg.config.data_dir, "Yaml Files (*.shp)")
        if shp_file[0]:
            if cfg.open_shape_file( shp_file[0]):
                self.mainwindow.refresh_diagram_shp()
                self.mainwindow.show_status_message("Shape file '" + shp_file[0] + "' is opened")

    def make_mesh(self):
        """open Make mesh dialog"""
        if self.save_file() is False:
            return

        dlg = MakeMeshDlg(self.mainwindow)
        dlg.exec()

    def open_recent(self, action):
        """open recent file menu action"""
        if action.data() == cfg.curr_file:
            return
        if not self.save_old_file():
            return
        cfg.open_recent_file(action.data())
        self.mainwindow.update_recent_files()
        self._update_document_name()
        self.mainwindow.show_status_message("File '" + action.data() + "' is opened")

    def save_file(self):
        """save file menu action"""
        if cfg.curr_file is None:
            return self.save_as()
        if cfg.confront_file_timestamp():
            return
        cfg.save_file()
        self.mainwindow.show_status_message("File is saved")

    def save_as(self):
        """save file menu action"""
        if cfg.confront_file_timestamp():
            return
        if cfg.curr_file is None:
            new_file = cfg.config.data_dir + os.path.sep + "NewFile.json"
        else:
            new_file = cfg.curr_file
        dialog = QtWidgets.QFileDialog(self.mainwindow, 'Save as JSON Geometry File', new_file,
                                       "JSON Files (*.json)")
        dialog.setDefaultSuffix('.json')
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setOption(QtWidgets.QFileDialog.DontConfirmOverwrite, False)
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            cfg.save_file(file_name)
            self.mainwindow.update_recent_files()
            self._update_document_name()
            self.mainwindow.show_status_message("File is saved")
            return True
        return False

    def save_old_file(self):
        """
        If file not saved, display confirmation dialog and if is needed, do it

        return: False if action have to be aborted
        """
        if cfg.changed():
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Confirmation")
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Abort)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.Abort)
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


    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Layer Editor"
        if cfg.curr_file is None:
            title += " - New File"
        else:
            title += " - " + cfg.curr_file
        self.mainwindow.setWindowTitle(title)

def make_application():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    app.setWindowIcon(icon.get_app_icon("le-geomap"))
    QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
    return app

def error_dialog():
    """
    Set error dialog for exception hook.
    :return:
    """
    from gm_base.geomop_util.logging import log_unhandled_exceptions

    def on_unhandled_exception(type_, exception, tback):
        """Unhandled exception callback."""
        # pylint: disable=unused-argument
        from gm_base.geomop_dialogs import GMErrorDialog
        err_dialog = GMErrorDialog(layer_editor.mainwindow)
        err_dialog.open_error_dialog("Unhandled Exception!", error=exception)
        sys.exit(1)

    log_unhandled_exceptions(cfg.config.__class__.CONTEXT_NAME, on_unhandled_exception)


def main():
    """LayerEditor application entry point."""
    parser = argparse.ArgumentParser(description='LayerEditor')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('file', help='Layers geometry JSON file.', default=None, nargs='?')
    args = parser.parse_args()

    app = make_application()

    if args.debug:
        cfg.config.__class__.DEBUG_MODE = True
    #else:

    # enable Ctrl+C from console to kill the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # launch the application
    in_file = args.file
    layer_editor = LayerEditor(app, in_file)
    layer_editor.exec()

    app.quit()
    del app
    del layer_editor
    sys.exit(0)


if __name__ == "__main__":
    main()


