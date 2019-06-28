"""
Special action which can contain subactions for repeating processes.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from frontend.analysis.util.rect_resize_handles import RectResizeHandles
from frontend.analysis.graphical_items.g_action import GAction
from PyQt5 import QtCore


class GActionForSubactions(GAction):
    """Base class for actions which contain subactions."""
    def __init__(self, parent=None, position=QtCore.QPoint(0, 0)):
        """
        :param parent: Action which holds this subaction: this action is inside parent action.
        :param position: Position of this action.
        """
        super(GActionForSubactions, self).__init__(parent, position)
        self.name = "While loop"
        self.width = 200
        self.height = 200
        # Add resize handles to GActio.
        self.resize_handle_width = 6
        self.resize_handles = RectResizeHandles(self, self.resize_handle_width, self.resize_handle_width * 2)

    @GAction.width.setter
    def width(self, value):
        super(GActionForSubactions, self).width(value)
        self.resize_handles.update_handles()

    @GAction.height.setter
    def height(self, value):
        super(GActionForSubactions, self).height(value)
        self.resize_handles.update_handles()