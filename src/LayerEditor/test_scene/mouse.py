import enum
from PyQt5.QtCore import  Qt


class Event(enum.IntEnum):
    Left = Qt.LeftButton
    Right = Qt.RightButton
    Middle = Qt.MiddleButton
    NoMod = Qt.NoModifier
    Shift = Qt.ShiftModifier
    Ctrl = Qt.ControlModifier
    Alt = Qt.AltModifier

