from LayerEditor.data.layer_geometry_serializer import LayerGeometrySerializer
from LayerEditor.ui.data.region import Region
from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import StratumLayer, LayerType, FractureLayer, TopologyType, InterfaceNodeSet


class LayerModel(IdObject):
    """Data about one geological layer"""
    def __init__(self, decomposition, regions_dict, layer_data=None):
        self.decomposition = decomposition
        """Decomposition of this layer. For now each layer in the same block has the same decomposition"""
        self.name = layer_data.name
        """Layer name"""
        self.top_top = layer_data.top
        """Top topology"""
        self.bottom_top = layer_data.__dict__.get("bottom")
        """Bottom topology if layer is fracture always None"""
        self.shape_regions = [{}, {}, {}]
        """[{point_id: region_id}, {seg_id: region_id}, {poly_id: region_id}]"""
        """Regions of shapes grouped by dimension"""
        self._init_regions_ids(layer_data, regions_dict)

        ######### Not undoable ########### Not undoable ########## Not undoable ##########
        self.gui_selected_region = Region.none
        """Default region for new objects in diagram. Also used by LayerHeads for RegionsPanel"""
        """Not undoable"""

        self.is_fracture = isinstance(layer_data, FractureLayer)
        """Is this layer fracture layer?"""
        self.is_stratum = isinstance(layer_data, StratumLayer)
        """Is this layer stratum layer?"""

    def _init_regions_ids(self, layer_data, regions_dict):
        for shape_id, region_id in enumerate(layer_data.node_region_ids):
            self.shape_regions[0][shape_id] = regions_dict.get(region_id)

        for shape_id, region_id in enumerate(layer_data.segment_region_ids):
            self.shape_regions[1][shape_id] = regions_dict.get(region_id)

        for shape_id, region_id in enumerate(layer_data.polygon_region_ids):
            self.shape_regions[2][shape_id] = regions_dict.get(region_id)

    def save(self, geo_model: LayerGeometrySerializer, region_id_to_idx: dict):
        if self.is_stratum:
            type = LayerType.stratum
            bottom_top = self.bottom_top
            # TODO: this seems to be obsolete, because in format_last bottom_type and top_type are commented
            if isinstance(self.bottom_top, InterfaceNodeSet):
                bottom_type = TopologyType.given
            else:
                bottom_type = TopologyType.interpolated
        elif self.is_fracture:
            type = LayerType.fracture
            bottom_type = None
            bottom_top = None
        else:
            type = LayerType.shadow
            bottom_type = None
            bottom_top = None

        shape_region_idx = ([], [], [])
        for point in sorted(self.decomposition.points.values(), key=lambda x: x.index):
            region = self.shape_regions[0][point.id]
            shape_region_idx[0].append(region_id_to_idx[region.id])

        for seg in sorted(self.decomposition.segments.values(), key=lambda x: x.index):
            region = self.shape_regions[1][seg.id]
            shape_region_idx[1].append(region_id_to_idx[region.id])

        for poly in sorted(self.decomposition.polygons.values(), key=lambda x: x.index):
            region = self.shape_regions[2][poly.id]
            shape_region_idx[2].append(region_id_to_idx[region.id])


        if isinstance(self.top_top, InterfaceNodeSet):
            top_type = TopologyType.given
        else:
            top_type = TopologyType.interpolated

        geo_model.add_GL(self.name,
                    type,
                    shape_region_idx,
                    top_type,
                    self.top_top,
                    bottom_type,
                    bottom_top)