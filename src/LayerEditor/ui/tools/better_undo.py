from bgem.external import undo

class _Group(undo._Group):
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._stack:
            return super(_Group, self).__exit__(exc_type, exc_val, exc_tb)
        return False


def group(desc):
    return _Group(desc)
