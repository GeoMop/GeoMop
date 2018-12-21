"""System for automatic saving of current file into backup file.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
import os
import psutil
import codecs
import time
from PyQt5 import QtCore, QtWidgets



class Autosave:

    AUTOSAVE_INTERVAL = 2000
    # todo: resolve late creation of config dir

    def __init__(self, default_backup_dir, curr_filename_fnc, string_to_save_fnc):
        """ Initializes the class
        :param cfg: config object
        :param string_to_save_fnc: function which returns string to be saved
        """
        self.curr_filename_fnc = curr_filename_fnc
        self.text = string_to_save_fnc
        """timer for periodical saving"""
        self.autosave_timer = QtCore.QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self._autosave)
        self.backup_dir = default_backup_dir

    def backup_filename(self):
        """returns backup filename based on currently opened file"""
        if self.curr_filename_fnc() is None:
            backup_filename = os.path.join(self.backup_dir, "." + "Untitled.yaml" + ".backup")
        else:
            head, tail = os.path.split(self.curr_filename_fnc())
            backup_filename = os.path.join(head, "." + tail + ".backup")

        return backup_filename

    def _autosave(self):
        """periodically saves specified string (current file)"""
        with codecs.open(self.backup_filename(), 'w', 'utf-8') as file_d:
            file_d.write(self.text())

    def restore_backup(self):
        if os.path.isfile(self.backup_filename()):
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Unsaved document found")
            msg.setIcon(QtWidgets.QMessageBox.Question)
            if self.curr_filename_fnc() is None:
                tail = "Untitled.yaml"
            else:
                head, tail = os.path.split(self.curr_filename_fnc() if not None else "Untitled.yaml")
            msg.setText("Do you wish to recover unsaved file: " + tail +
                        "\nLast modification: " +
                        time.strftime("%d/%m/%Y %H:%M:%S",
                                      time.gmtime(os.path.getmtime(self.backup_filename()))))
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.Yes)
            msg.resize(500, 200)
            if msg.exec_() == QtWidgets.QMessageBox.Yes:
                return True
            else:
                return False



    def delete_backup(self):
        print(self.backup_filename())
        if os.path.exists(self.backup_filename()):
            os.remove(self.backup_filename())
        self.autosave_timer.stop()

    def on_content_change(self):
        self.autosave_timer.start(self.AUTOSAVE_INTERVAL)
