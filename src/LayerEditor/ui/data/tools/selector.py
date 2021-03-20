

class Selector:
    """ Used for selecting one item(value) from list.
        Also used to check if selected item is still in iterable object.
        If not than select other item that is part of iterable"""
    def __init__(self, value):
        self.value = value
        self.old_value = None

    def validate(self, lst: list) -> bool:
        """Check if selected item is still in the list. If not select first item in the list.
            return: True if `value` was valid, False if value was changed."""
        if self.value not in lst:
            self.old_value = self.value
            if len(lst) == 0:
                self.value = None
            else:
                self.value = lst[0]
            return False
        else:
            return True

