from PyQt5 import QtCore
from PyQt5.QtCore import QPointF
from .resize_handle import ResizeHandle


class RectResizeHandles:
    def __init__(self, parent, width):
        self.parent = parent
        self.handles = []

        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.top_left))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.top_middle))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.top_right))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.middle_left))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.middle_right))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.bottom_left))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.bottom_middle))
        self.handles.append(ResizeHandle(self, parent, width, ResizeHandle.bottom_right))

    def update_handles(self):
        """Update current resize handles according to the shape size and position."""
        for handle in self.handles:
            handle.update_handle()


