from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel, QSlider, QHBoxLayout

from LayerEditor.ui.view_panel.available_overalys_widget import AvailableOverlaysWidget
from LayerEditor.ui.view_panel.overlay_control_widget import OverlayControlWidget


class ViewPanel(QWidget):
    opacity_changed = pyqtSignal(object, float)    # row, value
    def __init__(self, blocks_model, surfaces_model, shapes_model):
        super(ViewPanel, self).__init__()

        layout = QVBoxLayout()
        opacity_control = QWidget()
        opacity_control.setLayout(QHBoxLayout())
        self.opacity_label = QLabel(f"Opacity: 100")
        self.opacity_label.setFixedSize(self.opacity_label.sizeHint())
        self.opacity_label.setText(f"Opacity: 0")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.valueChanged.connect(self.handle_opacity_changed)
        self.opacity_slider.setDisabled(True)
        opacity_control.layout().addWidget(self.opacity_label)
        opacity_control.layout().addWidget(self.opacity_slider)
        opacity_control.layout().setContentsMargins(0, 0, 0, 0)
        layout.addWidget(opacity_control)

        self.overlay_control = OverlayControlWidget(self)
        self.available_overlays = AvailableOverlaysWidget(blocks_model, surfaces_model, shapes_model)
        layout.addWidget(self.overlay_control)
        layout.addWidget(self.available_overlays)
        self.setLayout(layout)

        self.overlay_control.currentItemChanged.connect(self.selected_overlay_changed)

    def opacity_label_text(self, opacity):
        return f"Opacity: {opacity:>3}"

    def handle_opacity_changed(self, opacity):
        self.opacity_label.setText(self.opacity_label_text(opacity))
        self.overlay_control.currentItem().opacity = opacity/100
        self.opacity_changed.emit(self.overlay_control.currentItem().data_item, opacity/100)

    def selected_overlay_changed(self):
        if self.overlay_control.currentItem() is not None:
            opacity = self.overlay_control.currentItem().opacity * 100
            self.opacity_label.setText(self.opacity_label_text(opacity))
            self.opacity_slider.setValue(opacity)
            self.opacity_slider.setDisabled(False)
        else:
            self.opacity_slider.setDisabled(True)

