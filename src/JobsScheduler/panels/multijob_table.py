#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class UiMultijobTable(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
