from enum import IntEnum
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

class ItemStates(IntEnum):
    """Item states"""
    standart = 0
    selected = 1
    moved = 2
    added = 3
    
def get_state_color(state):
    """return color for set state"""
    if state == ItemStates.added:
        return QtGui.QColor(QtCore.Qt.darkGreen)
    else:
        return QtGui.QColor(QtCore.Qt.black)

    # color = QtGui.QColor(QtCore.Qt.black)
    # if state ==  ItemStates.selected:
    #     color = QtGui.QColor(QtCore.Qt.black)
    # elif state ==  ItemStates.moved:
    #     color = QtGui.QColor(QtCore.Qt.black)
    # elif state ==  ItemStates.added:
    #     color = QtGui.QColor(QtCore.Qt.darkGreen)
    # return color
