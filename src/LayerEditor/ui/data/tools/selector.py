from PyQt5.QtCore import pyqtSignal, QObject


class Selector(QObject):
    """ Used for selecting one item(value) from list.
        Also used to check if selected item is still in iterable object.
        If not than select other item that is part of iterable"""
    value_changed = pyqtSignal(object)  # old_value
    """signal is emitted whenever value is changed"""

    def __init__(self, value):
        super(Selector, self).__init__()
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        old_value = self._value
        if value is not self._value:
            self._value = value
            self.value_changed.emit(old_value)

    def validate(self, lst: list) -> bool:
        """Check if selected item is still in the list. If not select first item in the list.
            return: True if `value` was valid, False if value was changed."""
        if self.value not in lst:
            if len(lst) == 0:
                self.value = None
            else:
                self.value = lst[0]
            return False
        else:
            return True

