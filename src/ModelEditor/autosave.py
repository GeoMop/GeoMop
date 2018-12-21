"""System for automatic saving of current file into backup file.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
import os
import psutil
import codecs
from PyQt5 import QtCore



class Autosave:

    AUTOSAVE_INTERVAL = 1000
    # todo: resolve late creation of config dir

    def __init__(self, cfg, string_to_save_fnc):
        """ Initializes the class
        :param cfg: config object
        :param string_to_save_fnc: function which returns string to be saved
        """
        self.cfg = cfg
        self.text = string_to_save_fnc
        """timer for periodical saving"""
        self.autosave_timer = QtCore.QTimer(cfg.main_window)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.autosave)

        self.backup_dir = os.path.join(self.cfg.config.CONFIG_DIR, "Backup")
        if not os.path.isdir(self.backup_dir):
            os.mkdir(self.backup_dir)

        backup_files = [f for f in os.listdir(self.backup_dir)
                        if os.path.isfile(os.path.join(self.backup_dir, f))]

        if len(backup_files) != 0:
            self.resolve_backup(backup_files)

    def autosave(self):
        """periodically saves specified string (current file)"""
        if self.cfg.curr_file is None:
            backup_filename = os.path.join(self.backup_dir, "." + "Undefined.yaml" + ".bckp")
        else:
            backup_filename = os.path.join(self.backup_dir, "." + os.path.basename(self.cfg.curr_file) + ".bckp")

        with codecs.open(backup_filename, 'w', 'utf-8') as file_d:
            file_d.write(self.text())

    def resolve_backup(self, files):
        for file in files:
            i = 1

    def delete_backup(self):
        if self.cfg.curr_file is None:
            backup_filename = os.path.join(self.backup_dir, "." + "Undefined.yaml" + ".bckp")
        else:
            backup_filename = os.path.join(self.backup_dir, "." + os.path.basename(self.cfg.curr_file) + ".bckp")
        print(backup_filename)
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
        self.autosave_timer.stop()

    def on_content_change(self):
        if not self.autosave_timer.isActive():
            self.autosave_timer.start(self.AUTOSAVE_INTERVAL)
