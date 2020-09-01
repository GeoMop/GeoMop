"""
Start script that inicialize main window
"""
import sys
import os
import signal

from LayerEditor.ui.data.le_data import LEData
from LayerEditor.ui.tools.cursor import Cursor

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from LayerEditor.ui.mainwindow import MainWindow
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from gm_base.geomop_util_qt import Autosave
from LayerEditor.data.config import _Config


class LayerEditor:
    """Layer Editor editor main class"""

    def __init__(self, args=None):
        self.qapp_setup()
        #TODO: handle args
        #if args:
        #    self.parse_args(args)


        self.le_data = LEData()
        self.cfg = _Config.open()

        self.mainwindow = MainWindow(self)
        self.exit = False

        save_fn = lambda c=self.le_data: self.le_data.le_serializer.save(c)
        self.autosave = Autosave(self.cfg.current_workdir, lambda: self.le_data.curr_file, save_fn)
        self._restore_backup()

        # show
        self.mainwindow.show()
        #self.mainwindow.paint_new_data()
        #self._update_document_name()
        #self.autosave.start_autosave()
        #self.mainwindow.diagramScene.regionsUpdateRequired.connect(self.autosave.on_content_change)


    def qapp_setup(self):
        """Setup application."""
        Cursor.setup_cursors()
        QtWidgets.QApplication.setWindowIcon(icon.get_app_icon("le-geomap"))
        QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

        # enable Ctrl+C from console to kill the application
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    # def parse_args(self, args):
    #     """
    #     Parse cmd line args.
    #     :return:
    #     """
    #     parser = argparse.ArgumentParser(description='OldLayerEditor')
    #     parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    #     parser.add_argument('file', help='Layers geometry JSON file.', default=None, nargs='?')
    #     args = parser.parse_args(args)
    #     if args.debug:
    #         cfg.config.__class__.DEBUG_MODE = True
    #         self.setup_logging()
    #     self.filename = ar
    #
    # def setup_logging(self):
    #     from gm_base.geomop_util.logging import log_unhandled_exceptions
    #
    #     def on_unhandled_exception(type_, exception, tback):
    #         """Unhandled exception callback."""
    #         # pylint: disable=unused-argument
    #         from gm_base.geomop_dialogs import GMErrorDialog
    #         err_dialog = GMErrorDialog(layer_editor.mainwindow)
    #         err_dialog.open_error_dialog("Unhandled Exception!", error=exception)
    #         sys.exit(1)
    #
    #     #            from geomop_dialogs import GMErrorDialog
    #     #            if layer_editor is not None:
    #     #                err_dialog = None
    #     #                # display message box with the exception
    #     #                if layer_editor.mainwindow is not None:
    #     #                    err_dialog = GMErrorDialog(layer_editor.mainwindow)
    #     #
    #     #                # try to reload editor to avoid inconsistent state
    #     #                if callable(layer_editor.mainwindow.reload):
    #     #                    try:
    #     #                        layer_editor.mainwindow.reload()
    #     #                    except:
    #     #                        if err_dialog is not None:
    #     #                            err_dialog.open_error_dialog("Application performed invalid operation!",
    #     #                                                         error=exception)
    #     #                            sys.exit(1)
    #     #
    #     #                if err_dialog is not None:
    #     #                    err_dialog.open_error_dialog("Unhandled Exception!", error=exception)
    #     #
    #     log_unhandled_exceptions(cfg.config.__class__.CONTEXT_NAME, on_unhandled_exception)
    #
    def _restore_backup(self):
        """recover file from backup file if it exists and if user wishes so"""
        restored = self.autosave.restore_backup()
        if restored:
            #self.cfg.main_window.release_data(self.cfg.diagram_id())
            #self.cfg.history.remove_all()
            self.le_data = LEData(self.autosave.backup_filename())
            #self.cfg.main_window.refresh_all()
            #self.cfg.history.last_save_labels = -1
        self.autosave.autosave_timer.stop()
        return restored

    def new_file(self):
        """
        New file action handler.
        return close if no file is created nor openned.
        """
        if not self.save_old_file():
            return

        #self.mainwindow.release_data(cls.diagram_id())
        self.le_data = LEData()

        self.le_data.curr_diagram.area.set_area([(0, 0), (100, 0), (100, 100), (0, 100)])
        #self.mainwindow.refresh_all()
        #self.mainwindow.paint_new_data()
        self._update_document_name()
        return True

    def open_file(self, in_file=None):
        """
        open file menu action
        handler for triggered signal.
        """

        if not self.save_old_file():
            return False
        if in_file is None:
            in_file, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.mainwindow, "Choose Json Geometry File",
                self.cfg.data_dir, "Json Files (*.json)")
        if in_file:
            #self.main_window.release_data(cls.diagram_id())
            self.le_data = LEData(in_file)
            self.cfg.update_current_workdir(in_file)
            scene = self.le_data.blocks[0].diagram_scene
            self.mainwindow.diagramView.setScene(scene)

            #cls.main_window.refresh_all()
            self.cfg.add_recent_file(in_file)
            self._update_document_name()
            self._restore_backup()
            self.mainwindow.show_status_message("File {} is opened".format(in_file))
            return True
        return False
    #
    # def add_shape_file(self):
    #     """open set file"""
    #     shp_file = QtWidgets.QFileDialog.getOpenFileName(
    #         self.mainwindow, "Choose Yaml Model File",
    #         cfg.config.data_dir, "Yaml Files (*.shp)")
    #     if shp_file[0]:
    #         if cfg.open_shape_file( shp_file[0]):
    #             self.mainwindow.refresh_diagram_shp()
    #             self.mainwindow.show_status_message("Shape file '" + shp_file[0] + "' is opened")
    #
    # def make_mesh(self):
    #     """open Make mesh dialog"""
    #     if self.save_file() is False:
    #         return
    #
    #     dlg = MakeMeshDlg(self.mainwindow)
    #     dlg.exec()
    #
    def open_recent(self, action):
        """open recent file menu action"""
        if action.data() == self.le_data.curr_file:
            return
        if not self.save_old_file():
            return
        self.cfg.open_recent_file(action.data())
        self.mainwindow.update_recent_files()
        self._update_document_name()
        self._restore_backup()
        self.mainwindow.show_status_message("File '" + action.data() + "' is opened")
    #
    def save_file(self):
        """save file menu action"""
        if self.le_data.curr_file is None:
            return self.save_as()
        if self.le_data.confront_file_timestamp():
            return
        self.le_data.save_file()
        self.cfg.add_recent_file(self.le_data.curr_file)
        self.autosave.delete_backup()
        self.mainwindow.show_status_message("File is saved")

    def save_as(self):
        """save file menu action"""
        if self.le_data.confront_file_timestamp():
            return
        if self.le_data.curr_file is None:
            new_file = self.cfg.current_workdir + os.path.sep + "NewFile.json"
        else:
            new_file = self.le_data.curr_file
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
            self.le_data.save_file(file_name)
            self.cfg.add_recent_file(file_name)
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
        if self.le_data.changed():
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
                if self.cfg.curr_file is None:
                    return self.save_as()
                else:
                    self.save_file()
            if reply == QtWidgets.QMessageBox.No:
                self.autosave.delete_backup()
        return True

    # def run(self):
    #     """go"""
    #     self._app.exec()
    #
    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Layer Editor"
        if self.le_data.curr_file is None:
            title += " - New File"
        else:
            title += " - " + self.le_data.curr_file
        self.mainwindow.setWindowTitle(title)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    layer_editor = LayerEditor(sys.argv[1:])
    app.exec()


