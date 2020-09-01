"""
Module contains help dialog.
"""

from gm_base.version import Version
from PyQt5.QtWidgets import (QDialog, QLabel, QGridLayout)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices, QFont

__author__ = 'Martin Matusu'

class LE_help_dialog(QDialog):
    """Dialog for displaying help information for LE. Main element is the link to documentation."""

    def __init__(self, parent, title='Layer Editor Help'):
        """Initializes the class."""
        super(LE_help_dialog, self).__init__(parent)

        version = Version()
        self.version = version.version

        link_label = QLabel()
        link_label.linkActivated.connect(self.link)
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setText('<a href="https://docs.google.com/document/d/1DipuCU-Gb9uCIGuSuYZOUIPLzQaHstPOYMD7smHNcQw/">Geomop reference guide</a>')
        link_label.setFont(QFont("monospace"))

        main_layout = QGridLayout()
        main_layout.addWidget(link_label, 0, 0)
        self.setLayout(main_layout)

        self.title = title + ' v.' + self.version
        self.setWindowTitle(self.title)
        self.setMinimumSize(300, 100)
        self.setModal(True)

    @staticmethod
    def link(linkStr):
        QDesktopServices.openUrl(QUrl(linkStr))


if __name__ == '__main__':
    def main():
        """"Launches dialog."""
        import sys
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        dialog = LE_help_dialog(None)
        dialog.show()
        sys.exit(app.exec_())
    main()


