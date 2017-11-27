"""
Start script that inicialize main window
"""
import sys
import os
import signal
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

import argparse
from ui import MainWindow
from leconfig import cfg
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import icon
from ui.dialogs.set_diagram import SetDiagramDlg
from ui.dialogs.make_mesh import MakeMeshDlg

class LayerEditor:
    """Analyzis editor main class"""
    
    def __init__(self, init_dialog=True):
        # main window
        self._app = QtWidgets.QApplication(sys.argv)
        self._app.setWindowIcon(icon.get_app_icon("le-geomap"))
        
        # load config        
        cfg.init()

        # set default font to layers
        cfg.layers.font = self._app.font()

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
        self.mainwindow.paint_new_data()
        
        if ret!=QtWidgets.QDialog.Accepted:
            if not self.open_file():
                self.new_file()
        
        # set default values
        self._update_document_name()        
        
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
        else:
            self.mainwindow.refresh_all()
            self.mainwindow.display_all()
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
#        self.mainwindow.show_status_message("File '" + action.data() + "' is opened")

    def save_file(self):
        """save file menu action"""
        if cfg.curr_file is None:
            return self.save_as()
        if cfg.confront_file_timestamp():
            return
        cfg.save_file()
        # self.mainwindow.show_status_message("File is saved")

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
#            self.mainwindow.show_status_message("File is saved")
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

    def main(self):
        """go"""
        self._app.exec_()
        
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
#    if not args.debug:
#        from geomop_util.logging import log_unhandled_exceptions
#
#        def on_unhandled_exception(type_, exception, tback):
#            """Unhandled exception callback."""
#            # pylint: disable=unused-argument
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
#        log_unhandled_exceptions(cfg.config.__class__.CONTEXT_NAME, on_unhandled_exception)

    # enable Ctrl+C from console to kill the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # launch the application
    layer_editor = LayerEditor()
    if not layer_editor.exit:
        layer_editor.main()
    sys.exit(0)


if __name__ == "__main__":
    main()


