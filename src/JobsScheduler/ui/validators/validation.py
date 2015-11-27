# -*- coding: utf-8 -*-
"""
Validators for UI
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtGui import QRegExpValidator, QColor, QValidator


class ValidationColors(Enum):
    white = QColor("#ffffff")
    red = QColor("#f6989d")
    green = QColor("#c4df9b")
    yellow = QColor("#fff79a")


class ValidationColorizer:
    @classmethod
    def colorize(cls, field, color):
        color_name = color.value.name()
        class_name = field.__class__.__name__
        field.setStyleSheet('%s { background-color: %s }' % (
            class_name, color_name))

    @classmethod
    def colorize_white(cls, field):
        cls.colorize(field, ValidationColors.white)

    @classmethod
    def colorize_red(cls, field):
        cls.colorize(field, ValidationColors.red)

    @classmethod
    def colorize_green(cls, field):
        cls.colorize(field, ValidationColors.green)

    @classmethod
    def colorize_yellow(cls, field):
        cls.colorize(field, ValidationColors.yellow)

    @classmethod
    def colorize_by_validator(cls, field, validator=None):
        if validator is None:
            validator = field.validator()
        state = validator.validate(field.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = ValidationColors.green
        elif state == QValidator.Intermediate:
            color = ValidationColors.yellow
        else:
            color = ValidationColors.red
        cls.colorize(field, color)

        if state == QValidator.Acceptable:
            return True
        else:
            return False


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
            "(\d+[wdhms])(\d+[dhms])?(\d+[hms])?(\d+[ms])?(\d+[s])?")
        super().__init__(rx, parent)


class MemoryValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("\d+(mb|gb)")
        super().__init__(rx, parent)


class ScratchValidator(QRegExpValidator):

    def __init__(self, parent=None):
        rx = QtCore.QRegExp("\d+(mb|gb)(:(ssd|shared|local|first))?")
        super().__init__(rx, parent)
