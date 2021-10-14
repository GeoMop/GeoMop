from PyQt5.QtWidgets import QGraphicsItem


class AbstractGraphicsItem(QGraphicsItem):
    def enable_editing(self):
        raise NotImplemented

    def disable_editing(self):
        raise NotImplemented

    def update_item(self):
        raise NotImplemented

    @property
    def data_item(self):
        raise NotImplemented