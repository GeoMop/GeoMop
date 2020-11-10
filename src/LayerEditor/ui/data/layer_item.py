from collections import deque

from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import StratumLayer, FractureLayer


class LayerItem(IdObject):
    """Data about one geological layer"""
    def __init__(self, block, name, top_in, bottom_in, shape_regions):

        self.block = block
        """This layer is part of this block"""
        self.name = name
        """Layer name"""
        self.top_in = top_in
        """Top InterfaceNodeSetItem/InterpolatedNodeSetItem"""
        self.bottom_in = bottom_in
        """Bottom InterfaceNodeSetItem/InterpolatedNodeSetItem if layer is fracture always None"""
        self.shape_regions = shape_regions
        """[{point_id: region_object}, {seg_id: region_object}, {poly_id: region_object}]"""
        """Regions of shapes grouped by dimension"""

        ######### Not undoable ########### Not undoable ########## Not undoable ##########
        self.gui_selected_region = RegionItem.none
        """Default region for new objects in diagram. Also used by LayerHeads for RegionsPanel"""
        """Not undoable"""

        self.is_stratum = self.bottom_in is not None
        """Is this layer stratum layer?"""


    def save(self):
        layer_config = dict(name=self.name, top=self.top_in.save())
        shape_region_idx = ([], [], [])
        if isinstance(self.top_in, InterfaceNodeSetItem):
            decomp = self.top_in.decomposition
        else:
            decomp = self.top_in.top_itf_node_set.decomposition

        for dim in range(3):
            for shape in sorted(decomp.decomp.shapes[dim].values(), key=lambda x: x.index):
                region = self.shape_regions[dim][shape.id]
                shape_region_idx[dim].append(region.index)
        layer_config["node_region_ids"] = shape_region_idx[0]
        layer_config["segment_region_ids"] = shape_region_idx[1]
        layer_config["polygon_region_ids"] = shape_region_idx[2]

        if self.is_stratum:
            layer_config['bottom'] = self.bottom_in.save()
            gl = StratumLayer(layer_config)
        else:
            gl = FractureLayer(layer_config)

        return gl

    def set_region_to_selected_shapes(self, region: RegionItem):
        """Sets regions of shapes only in this layer."""
        assert isinstance(undo.stack()._receiver, deque), "groups cannot be nested"
        with undo.group(f"Set region of selected to {region.id}"):
            for orig_dim, shape_id in self.block.selection.get_selected_shape_dim_id():
                dim = orig_dim
                if self.is_stratum:
                    dim += 1
                if dim == region.dim or region.dim == -1:
                    self.set_region_to_shape(orig_dim, shape_id, region)

    def get_shape_region(self, dim, shape_id) -> RegionItem:
        return self.shape_regions[dim][shape_id]

    @undo.undoable
    def set_region_to_shape(self, dim, shape_id, region: RegionItem):
        old_region = self.shape_regions[dim].get(shape_id, RegionItem.none)
        self.shape_regions[dim][shape_id] = region
        shape = ["point", "segment", "polygon"]
        yield f"Change region of {shape[dim]} {shape_id} from {old_region.id} to {region.id}"
        self.set_region_to_shape(dim, shape_id, old_region)

    @undo.undoable
    def set_gui_selected_region(self, region: RegionItem):
        """Use this when you want this to be included in undo/redo system"""
        old_region = self.gui_selected_region
        self.gui_selected_region = region
        yield f"Selected region {region.id} on layer {self.id} changed. Old region {old_region.id}"
        self.gui_selected_region = old_region

    @undo.undoable
    def set_bottom_in(self, new_in):
        """Sets new bottom InterfaceNodeSetItem/InterpolatedNodeSetItem"""
        old_ni = self.bottom_in
        self.bottom_in = new_in
        yield f"bottom_ni changed in layer {self.id}"
        self.set_bottom_in(old_ni)