from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QDialog

from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.layers_panel.dialogs.split_layer import SplitLayerDlg
from LayerEditor.ui.layers_panel.menu.layer_menu import LayerMenu


class WGLayer(QWidget):
    """Widget for Layers Panel which represents layer"""
    def __init__(self, parent, layer: LayerItem):
        super(WGLayer, self).__init__(parent)
        self._parent = parent
        self.le_model = parent.le_model
        self.layer = layer
        self.name = QLabel(layer.name)
        self.name.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout()
        layout.addWidget(self.name, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        layout.setContentsMargins(5, 0, 5, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.menu = LayerMenu()
        self.menu.split_action.triggered.connect(self.split_layer)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(WGLayer, self).paintEvent(a0)
        painter = QPainter(self)
        painter.setPen(self._parent.LINE_PEN)
        x = self.rect().left() + self._parent.LINE_WIDTH / 2
        painter.drawLine(x, self.rect().top(), x, self.rect().bottom())

    def split_layer(self):
        top_y = self.layer.top_in.interface.elevation
        bot_y = self.layer.bottom_in.interface.elevation
        dlg = SplitLayerDlg(top_y, bot_y, self.le_model.layer_names())
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            name = dlg.layer_name.text()
            elevation = float(dlg.elevation.text())
            self.le_model.split_layer(self.layer, name, elevation)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.RightButton or event.button() == Qt.LeftButton:
            self.menu.exec_(event.globalPos())

