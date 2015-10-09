"""
Module contains about dialog.
"""

import os

from PyQt5.QtWidgets import (QDialog, QTextEdit, QLabel, QLineEdit, QGridLayout)
from PyQt5.QtGui import QFont

__author__ = 'Tomas Krizek'

__git_root_path__ = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0],
                                 '..', '..')


class GMAboutDialog(QDialog):
    """Dialog for displaying information about the application."""

    def __init__(self, parent, title='GeoMop'):
        """Initializes the class."""
        super(GMAboutDialog, self).__init__(parent)

        version_file_path = os.path.join(__git_root_path__, 'VERSION')
        changelog_file_path = os.path.join(__git_root_path__, 'CHANGELOG.md')

        try:
            with open(version_file_path) as version_file:
                lines = version_file.readlines()
        except FileNotFoundError:
            lines = []

        self.version = lines[0] if len(lines) > 0 else ''
        self.build = lines[1] if len(lines) > 1 else ''
        self.date = lines[2] if len(lines) > 2 else ''

        try:
            with open(changelog_file_path) as changelog_file:
                changelog = changelog_file.read()
        except FileNotFoundError:
            changelog = 'Changelog not found!'

        version_label = QLabel('Version: ')
        version_edit = QLineEdit()
        version_edit.setText(self.version)
        version_edit.setReadOnly(True)

        build_label = QLabel('Build: ')
        build_edit = QLineEdit()
        build_edit.setText(self.build)
        build_edit.setReadOnly(True)

        date_label = QLabel('Date: ')
        date_edit = QLineEdit()
        date_edit.setText(self.date)
        date_edit.setReadOnly(True)

        changelog_edit = QTextEdit()
        changelog_edit.setReadOnly(True)
        changelog_edit.setText(changelog)
        changelog_edit.setFont(QFont("monospace"))

        main_layout = QGridLayout()
        main_layout.addWidget(version_label, 0, 0)
        main_layout.addWidget(version_edit, 0, 1)
        main_layout.addWidget(build_label, 1, 0)
        main_layout.addWidget(build_edit, 1, 1)
        main_layout.addWidget(date_label, 2, 0)
        main_layout.addWidget(date_edit, 2, 1)
        main_layout.addWidget(changelog_edit, 3, 0, 1, 2)
        self.setLayout(main_layout)

        self.title = title + ' ' + self.version
        self.setWindowTitle(self.title)
        self.setMinimumSize(400, 300)
        self.setModal(True)


if __name__ == '__main__':
    def main():
        """"Launches dialog."""
        import sys
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        dialog = GMAboutDialog(None)
        dialog.show()
        sys.exit(app.exec_())
    main()


