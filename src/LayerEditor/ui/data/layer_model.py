from gm_base.geometry_files.format_last import StratumLayer, LayerType, FractureLayer


class LayerModel:
    """Data about one geologycal layer"""
    def __init__(self, layer_data):
        self.layer_data = layer_data
        """For now just save raw data from LayerGeometry"""