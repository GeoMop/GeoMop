"""
Start script that inicialize main window
"""
import json
import sys
import os
import signal

from LayerEditor.exceptions.data_inconsistent_exception import DataInconsistentException
from LayerEditor.ui.data.le_model import LEModel
from LayerEditor.ui.diagram_editor.diagram_view import DiagramView
from LayerEditor.ui.dialogs.make_mesh import MakeMeshDlg
from LayerEditor.ui.panels import RegionsPanel
from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.cursor import Cursor
from gm_base.geometry_files.format_last import UserSupplement
from gm_base.geomop_dialogs import GMErrorDialog

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from LayerEditor.ui.mainwindow import MainWindow
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import gm_base.icon as icon
from gm_base.geomop_util_qt import Autosave
from LayerEditor.data import cfg


class LayerEditor:
    """Layer Editor editor main class"""

    def __init__(self, args=None):
        self.qapp_setup()

        self._le_model = LEModel()

        self.mainwindow = MainWindow(self)
        self.exit = False

        save_fn = lambda: self.save_model()
        curr_file_fn = lambda: self.le_model.curr_file
        #TODO: check default dir to autosave, this might be wrong
        self.autosave = Autosave(cfg.current_workdir, curr_file_fn, save_fn)
        self._restore_backup()

        # show
        self.mainwindow.show()
        self._update_document_name()
        self.autosave.start_autosave()

    def qapp_setup(self):
        """Setup application."""
        Cursor.setup_cursors()
        QtWidgets.QApplication.setWindowIcon(icon.get_app_icon("le-geomap"))
        QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

        # enable Ctrl+C from console to kill the application
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    @property
    def le_model(self):
        return self._le_model

    @le_model.setter
    def le_model(self, le_model):
        self._le_model = le_model
        self.mainwindow.make_widgets()
        self.autosave.update_content()

    def _restore_backup(self):
        """recover file from backup file if it exists and if user wishes so"""
        restored = self.autosave.restore_backup()
        if restored:
            self.load_file(self.autosave.backup_filename(), from_backup=True)
        return restored

    def new_file(self):
        """
        New file action handler.
        return close if no file is created nor openned.
        """
        if not self.save_old_file():
            return
        self.load_file()

    def load_file(self, in_file=None, from_backup=False):
        """Loads in_file and sets the new scene to be visible. If in_file is None it will create default model"""
        undo.clear()
        try:
            le_model = LEModel(in_file)
            if from_backup:
                le_model.curr_file = None
                le_model.curr_file_timestamp = None
            self.le_model = le_model
            self._update_document_name()
        except (RuntimeError, IOError) as err:
            err_dialog = GMErrorDialog(self.mainwindow)
            err_dialog.open_error_dialog("Can't open file", err)


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
                cfg.data_dir, "Json Files (*.json)")
        if in_file:
            cfg.add_recent_file(in_file)
            self.load_file(in_file)
            cfg.update_current_workdir(in_file)

            cfg.current_workdir = os.path.dirname(in_file)
            self._restore_backup()
            self.mainwindow.show_status_message("File {} is opened".format(in_file))
            return True
        return False

    def add_shape_file(self):
        """open set file"""
        shp_file = QtWidgets.QFileDialog.getOpenFileName(
            self.mainwindow, "Choose Yaml Model File",
            cfg.data_dir, "Yaml Files (*.shp)")
        if shp_file[0]:
            errors = self.le_model.add_shape_file(shp_file[0])
            if errors is None:
                errors = ["This shapefile is already opened!"]
            if len(errors) == 0:
                self.mainwindow.refresh_diagram_shp()
                self.mainwindow.show_status_message("Shape file '" + shp_file[0] + "' is opened")
            else:
                err_dialog = GMErrorDialog(self.mainwindow)
                err_dialog.open_error_report_dialog(errors, msg="Shape file parsing errors:", title=shp_file[0])


    def make_mesh(self):
        """open Make mesh dialog"""
        # if self.save_file() is False:
        #     return
        if self.le_model.curr_file is None:
            if self.save_as() is not True:
                return

        dlg = MakeMeshDlg(self)
        dlg.exec()

    def open_recent(self, action):
        """open recent file menu action"""
        if action.data() == self.le_model.curr_file:
            return
        if not self.save_old_file():
            return
        self.load_file(action.data())
        cfg.add_recent_file(action.data())
        self.mainwindow.update_recent_files()
        self._update_document_name()
        self._restore_backup()
        self.mainwindow.show_status_message("File '" + action.data() + "' is opened")

    def save_model(self, filename=""):
        geo_model, supplement_config = self.le_model.save()
        supplement_config.update(self.mainwindow.diagram_view.save())
        geo_model.supplement = UserSupplement(supplement_config)
        errors = LEModel.check_geo_model_consistency(geo_model)
        if len(errors) > 0:
            raise DataInconsistentException("Some file consistency errors occure", errors)
        if filename:
            with open(filename, 'w') as f:
                json.dump(geo_model.serialize(), f, indent=4, sort_keys=True)
            return None
        else:
            return json.dumps(geo_model.serialize(), indent=4, sort_keys=True)


    def save(self, filename=None):
        """Common code for saving file (used by save_file and save_as)"""
        if filename is None:
            filename = self.le_model.curr_file
        self.save_model(filename)
        self.le_model.curr_file = filename
        try:
            self.le_model.curr_file_timestamp = os.path.getmtime(filename)
        except OSError:
            self.le_model.curr_file_timestamp = None

        cfg.add_recent_file(self.le_model.curr_file)
        self.autosave.delete_backup()
        self.mainwindow.update_recent_files()
        self._update_document_name()
        undo.savepoint()

    def save_file(self):
        """save file menu action"""
        if self.le_model.curr_file is None:
            return self.save_as()
        if self.le_model.confront_file_timestamp():
            return
        self.save()
        self.mainwindow.show_status_message("File is saved")

    def save_as(self):
        """save file menu action"""
        if self.le_model.confront_file_timestamp():
            return
        if self.le_model.curr_file is None:
            new_file = cfg.current_workdir + os.path.sep + "NewFile.json"
        else:
            new_file = self.le_model.curr_file
        dialog = QtWidgets.QFileDialog(self.mainwindow, 'Save as JSON Geometry File', new_file,
                                       "JSON Files (*.json)")
        dialog.setDefaultSuffix('.json')
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setOption(QtWidgets.QFileDialog.DontConfirmOverwrite, False)
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if dialog.exec_():
            file_name = dialog.selectedFiles()[0]
            cfg.current_workdir = os.path.dirname(file_name)
            self.save(file_name)
            self.mainwindow.show_status_message("File is saved")
            return True
        return False

    def save_old_file(self):
        """
        If file not saved, display confirmation dialog and if is needed, do it
        return: False if action have to be aborted
        """
        if undo.has_changed():
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

    def _update_document_name(self):
        """Update document title (add file name)"""
        title = "GeoMop Layer Editor"
        if self.le_model.curr_file is None:
            title += " - New File"
        else:
            title += " - " + self.le_model.curr_file
        self.mainwindow.setWindowTitle(title)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    layer_editor = LayerEditor(sys.argv[1:])
    app.exec()


