from PyQt5.QtWidgets import QListWidgetItem


class OverlayListItem(QListWidgetItem):
    def __init__(self, data_item, opacity=1):
        super(OverlayListItem, self).__init__(data_item.overlay_name)
        self.data_item = data_item
        self.opacity = opacity

