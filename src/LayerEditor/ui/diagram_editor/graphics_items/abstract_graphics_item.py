from PyQt5.QtWidgets import QGraphicsItem


class AbstractGraphicsItem(QGraphicsItem):
    def enable_editing(self):
        pass

    def disable_editing(self):
        pass