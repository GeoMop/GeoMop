"""System for automatic saving of current file into backup file.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
import os
import psutil
import codecs
import time
from PyQt5 import QtCore, QtWidgets


class Autosave:

    AUTOSAVE_INTERVAL = 1000
    # in miliseconds
    DEFAULT_FILENAME = "Untitled.yaml"

    def __init__(self, default_backup_dir, curr_filename_fnc, string_to_save_fnc):
        """Initializes the class.
        :param default_backup_dir: place where to save backup file for Untitled file
        :param curr_filename_fnc: function which returns currently opened filename
        :param string_to_save_fnc: function which returns string to be saved
        """
        self.curr_filename_fnc = curr_filename_fnc
        self.text = string_to_save_fnc

        self.autosave_timer = QtCore.QTimer()
        """timer for periodical saving"""
        #self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(self.AUTOSAVE_INTERVAL)
        if not os.path.isdir(default_backup_dir):
            try:
                os.makedirs(default_backup_dir)
            except OSError:
                print("Could not create config directory: " + default_backup_dir)
                self.backup_dir = os.path.curdir()
                return
        self.backup_dir = default_backup_dir

    def backup_filename(self):
        """Returns backup filename based on currently opened file."""
        if self.curr_filename_fnc() is None:
            backup_filename = os.path.join(self.backup_dir, "." + self.DEFAULT_FILENAME + ".backup")
        else:
            head, tail = os.path.split(self.curr_filename_fnc())
            backup_filename = os.path.join(head, "." + tail + ".backup")

        return backup_filename

    def _autosave(self):
        """Periodically saves specified string (current file)."""
        print("autosave")
        content = self.text()
        content_hash = hash(content)
        if self.content_hash != content_hash:
            self.content_hash = content_hash
            with codecs.open(self.backup_filename(), 'w', 'utf-8') as file_d:
                file_d.write(content)

    def restore_backup(self):
        """When new file is opened, check if there is backup file and ask user if it should be recovered.
        :return bool: True if user wants to recover backup file
        """
        if os.path.isfile(self.backup_filename()):
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Unsaved document found")
            msg.setIcon(QtWidgets.QMessageBox.Question)
            if self.curr_filename_fnc() is None:
                tail = self.DEFAULT_FILENAME
            else:
                head, tail = os.path.split(self.curr_filename_fnc() if not None else self.DEFAULT_FILENAME)
            msg.setText("Do you wish to continue editing last unsaved version of file: " + tail + " ?" +
                        "\nLast modification: " +
                        time.strftime("%Y/%m/%d %H:%M:%S",
                                      time.gmtime(os.path.getmtime(self.backup_filename()))))
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.Yes)
            msg.resize(500, 200)
            if msg.exec_() == QtWidgets.QMessageBox.Yes:
                return True
            else:
                self.delete_backup()
                return False

    def delete_backup(self):
        """Delete backup file if is no longer needed."""
        if os.path.exists(self.backup_filename()):
            os.remove(self.backup_filename())
        self.autosave_timer.stop()

    def on_content_change(self):
        """Restart timer when current document changed."""
        #self.autosave_timer.start(self.AUTOSAVE_INTERVAL)
