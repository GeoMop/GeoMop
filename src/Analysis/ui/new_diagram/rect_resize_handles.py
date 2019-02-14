from PyQt5 import QtCore
from PyQt5.QtCore import QPointF
from .resize_handle import ResizeHandle


class RectResizeHandles:
    ALL_HANDLES = 255
    HORIZONTAL_HANDLES = ResizeHandle.top_middle | ResizeHandle.bottom_middle
    VERTICAL_HANDLES = ResizeHandle.middle_left | ResizeHandle.middle_right
    NO_CORNERS = HORIZONTAL_HANDLES | VERTICAL_HANDLES

    def __init__(self, parent, size, corner_size, options=ALL_HANDLES):
        self.parent = parent
        self.handles = []

        self.top_middle_corners = False
        self.left_middle_corners = False
        self.bot_middle_corners = False
        self.right_middle_corners = False

        if options & ResizeHandle.top_left:
            self.top_middle_corners = True
            self.left_middle_corners = True
        if options & ResizeHandle.top_right:
            self.top_middle_corners = True
            self.right_middle_corners = True
        if options & ResizeHandle.bottom_left:
            self.bot_middle_corners = True
            self.left_middle_corners = True
        if options & ResizeHandle.bottom_right:
            self.bot_middle_corners = True
            self.right_middle_corners = True

        if options & ResizeHandle.top_left:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.top_left, corner_size))

        if options & ResizeHandle.top_middle:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.top_middle,
                                             corner_size, self.top_middle_corners))

        if options & ResizeHandle.top_right:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.top_right, corner_size))

        if options & ResizeHandle.middle_left:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.middle_left,
                                             corner_size, self.left_middle_corners))

        if options & ResizeHandle.middle_right:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.middle_right,
                                             corner_size, self.right_middle_corners))

        if options & ResizeHandle.bottom_left:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.bottom_left, corner_size))

        if options & ResizeHandle.bottom_middle:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.bottom_middle,
                                             corner_size, self.bot_middle_corners))

        if options & ResizeHandle.bottom_right:
            self.handles.append(ResizeHandle(self, parent, size, ResizeHandle.bottom_right, corner_size))

    def update_handles(self):
        """Update current resize handles according to the shape size and position."""
        for handle in self.handles:
            handle.update_handle()


