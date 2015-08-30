# -*- coding: utf-8 -*-
"""
Basic dialogs templates
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class UiFormDialog(object):
    """
    UI of basic form dialog.
    """
    def setup_ui(self, dialog):
        # dialog properties
        dialog.setObjectName("FormDialog")
        dialog.setWindowTitle("Form dialog")

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.mainVerticalLayoutWidget.setObjectName("mainVerticalLayoutWidget")
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(
            self.mainVerticalLayoutWidget)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")

        # title label
        self.titleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        title_font = QtGui.QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_font.setWeight(75)
        self.titleLabel.setFont(title_font)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setText("Title")
        self.mainVerticalLayout.addWidget(self.titleLabel)

        # subtitle label
        self.subtitleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        subtitle_font = QtGui.QFont()
        subtitle_font.setWeight(50)
        self.subtitleLabel.setFont(subtitle_font)
        self.subtitleLabel.setObjectName("subtitleLabel")
        self.subtitleLabel.setText("Subtitle text")
        self.mainVerticalLayout.addWidget(self.subtitleLabel)

        # divider
        self.headerDivider = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.headerDivider.setObjectName("headerDivider")
        self.headerDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.headerDivider)

        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 5, 0, 5)

        # add form to main layout
        self.mainVerticalLayout.addLayout(self.formLayout)

        # button box (order of of buttons is set by system default)
        self.buttonBox = QtWidgets.QDialogButtonBox(
            self.mainVerticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Close | QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.mainVerticalLayout.addWidget(self.buttonBox)

        # resize layout to fit dialog
        dialog.setLayout(self.mainVerticalLayout)
