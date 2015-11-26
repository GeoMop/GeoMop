# -*- coding: utf-8 -*-
"""
Validators for UI
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os

from PyQt5 import QtCore
from PyQt5.QtGui import QRegExpValidator


class PresetNameValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("([a-zA-Z0-9]){1}([a-zA-Z0-9])*")
        super().__init__(rx, parent)


class MultiJobNameValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("[a-zA-Z0-9]{1}([a-zA-Z0-9]|[_-])*")
        super().__init__(rx, parent)

