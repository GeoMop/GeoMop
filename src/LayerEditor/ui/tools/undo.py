"""Extends and improves `undo`"""

from bgem.external.undo import *
from bgem.external.undo import _Group, _Action


class Group(_Group):
    def __init__(self, desc, undo_callback=lambda: None, do_callback=lambda: None):
        """ Added possibility to specify function which gets called after undoing/redoing the group.
            This serves mainly for emitting signals, which need to be emitted after changes.
            If do_callback is None the same function will be used as for undo_callback"""
        super(Group, self).__init__(desc)
        self.undo_callback = undo_callback
        if do_callback is None:
            self.do_callback = undo_callback
        else:
            self.do_callback = do_callback

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ This modification will not add empty group to stack.
            Empty group was still one action and undoing empty group did nothing."""
        if self._stack:
            self.do_callback()
            return super(Group, self).__exit__(exc_type, exc_val, exc_tb)

        elif exc_type is None:
            stack().resetreceiver()
        return False

    def undo(self):
        super(Group, self).undo()
        self.undo_callback()

    def do(self):
        super(Group, self).do()
        self.do_callback()


def group(desc, undo_callback=lambda: None, do_callback=lambda: None) -> Group:
    """ If the function which should be done after undo/redo is the same just pass None to do_callback.
        undo_callback: Function which gets called after undoing group.
        do_callback: Function which gets called after redoing group or None if this function is the same as undo_callback"""
    return Group(desc, undo_callback, do_callback)


__savepoint = None
"""Stores saved action for detecting if there have been new changes"""

def savepoint():
    """Store top action from `undo.stack()` for determining whether there has been changes."""
    global __savepoint
    if stack().undocount() > 0:
        __savepoint = stack()._undos[-1]
    else: __savepoint = None


def has_changed(savepoint=None):
    """ Default savepoint only keeps track of number of undos in stack. That is not good enough!!!
        This improvement keeps track of which action was on top of stack and compares it with current top,
        or with provided parameter `savepoint`.
        return: False if `savepoint` or top of `undo.stack()` is the same as `__savepoint`. True otherwise"""

    if stack()._undos:
        if savepoint is None:
            if __savepoint is None:
                return True
            else:
                return __savepoint is not stack()._undos[-1]
        else:
            return savepoint is not stack()._undos[-1]
    else:
        return False


def clear():
    """Clear extra info in this extension"""
    global __savepoint
    stack().clear()
    __savepoint = None