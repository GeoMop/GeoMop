from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QDialog, QLineEdit

from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.layers_panel.dialogs.split_layer import SplitLayerDlg
from LayerEditor.ui.layers_panel.editable_text import EditableText
from LayerEditor.ui.layers_panel.menu.layer_menu import LayerMenu


class WGLayer(QWidget):
    """Widget for Layers Panel which represents layer"""
    def __init__(self, parent, layer: LayerItem):
        super(WGLayer, self).__init__(parent)
        self._parent = parent
        self.le_model = parent.le_model
        self.layer = layer
        self.name = EditableText(self, layer.name)
        self.name.setCursor(Qt.PointingHandCursor)
        self.name.text_edit.editingFinished.connect(self.name_finished)
        self.name.text_edit.textChanged.connect(self.text_changed)

        layout = QHBoxLayout()
        layout.addWidget(self.name, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        layout.setContentsMargins(5, 0, 5, 0)

        self.menu = LayerMenu(self.le_model, self.layer)
        self.menu.split_action.triggered.connect(self.split_layer)
        self.menu.rename_action.triggered.connect(self.name.start_editing)
        self.menu.del_layer_top.triggered.connect(self.del_layer_top)
        self.menu.del_layer_bot.triggered.connect(self.del_layer_bot)
        self.menu.del_block_action.triggered.connect(self.del_block)

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

    def text_changed(self, new_name):
        new_name = new_name.strip()
        unique = self.is_layer_name_unique(new_name)
        if unique is None or unique:
            self.name.text_edit.mark_text_valid()
            self.name.setToolTip("")
        else:
            self.name.text_edit.mark_text_invalid()
            self.name.setToolTip("This name already exist")

    def name_finished(self):
        new_name = self.name.text_edit.text().strip()
        if self.is_layer_name_unique(new_name):
            self.layer.set_name(new_name)
            self._parent.update_layers_panel()
        else:
            self.name.text_edit.setText(self.layer.name)
            self.name.finish_editing()
            self.name.setToolTip("")

    def is_layer_name_unique(self, new_name):
        """ Is new layer name unique?
            :return: True if new name is unique, False if it is not unique, None if new name is the same as old name"""
        if self.layer.name == new_name:
            return None
        else:
            for name in self.le_model.layer_names():
                if name == new_name:
                    return False
            return True

    def del_layer_top(self):
        self.le_model.delete_layer_top(self.layer)

    def del_layer_bot(self):
        self.le_model.delete_layer_bot(self.layer)

    def del_block(self):
        # TODO: was not able to test this testa when blocks can be created
        self.le_model.delete_block(self.layer.block)


