# -*- coding: utf-8 -*-
"""
Validators for UI
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
from enum import Enum
from PyQt5.QtGui import QColor
from PyQt5 import QtWidgets


class ValidationColors(Enum):
    """
    Holds colors for form validation.
    """
    white = QColor("#ffffff")
    red = QColor("#f6989d")
    grey = QColor("#A0A0A0")


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
    def colorize_frame(cls, field, color):
        """
        Color border of the field with specified color.
        :param field: Field handler.
        :param color: Desired color.
        :return:
        """
        color_name = color.name()
        class_name = field.__class__.__name__
        field.setStyleSheet('%s { border: 1px solid %s; border-radius: 3px; }' % (
            class_name, color_name))

    @classmethod
    def colorize_default(cls, field):
        """
        Convenience method for white coloring.
        :param field: Field handler.
        :return:
        """
        if isinstance( field, QtWidgets.QLineEdit):
            cls.colorize(field, ValidationColors.white.value)
        if isinstance( field, QtWidgets.QComboBox):
            cls.colorize_frame(field, ValidationColors.grey.value)

    @classmethod
    def colorize_red(cls, field):
        """
        Convenience method for red coloring.
        :param field: Field handler.
        :return:
        """
        if isinstance( field, QtWidgets.QLineEdit):
            cls.colorize(field, ValidationColors.red.value)
        if isinstance( field, QtWidgets.QComboBox):
            cls.colorize_frame(field, ValidationColors.red.value)


class PresetsValidationColorizer():
    """validator for controls in preset."""
    
    def __init__(self):
        self.controls={}
        """dictionary of validated controls"""
        
    def add(self, key, control):
        """add control for validation"""
        self.controls[key] = control
        
    def colorize(self, errors):
        """Colorized associated control and return if any control was colorized"""
        valid = True
        for key, control in self.controls.items():
            if key in errors:
                control.setToolTip(errors[key])                
                ValidationColorizer.colorize_red(control)
                valid = False
            else:
                ValidationColorizer.colorize_default(control)
                control.setToolTip("")
        return valid
    
    def reset_colorize(self):
        """Colorized associated control to white"""
        for key, control in self.controls.items():
            ValidationColorizer.colorize_default(control)
            control.setToolTip("")
            
    def connect(self, validation_func):
        """Colorized associated control to white"""
        for key, control in self.controls.items():
            if isinstance( control, QtWidgets.QLineEdit):
                control.editingFinished.connect(validation_func)
            if isinstance( control, QtWidgets.QComboBox):
                control.currentIndexChanged.connect(validation_func)
