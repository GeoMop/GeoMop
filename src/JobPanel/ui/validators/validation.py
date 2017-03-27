# -*- coding: utf-8 -*-
"""
Validators for UI
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
from enum import Enum
from PyQt5.QtGui import QColor


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
    def colorize_by_validator(cls, field, errors):
        """
        :param field: Field handler.
        :param errors: Data errors dictionary.
        :return: True if state is acceptable, otherwise False
        """
        validator = field.validator()
        state,  error_text = validator.validate(errors)
        if state:
            color = ValidationColors.white.value
        else:
            color = ValidationColors.red.value
        cls.colorize(field, color)

class PresetsValidationColorizer():
    """validator for controls in preset."""
    
    def __init__(self):
        self.controls={}
        """dictionary of validated controls"""
        
    def add(self, key, control):
        """add control for validation"""
        self.control[key] = control
        
    def colorize(self, errors):
        """Colorized associated control and return if any control was colorized"""
        valid = True
        for key, control in self.controls.items():
            if key in errors:                
                ValidationColorizer.colorize_by_validator(control)
                valid = False
        return valid
    
    def reset_colorize(self):
        """Colorized associated control to white"""
        for key, control in self.controls.items():
            ValidationColorizer.colorize_white(control)
