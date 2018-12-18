"""System for automatic saving of current file into backup file.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
import os
import codecs
from PyQt5 import QtCore


class Autosave:

    AUTOSAVE_INTERVAL = 30000

    def __init__(self, cfg):
        """ Initializes the class
        :param cfg: config object
        """
        self.cfg = cfg
        """timer for periodical saving"""
        self.autosave_timer = QtCore.QTimer(cfg.main_window)
        #self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(self.AUTOSAVE_INTERVAL)

        self.backup_dir = os.path.join(self.cfg.config.CONFIG_DIR, "Backup")
        backup_files = [f for f in os.listdir(self.backup_dir)
                        if os.path.isfile(os.path.join(self.backup_dir, f))]

        if len(backup_files) != 0:
            self.resolve_backup()

        if self.cfg.curr_file is not None:
            self.backup_filename = os.path.join(self.backup_dir, self.cfg.curr_file)
        while os.path.isfile(self.backup_filename):


    def autosave(self):
        """ periodically saves specified string (current file)
        """
        with codecs.open(self.cfg.curr_file, 'w', 'utf-8') as file_d:
            file_d.write(self.cfg.document)

    def resolve_backup(self):
