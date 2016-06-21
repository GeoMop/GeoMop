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
    """
    Holds colors for form validation.
    """
    white = QColor("#ffffff")
    red = QColor("#f6989d")
    green = QColor("#c4df9b")
    yellow = QColor("#fff79a")


class ValidationColorizer:
    """
    Provides simple coloring capability.
    """
    @classmethod
    def colorize(cls, field, color):
        """
        Color background of the field with specified color.
        :param field: Field handler.
        :param color: Desired color.
        :return:
        """
        color_name = color.name()
        class_name = field.__class__.__name__
        field.setStyleSheet('%s { background-color: %s }' % (
            class_name, color_name))

    @classmethod
    def colorize_white(cls, field):
        """
        Convenience method for white coloring.
        :param field: Field handler.
        :return:
        """
        cls.colorize(field, ValidationColors.white.value)

    @classmethod
    def colorize_red(cls, field):
        """
        Convenience method for red coloring.
        :param field: Field handler.
        :return:
        """
        cls.colorize(field, ValidationColors.red.value)

    @classmethod
    def colorize_green(cls, field):
        """
        Convenience method for green coloring.
        :param field: Field handler.
        :return:
        """
        cls.colorize(field, ValidationColors.green.value)

    @classmethod
    def colorize_yellow(cls, field):
        """
        Convenience method for yellow coloring.
        :param field: Field handler.
        :return:
        """
        cls.colorize(field, ValidationColors.yellow.value)

    @classmethod
    def colorize_by_validator(cls, field, validator=None):
        """
        :param field: Field handler.
        :param validator: External validator if needed, otherwise taken from
        field.validator().
        :return: True if state is acceptable, otherwise False
        """
        if validator is None:
            validator = field.validator()
        state = validator.validate(field.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = ValidationColors.green.value
        elif state == QValidator.Intermediate:
            color = ValidationColors.yellow.value
        else:
            color = ValidationColors.red.value
        cls.colorize(field, color)

        if state == QValidator.Acceptable:
            return True
        else:
            return False


class PresetNameValidator(QRegExpValidator):
    """
    Preset name validator.
    """
    def __init__(self, rx=None, parent=None, excluded=None):
        if excluded is None:
            excluded = []
        self.excluded = excluded
        if rx is None:
            rx = QtCore.QRegExp("([a-zA-Z0-9])([a-zA-Z0-9]|[_-\s])*")
        super(PresetNameValidator, self).__init__(rx, parent)

    def validate(self, text, pos):
        if text in self.excluded:
            return (QValidator.Intermediate, text, pos)
        return super(PresetNameValidator, self).validate(text, pos)


class SshNameValidator(PresetNameValidator):
    def __init__(self, rx=None, parent=None, excluded=None):
        if excluded is None:
            excluded = []
        if 'local' not in excluded:
            excluded.append('local')
        super(SshNameValidator, self).__init__(rx, parent, excluded)


class PbsNameValidator(PresetNameValidator):
    def __init__(self, rx=None, parent=None, excluded=None):
        if excluded is None:
            excluded = []
        if 'no PBS' not in excluded:
            excluded.append('no PBS')
        super(PbsNameValidator, self).__init__(rx, parent, excluded)


class MultiJobNameValidator(PresetNameValidator):
    """
    MultiJob validator, only alphanumeric values and (_-).
    """
    def __init__(self, rx=None, parent=None, excluded=None):
        if rx is None:
            rx = QtCore.QRegExp("[a-zA-Z0-9]([a-zA-Z0-9]|[_-])*")
        super().__init__(rx, parent, excluded)


class WalltimeValidator(QRegExpValidator):
    """
    Ẅalltime validator, accepts only valid walltime string.
    """
    def __init__(self, parent=None):
        rx = QtCore.QRegExp(
            "^$|(\d+[wdhms])(\d+[dhms])?(\d+[hms])?(\d+[ms])?(\d+[s])?")
        super().__init__(rx, parent)


class MemoryValidator(QRegExpValidator):
    """
    Memory validator, accepts only valid memory string.
    """
    def __init__(self, parent=None):
        rx = QtCore.QRegExp("^$|\d+(mb|gb)")
        super().__init__(rx, parent)


class ScratchValidator(QRegExpValidator):
    """
    Scratch validator, accepts only valid scratch string.
    """
    def __init__(self, parent=None):
        rx = QtCore.QRegExp("^$|\d+(mb|gb)(:(ssd|shared|local|first))?")
        super().__init__(rx, parent)
