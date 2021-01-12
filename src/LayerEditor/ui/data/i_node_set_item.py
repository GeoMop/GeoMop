

class INodeSetItem:
    def __init__(self, interface):
        self.interface = interface
        """InterfaceItem defining surface (elevation)"""

    @property
    def decomposition(self):
        assert False, "Abstract function! Must be overridden by child class!"

    @property
    def block(self):
        return self.decomposition.block



