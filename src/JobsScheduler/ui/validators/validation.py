# -*- coding: utf-8 -*-
"""
Validators for UI
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QRegExpValidator


class PresetNameValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("([a-zA-Z0-9])([a-zA-Z0-9])*")
        super().__init__(rx, parent)


class MultiJobNameValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("[a-zA-Z0-9]([a-zA-Z0-9]|[_-])*")
        super().__init__(rx, parent)


class WalltimeValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp(
            "(\d+[wdhms])(\d+[dhms])(\d+[hms])(\d+[ms])(\d+[s])")
        super().__init__(rx, parent)


class MemoryValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("\d+(mb|gb)")
        super().__init__(rx, parent)


class ScratchValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("\d+(mb|gb)(:(ssd|shared|local|first))?")
        super().__init__(rx, parent)
