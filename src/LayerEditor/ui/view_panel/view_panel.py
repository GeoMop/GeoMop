from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel, QSlider, QHBoxLayout

from LayerEditor.ui.view_panel.available_overalys_widget import AvailableOverlaysWidget
from LayerEditor.ui.view_panel.overlay_control_widget import OverlayControlWidget


class ViewPanel(QWidget):
    def __init__(self, blocks_model, surfaces_model, shapes_model):
        super(ViewPanel, self).__init__()

        layout = QVBoxLayout()
        opacity_control = QWidget()
        opacity_control.setLayout(QHBoxLayout())
        self.opacity_label = QLabel(f"Opacity: 100")
        self.opacity_label.setFixedSize(self.opacity_label.sizeHint())
        self.opacity_label.setText(f"Opacity: 0")
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setMaximum(100)
        opacity_slider.valueChanged.connect(self.opacity_changed)
        opacity_control.layout().addWidget(self.opacity_label)
        opacity_control.layout().addWidget(opacity_slider)
        opacity_control.layout().setContentsMargins(0, 0, 0, 0)
        layout.addWidget(opacity_control)

        self.overlay_control = OverlayControlWidget(self)
        self.available_overlays = AvailableOverlaysWidget(blocks_model, surfaces_model, shapes_model)
        layout.addWidget(self.overlay_control)
        layout.addWidget(self.available_overlays)
        self.setLayout(layout)

    def opacity_changed(self, value):
        self.opacity_label.setText(f"Opacity: {value:>3}")
        # Todo: Change opacity of currently selected overlay layer
