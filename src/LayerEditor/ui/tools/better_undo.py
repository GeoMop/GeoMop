from bgem.external import undo

class _Group(undo._Group):
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._stack:
            return super(_Group, self).__exit__(exc_type, exc_val, exc_tb)
        elif exc_type is None:
            undo.stack().resetreceiver()
        return False


def group(desc):
    return _Group(desc)


__savepoint = None


def savepoint():
    global __savepoint
    if undo.stack().undocount() > 0:
        __savepoint = undo.stack()._undos[-1]
    else: __savepoint = None


def has_changed(savepoint=None):

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
    global __savepoint
    undo.stack().clear()
    __savepoint = None