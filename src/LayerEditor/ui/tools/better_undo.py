"""Extends and improves `undo`"""

from bgem.external import undo

class _Group(undo._Group):
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ This modification will not add empty group to stack.
            Empty group was still one action and undoing empty group did nothing."""
        if self._stack:
            return super(_Group, self).__exit__(exc_type, exc_val, exc_tb)
        elif exc_type is None:
            undo.stack().resetreceiver()
        return False


def group(desc):
    return _Group(desc)


__savepoint = None
"""Stores saved action for detecting if there have been new changes"""

def savepoint():
    """Store top action from `undo.stack()` for determining whether there has been changes."""
    global __savepoint
    if undo.stack().undocount() > 0:
        __savepoint = undo.stack()._undos[-1]
    else: __savepoint = None


def has_changed(savepoint=None):
    """ Default savepoint only keeps track of number of undos in stack. That is not good enough!!!
        This improvement keeps track of which action was on top of stack and compares it with current top,
        or with provided parameter `savepoint`.
        return: False if `savepoint` or top of `undo.stack()` is the same as `__savepoint`. True otherwise"""

    if undo.stack()._undos:
        if savepoint is None:
            if __savepoint is None:
                return True
            else:
                return __savepoint is not undo.stack()._undos[-1]
        else:
            return savepoint is not undo.stack()._undos[-1]
    else:
        return False


def clear():
    """Clear extra info in this extension"""
    global __savepoint
    undo.stack().clear()
    __savepoint = None