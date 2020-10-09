from collections import deque

from bgem.external import undo

from LayerEditor.ui.data.region import Region
from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment
from LayerEditor.ui.tools import better_undo
from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import StratumLayer, LayerType, FractureLayer, TopologyType, InterfaceNodeSet, \
    ShadowLayer, InterpolatedNodeSet


class LayerModel(IdObject):
    """Data about one geological layer"""
    def __init__(self, block, regions_dict, layer_data=None):
        self.block = block
        """This layer is part of this block"""
        self.decomposition = block.decomposition
        """Decomposition of this layer. For now each layer in the same block has the same decomposition"""
        self.name = layer_data.name
        """Layer name"""
        self.top_top = layer_data.top
        """Top topology"""
        self.bottom_top = layer_data.__dict__.get("bottom")
        """Bottom topology if layer is fracture always None"""
        self.shape_regions = [{}, {}, {}]
        """[{point_id: region_object}, {seg_id: region_object}, {poly_id: region_object}]"""
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

    def save(self, region_id_to_idx: dict):
        layer_config = dict(name=self.name, top=self.top_top)
        if self.is_stratum:
            layer_class = StratumLayer
            layer_config['bottom'] = self.bottom_top
        elif self.is_fracture:
            layer_class = FractureLayer
        else:
            layer_class = ShadowLayer

        shape_region_idx = ([], [], [])
        for dim in range(3):
            for shape in sorted(self.decomposition.decomp.shapes[dim].values(), key=lambda x: x.index):
                region = self.shape_regions[dim][shape.id]
                shape_region_idx[dim].append(region_id_to_idx[region.id])

        gl = layer_class(layer_config)
        gl.node_region_ids = shape_region_idx[0]
        gl.segment_region_ids = shape_region_idx[1]
        gl.polygon_region_ids = shape_region_idx[2]
        return gl

    def set_region_to_selected_shapes(self, region: Region):
        """Sets regions of shapes only in this layer."""
        assert isinstance(undo.stack()._receiver, deque), "groups cannot be nested"
        with better_undo.group(f"Set region of selected to {region.id}"):
            for g_item in self.block.selection._selected:
                dim = g_item.dim
                if self.is_stratum:
                    dim += 1
                if dim == region.dim or region.dim == -1:
                    self.set_region_to_shape(g_item, region)

    def get_shape_region(self, g_item: [GsPoint, GsSegment, GsPolygon]) -> Region:
        return self.shape_regions[g_item.dim][g_item.shape_id]

    @undo.undoable
    def set_region_to_shape(self, g_item: [GsPoint, GsSegment, GsPolygon], region: Region):
        old_region = self.shape_regions[g_item.dim].get(g_item.shape_id, Region.none)
        self.shape_regions[g_item.dim][g_item.shape_id] = region
        shape = ["point", "segment", "polygon"]
        yield f"Change region of {shape[g_item.dim]} {g_item.shape_id} from {old_region.id} to {region.id}"
        self.set_region_to_shape(g_item, old_region)

    @undo.undoable
    def set_gui_selected_region(self, region: Region):
        """Use this when you want this to be included in undo/redo system"""
        old_region = self.gui_selected_region
        self.gui_selected_region = region
        yield f"Selected region {region.id} on layer {self.id} changed. Old region {old_region.id}"
        self.gui_selected_region = old_region
