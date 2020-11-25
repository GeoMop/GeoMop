from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter, QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy

from LayerEditor.ui.layers_panel.editable_text import EditableText
from LayerEditor.ui.layers_panel.menu.fracture_menu import FractureMenu


class InterfaceType:
    BOTH = 0
    BOTTOM = 1
    TOP = 2
    NONE = 3

class WGInterface(QWidget):
    """Widget for Layers Panel which represents an interface or fracture layer"""
    def __init__(self, parent, fracture_layer=None, placement=InterfaceType.BOTH):
        """Placement selects joining line on left."""
        super(WGInterface, self).__init__()
        self._parent = parent
        self.fracture_layer = fracture_layer
        self.le_model = parent.le_model
        self.placement = placement
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        if fracture_layer is not None:
            self.name = EditableText(fracture_layer.name)
            self.name.text_label.setContentsMargins(5, 0, 5, 0)
            palette = self.name.palette()
            color = palette.color(QPalette.Window)
            self.name.setStyleSheet(f"QLabel {{background: {color.name()}}};")
            layout = QHBoxLayout()
            layout.setContentsMargins(15, 0, 15, 0)
            layout.addWidget(self.name, alignment=Qt.AlignCenter)
            self.setLayout(layout)
            self.name.text_edit.textChanged.connect(self.name_changed)
            self.name.text_edit.editingFinished.connect(self.name_finished)

            self.menu = FractureMenu()
            self.menu.rename_fracture_action.triggered.connect(self.rename)
            self.menu.remove_fracture_action.triggered.connect(self.remove)
        else:
            self.name = None
            self.setMinimumHeight(QLabel().sizeHint().height())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if (event.button() == Qt.RightButton or event.button() == Qt.LeftButton) and self.name is not None:
            self.menu.exec_(event.globalPos())

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(WGInterface, self).paintEvent(a0)
        painter = QPainter(self)
        painter.setPen(self._parent.LINE_PEN)
        center = self.rect().center()
        start = QPoint(self.rect().left() + self._parent.LINE_WIDTH * 0.5, center.y())

        painter.drawLine(start, QPoint(self.rect().right(), center.y()))

        if self.placement == InterfaceType.NONE:
            return

        if self.placement in [InterfaceType.TOP, InterfaceType.BOTH]:
            painter.drawLine(start,
                             self.rect().bottomLeft() + QPoint(self._parent.LINE_WIDTH * 0.5, 0))
        if self.placement in [InterfaceType.BOTTOM, InterfaceType.BOTH]:
            painter.drawLine(start,
                             self.rect().topLeft() + QPoint(self._parent.LINE_WIDTH * 0.5, 0))

    def name_changed(self, new_name):
        new_name = new_name.strip()
        unique = self.le_model.is_layer_name_unique(new_name)
        if new_name == self.fracture_layer.name or unique:
            self.name.text_edit.mark_text_valid()
            self.name.setToolTip("")
        else:
            self.name.text_edit.mark_text_invalid()
            self.name.setToolTip("This name already exist")

    def name_finished(self):
        new_name = self.name.text_edit.text().strip()
        if self.le_model.is_layer_name_unique(new_name) and new_name != self.fracture_layer.name:
            self.fracture_layer.set_name(new_name)
            self._parent.update_layers_panel()
        else:
            self.name.text_edit.setText(self.fracture_layer.name)
            self.name.finish_editing()
            self.name.setToolTip("")

    def rename(self):
        self.name.start_editing()

    def remove(self):
        self.le_model.delete_layer(self.fracture_layer)
