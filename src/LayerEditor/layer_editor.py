"""
Start script that inicialize main window
"""
import sys
import os
import signal
import argparse
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from LayerEditor.ui import MainWindow
from LayerEditor.leconfig import cfg
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from gm_base.geomop_util import Autosave
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
    
    def __init__(self, init_dialog=True):
        # main window
        self._app = QtWidgets.QApplication(sys.argv)
        self._app.setStyleSheet(style_sheet)
        #print("Layer app: ", str(self._app))
        self._app.setWindowIcon(icon.get_app_icon("le-geomap"))
        
        # load config        
        cfg.init()

        # set default font to layers
        #cfg.layers.font = self._app.font()

        # set geomop root dir
        cfg.geomop_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        self.exit = False
        if init_dialog:
            init_dlg = SetDiagramDlg()
            ret = init_dlg.exec_()
            if init_dlg.closed:
                self.exit = True
                return
        else:
            ret = QtWidgets.QDialog.Accepted
            cfg.diagram.area.set_area([0, 0, 100, 100],[0, 100, 100, 0])
            
        self.mainwindow = MainWindow(self)
        cfg.set_main(self.mainwindow)
        
        # show
        self.mainwindow.show()

        self.autosave = Autosave(cfg.config.CONFIG_DIR,
                                 lambda: cfg.curr_file,
                                 lambda: json.dumps(cfg.le_serializer.cfg_to_geometry(
                                     cfg, self.autosave.backup_filename()).serialize(),
                                                    indent=4, sort_keys=True))
        """Object handling automatic saving"""
        
        if ret != QtWidgets.QDialog.Accepted:
            if not self.open_file():
                self.mainwindow.close()
                self.mainwindow._layer_editor = None
                del self.mainwindow
                self.exit = True
                return
        else:
            self._restore_backup()

        self.mainwindow.diagramScene.regionsUpdateRequired.connect(self.autosave.on_content_change)
        
        # set default values
        self.mainwindow.paint_new_data()
        self._update_document_name()

    def _restore_backup(self):
        """recover file from backup file if it exists and if user wishes so"""
        if self.autosave.restore_backup():
            cfg.main_window.release_data(cfg.diagram_id())
            cfg.history.remove_all()
            cfg.le_serializer.load(cfg, self.autosave.backup_filename())
            cfg.main_window.refresh_all()
            cfg.history.last_save_labels = -1
        self.autosave.autosave_timer.stop()
        
    def new_file(self):
        """new file menu action"""
        if not self.save_old_file():
            return
        init_dlg = SetDiagramDlg()
        ret = init_dlg.exec_()
        if init_dlg.closed:
            return
        cfg.new_file()        
        if ret!=QtWidgets.QDialog.Accepted:
            if not self.open_file():
                self.new_file()
                self.mainwindow.show_status_message("New file is opened")
        else:
            self.mainwindow.refresh_all()
            self.mainwindow.paint_new_data()
        self._update_document_name()
 
    def open_file(self):
        """open file menu action"""
        if not self.save_old_file():
            return False
        file = QtWidgets.QFileDialog.getOpenFileName(
            self.mainwindow, "Choose Json Geometry File",
            cfg.config.data_dir, "Json Files (*.json)")
        if file[0]:
            cfg.open_file(file[0])
            self._update_document_name()
            self._restore_backup()
            self.mainwindow.show_status_message("File '" + file[0] + "' is opened")
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
        self._restore_backup()
        self.mainwindow.show_status_message("File '" + action.data() + "' is opened")

    def save_file(self):
        """save file menu action"""
        if cfg.curr_file is None:
            return self.save_as()
        if cfg.confront_file_timestamp():
            return
        cfg.save_file()
        self.autosave.delete_backup()
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
            self.autosave.delete_backup()
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
            if reply == QtWidgets.QMessageBox.No:
                self.autosave.delete_backup()
        return True

    def main(self):
        """go"""
        self._app.exec()
        
    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Layer Editor"
        if cfg.curr_file is None:
            title += " - New File"
        else:
            title += " - " + cfg.curr_file
        self.mainwindow.setWindowTitle(title)


def main():
    """LayerEditor application entry point."""
    parser = argparse.ArgumentParser(description='LayerEditor')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    if args.debug:
        cfg.config.__class__.DEBUG_MODE = True
        
    #set locale    
    QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

    # logging
    if not args.debug:
        from gm_base.geomop_util.logging import log_unhandled_exceptions

        def on_unhandled_exception(type_, exception, tback):
            """Unhandled exception callback."""
            # pylint: disable=unused-argument
            from gm_base.geomop_dialogs import GMErrorDialog
            err_dialog = GMErrorDialog(layer_editor.mainwindow)
            err_dialog.open_error_dialog("Unhandled Exception!", error=exception)
            sys.exit(1)
            
            
            
#            from geomop_dialogs import GMErrorDialog
#            if layer_editor is not None:
#                err_dialog = None
#                # display message box with the exception
#                if layer_editor.mainwindow is not None:
#                    err_dialog = GMErrorDialog(layer_editor.mainwindow)
#
#                # try to reload editor to avoid inconsistent state
#                if callable(layer_editor.mainwindow.reload):
#                    try:
#                        layer_editor.mainwindow.reload()
#                    except:
#                        if err_dialog is not None:
#                            err_dialog.open_error_dialog("Application performed invalid operation!",
#                                                         error=exception)
#                            sys.exit(1)
#
#                if err_dialog is not None:
#                    err_dialog.open_error_dialog("Unhandled Exception!", error=exception)
#
        log_unhandled_exceptions(cfg.config.__class__.CONTEXT_NAME, on_unhandled_exception)

    # enable Ctrl+C from console to kill the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # launch the application
    layer_editor = LayerEditor()
    if not layer_editor.exit:
        layer_editor.main()

    layer_editor._app.quit()
    del layer_editor._app
    del layer_editor
    sys.exit(0)


if __name__ == "__main__":
    main()


