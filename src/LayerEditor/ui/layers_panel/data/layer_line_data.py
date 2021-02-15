

class LayerLineData:
    """Helper data object for better readability of LayersPanel initialization"""
    def __init__(self, layer):
        self.layer = layer
        self.top_del_enable = False
        self.bottom_del_enable = False