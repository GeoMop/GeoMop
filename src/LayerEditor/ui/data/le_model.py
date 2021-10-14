import os

from PyQt5.QtCore import QObject, QPointF, pyqtSignal
from PyQt5.QtGui import QPolygonF

from LayerEditor.ui.data.block_layers_model import BlockLayersModel
from LayerEditor.ui.data.shp_structures import ShapesModel
from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.data.tools.selector import Selector
from LayerEditor.ui.tools import undo

from LayerEditor.exceptions.data_inconsistent_exception import DataInconsistentException
from LayerEditor.ui.data.blocks_model import BlocksModel
from LayerEditor.ui.data.interface_item import InterfaceItem
from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.interfaces_model import InterfacesModel
from LayerEditor.ui.data.decompositions_model import DecompositionsModel
from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.data.regions_model import RegionsModel
from LayerEditor.ui.data.surfaces_model import SurfacesModel
from gm_base.geometry_files import layers_io
from gm_base.geometry_files.format_last import InterfaceNodeSet, LayerGeometry, NodeSet, Region, RegionDim, Interface, \
    InterpolatedNodeSet, StratumLayer, Topology


class LEModel(QObject):
    """Main data class for Layer Editor"""
    region_list_changed = pyqtSignal()
    """Regions were added or deleted"""
    invalidate_scene = pyqtSignal()
    """The scene needs to be updated"""
    layers_changed = pyqtSignal()
    """The structure of layers and interfaces was changed"""
    scenes_changed = pyqtSignal()
    """ Scene created or deleted
        carries block id of the scene and True if scene was created or False if scene was deleted"""
    active_block_changed = pyqtSignal(int)
    """ curr_block was changed, so scene has to be changed (plus maybe other stuff)
        param holds id of the previous curr block"""

    def __init__(self, in_file=None):
        super(LEModel, self).__init__()
        geo_model, self.curr_file_timestamp = self.load_geo_model(in_file)

        self.curr_file = in_file
        """Current file (could be moved to config?)."""
        self.decompositions_model = DecompositionsModel(geo_model.node_sets, geo_model.topologies)
        """Manages decompositions, this is similar to self.node_sets in format last"""

        self.surfaces_model = SurfacesModel(geo_model.surfaces)
        """Manages surfaces"""
        self.interfaces_model = InterfacesModel(self, geo_model.interfaces)
        """Manages interfaces"""
        self.regions_model = RegionsModel(self, geo_model.regions)
        """Manages regions."""
        self.blocks_model = BlocksModel(geo_model, self)
        """Manages blocks."""
        self.shapes_model = ShapesModel(geo_model.supplement.shps)

        self.init_area = QPolygonF([QPointF(point[0], -point[1]) for point in geo_model.supplement.init_area]).boundingRect()
        """Initialization area (polygon x,y coordinates) for scene"""
        self.init_zoom_pos_data = geo_model.supplement.zoom
        """Used only for initializing DiagramView after that is None and DiagramView holds those informations"""

        self.gui_block_selector = Selector(self.decompositions_model.decomps[geo_model.supplement.last_node_set].block)
        """helper attribute, holds currently active block"""
        if geo_model.supplement.surface_idx is None:
            self.gui_surface_selector = Selector(None)
        else:
            self.gui_surface_selector = Selector(self.surfaces_model.surfaces[geo_model.supplement.surface_idx])
        """helper attribute, holds currently active surface"""

    def validate_selectors(self):
        for block in self.blocks_model.blocks.values():
            block.validate_selectors()

        if not self.gui_block_selector.validate(self.blocks_model.get_sorted_blocks()):
            self.active_block_changed.emit(self.gui_block_selector.old_value.id)

    def load_geo_model(self, in_file=None):
        if in_file is None:
            geo_model = self.make_default_geo_model()
        else:
            geo_model = layers_io.read_geometry(in_file)
            errors = self.check_geo_model_consistency(geo_model)
            if len(errors) > 0:
                raise DataInconsistentException(
                    "Some file consistency errors occure in {0}".format(in_file), errors)

        if in_file is None:
            curr_file_timestamp = None
        else:
            try:
                curr_file_timestamp = os.path.getmtime(in_file)
            except OSError:
                curr_file_timestamp = None
        """Timestamp is used for detecting file changes while file is loaded in LE."""
        return (geo_model, curr_file_timestamp)

    def is_layer_name_unique(self, new_name):
        """ Is new layer name unique?
            :return: True if new name is unique, False if it is not unique"""
        for name in self.layer_names():
            if name == new_name:
                return False
        return True

    def get_default_layer_name(self, prefix):
        """ Set default layer name to QLineEdit. """
        lay_id = 1
        name = prefix + f"_{lay_id}"
        while not self.is_layer_name_unique(name):
            lay_id += 1
            name = prefix + f"_{lay_id}"
        return name

    def layer_names(self):
        r = []
        for block in self.blocks_model.blocks.values():
            r.extend(block.layer_names)
        return r

    def confront_file_timestamp(self):
        """
        Compare file timestamp with file time and if is diferent
        show dialog, and reload file content.
        :return: if file is reloaded
        """
        if self.curr_file_timestamp is not None and \
            self.curr_file is not None:
            try:
                timestamp = os.path.getmtime(self.curr_file)
                if timestamp!=self.curr_file_timestamp:
                    from PyQt5 import QtWidgets
                    msg = QtWidgets.QMessageBox()
                    msg.setText(
                        "File has been modified outside of Layer editor. Do you want to reload it?")
                    msg.setStandardButtons( QtWidgets.QMessageBox.Ignore | \
                        QtWidgets.QMessageBox.Reset)
                    msg.button(QtWidgets.QMessageBox.Reset).setText("Reload")
                    msg.setDefaultButton(QtWidgets.QMessageBox.Ignore)
                    ret = msg.exec_()
                    if ret==QtWidgets.QMessageBox.Reset:
                        with open(self.curr_file, 'r') as file_d:
                            self.document = file_d.read()
                        self.curr_file_timestamp = timestamp
                        return True
            except OSError:
                pass
        return False

    def add_region(self, reg):
        with undo.group("Add new region"):
            self.regions_model.add_region(reg)
            self.gui_block_selector.value.gui_layer_selector.value.set_gui_selected_region(reg)
        self.region_list_changed.emit()
        self.invalidate_scene.emit()
        return reg

    def delete_region(self, reg):
        with undo.group("Delete new region"):
            self.regions_model.delete_region(reg)
        self.region_list_changed.emit()
        self.invalidate_scene.emit()

    def is_region_used(self, reg):
        """Returns True if reg is assigned to any shape in any layer in any block"""
        for block in self.blocks_model.blocks.values():
            for layer in block.layers_dict.values():
                dim = self.regions_model.regions[reg].dim
                if layer.is_stratum:
                    dim -= 1
                    if dim < 0:
                        continue
                else:
                    if dim == 3:
                        continue
                if reg in layer.shape_regions[dim].values():
                    return True
        return False

    def delete_layer_top(self, layer):
        """ Delete specified layer and top interface.
            Layer above deleted layer (if it exists) will be extended to bottom interface of deleted layer.
            There must be at least one stratum layer above specified layer in parameter(fracture layer doesn't count)"""
        with undo.group("Delete layer and extend the layer above"):
            layers = layer.block.get_sorted_layers()
            idx = layers.index(layer)
            if idx != 0 or (idx == 1 and layers[idx - 1].is_stratum):
                if layers[idx - 1].is_stratum:
                    above_layer = layers[idx - 1]
                else:
                    layer.block.delete_layer(layers[idx - 1])
                    above_layer = layers[idx - 2]
                above_layer.set_bottom_in(layer.bottom_in)
            self.interfaces_model.delete_itf(layer.top_in.interface)
            layer.block.delete_layer(layer)
        self.layers_changed.emit()

    def delete_layer_bot(self, layer):
        """ Delete specified layer and bottom interface.
            Layer below deleted layer (if it exists) will be extended to top interface of deleted layer.
            There must be at least one stratum layer below specified layer (fracture layer doesn't count)"""
        with undo.group("Delete layer and extend the layer below"):
            layers = layer.block.get_sorted_layers()
            idx = layers.index(layer)
            if idx != len(layers) - 1 or ((idx == len(layers) - 2) and layers[idx + 1].is_stratum):
                if layers[idx + 1].is_stratum:
                    below_layer = layers[idx + 1]
                else:
                    layer.block.delete_layer(layers[idx + 1])
                    below_layer = layers[idx + 2]
                below_layer.set_top_in(layer.top_in)
            self.interfaces_model.delete_itf(layer.bottom_in.interface)
            layer.block.delete_layer(layer)
        self.layers_changed.emit()

    def delete_layer(self, layer: LayerItem):
        if len(layer.block.layers_dict) == 1:
            self.delete_block(layer.block)
        else:
            with undo.group("Delete Layer"):
                layer.block.delete_layer(layer)
            self.layers_changed.emit()

    def delete_block(self, block: BlockLayersModel):
        with undo.Group("Delete Block"):
            for i_node_set in block.get_interface_node_sets():
                self.decompositions_model.delete_decomposition(i_node_set.decomposition)
            self.blocks_model.delete_block(block)

        self.layers_changed.emit()
        self.scenes_changed.emit()

    def save(self):
        geo_model = LayerGeometry()
        geo_model.version = [0, 5, 6]
        surfaces = self.surfaces_model.save()
        geo_model.surfaces = surfaces
        node_sets, topologies = self.decompositions_model.save()
        geo_model.topologies = topologies
        geo_model.node_sets = node_sets
        regions_data = self.regions_model.save()
        geo_model.regions = regions_data
        interfaces_data = self.interfaces_model.save()
        geo_model.interfaces = interfaces_data
        geo_model.layers = self.blocks_model.save()

        last_node_set = self.decompositions_model.decomps.index(self.gui_block_selector.value.decomposition)

        if self.gui_surface_selector.value in self.surfaces_model.surfaces:
            curr_surf_idx = self.surfaces_model.surfaces.index(self.gui_surface_selector.value)
        else:
            curr_surf_idx = None

        shps = self.shapes_model.serialize()

        supplement_config = {"last_node_set": last_node_set,
                             "surface_idx": curr_surf_idx,
                             "shps": shps}

        self.surfaces_model.clear_indexing()
        self.decompositions_model.clear_indexing()
        self.regions_model.clear_indexing()
        self.interfaces_model.clear_indexing()
        return geo_model, supplement_config

    @classmethod
    def open_file(cls, file):
        """
        save file name and timestamp
        """
        cls.main_window.release_data(cls.diagram_id())
        cls.curr_file = file
        cls.config.update_current_workdir(file)
        if file is None:
            cls.curr_file_timestamp = None
        else:
            try:
                cls.curr_file_timestamp = os.path.getmtime(file)
            except OSError:
                cls.curr_file_timestamp = None
        cls.history.remove_all()
        cls.le_serializer.load(cls, file)
        cls.main_window.refresh_all()
        cls.config.add_recent_file(file)

    @staticmethod
    def check_geo_model_consistency(geo_model):
        """check created file consistency"""
        errors = []
        for ns_idx in range(0, len(geo_model.node_sets)):
            ns = geo_model.node_sets[ns_idx]
            topology_idx = ns.topology_id
            if topology_idx < 0 or topology_idx >= len(geo_model.topologies):
                errors.append("Topology {} is out of geometry topologies range 0..{}".format(
                    topology_idx, len(geo_model.topologies) - 1))

        # topology test
        curr_top = geo_model.node_sets[0].topology_id
        used_top = [curr_top]
        for ns in geo_model.node_sets:
            if curr_top != ns.topology_id:
                curr_top = ns.topology_id
                if curr_top in used_top:
                    errors.append("Topology {} is in more that one block.".format(curr_top))
                else:
                    used_top.append(curr_top)
        return errors

    @staticmethod
    def make_default_geo_model():
        geo_model = LayerGeometry()
        geo_model.version = [0, 5, 6]

        lname = "Layer_1"
        default_region = Region(dict(color="gray", name="NONE", not_used=True, dim=RegionDim.none))
        geo_model.regions.append(default_region)

        regions = ([], [], [0])  # No node, segment, polygon or regions.
        inter = Interface(dict(elevation=0.0, surface_id=None))
        inter.transform_z = [1.0, 0.0]
        geo_model.interfaces.append(inter)
        ns_top = InterfaceNodeSet(dict(nodeset_id=0, interface_id=0))

        inter = Interface(dict(elevation=-100.0, surface_id=None))
        inter.transform_z = [1.0, 0.0]
        geo_model.interfaces.append(inter)

        ns_bot = InterpolatedNodeSet(dict(surf_nodesets=(ns_top, ns_top), interface_id=1))

        gl = StratumLayer(dict(name=lname, top=ns_top, bottom=ns_bot))
        gl.node_region_ids = regions[0]
        gl.segment_region_ids = regions[1]
        gl.polygon_region_ids = regions[2]
        geo_model.layers.append(gl)

        geo_model.topologies.append(Topology())
        geo_model.node_sets.append(NodeSet(dict(topology_id=0, nodes=[])))
        geo_model.supplement.last_node_set = 0
        return geo_model

    def append_layer(self, last_layer: LayerItem, new_layer_name: str, elevation: float):
        """ Appends layer after last_layer
            :last_layer: must be last layer in block"""
        with undo.group("Append Layer"):
            if last_layer.is_stratum:
                top_in = last_layer.bottom_in
            else:
                top_in = last_layer.top_in
            top_itf = top_in.interface
            bot_itf = InterfaceItem(elevation)
            self.interfaces_model.insert_after(bot_itf, top_itf)

            if top_in.is_interpolated:
                bot_in = InterpolatedNodeSetItem(top_in.top_itf_node_set, top_in.bottom_itf_node_set, bot_itf)
            else:
                bot_in = InterpolatedNodeSetItem(top_in, top_in, bot_itf)

            shape_regions = [dict(last_layer.shape_regions[0]),
                             dict(last_layer.shape_regions[1]),
                             dict(last_layer.shape_regions[2])]

            new_layer = LayerItem(last_layer.block,
                                  new_layer_name,
                                  top_in,
                                  bot_in,
                                  shape_regions)

            self.blocks_model.blocks[last_layer.block].add_layer(new_layer)
        self.layers_changed.emit()

    def prepend_layer(self, first_layer: LayerItem, new_layer_name: str, elevation: float):
        """ Prepends layer before firs_layer
            :first_layer: must be first layer in block"""
        with undo.group("Prepend Layer"):
            bot_in = first_layer.top_in
            bot_itf = bot_in.interface
            top_itf = InterfaceItem(elevation)
            self.interfaces_model.insert_before(top_itf, bot_itf)

            if bot_in.is_interpolated:
                top_in = InterpolatedNodeSetItem(bot_in.top_itf_node_set, bot_in.bottom_itf_node_set, top_itf)
            else:
                top_in = InterpolatedNodeSetItem(bot_in, bot_in, top_itf)
                top_in = InterpolatedNodeSetItem(bot_in, bot_in, top_itf)

            shape_regions = [dict(first_layer.shape_regions[0]),
                             dict(first_layer.shape_regions[1]),
                             dict(first_layer.shape_regions[2])]

            new_layer = LayerItem(first_layer.block,
                                  new_layer_name,
                                  top_in,
                                  bot_in,
                                  shape_regions)

            self.blocks_model.blocks[first_layer.block].add_layer(new_layer)
        self.layers_changed.emit()

    def split_layer(self, layer: LayerItem, new_layer_name: str, elevation: float):
        with undo.group("Split Layer"):
            new_itf = InterfaceItem(elevation)
            self.interfaces_model.insert_after(new_itf, layer.top_in.interface)
            bottom_in = layer.bottom_in

            if isinstance(bottom_in, InterpolatedNodeSetItem):
                middle_it_node_set = InterpolatedNodeSetItem(bottom_in.top_itf_node_set,
                                                             bottom_in.bottom_itf_node_set,
                                                             new_itf)

            elif isinstance(layer.top_in, InterpolatedNodeSetItem):
                middle_it_node_set = InterpolatedNodeSetItem(layer.top_in.top_itf_node_set,
                                                             layer.top_in.bottom_itf_node_set,
                                                             new_itf)
            else:
                middle_it_node_set = InterpolatedNodeSetItem(layer.top_in, layer.bottom_in, new_itf)

            layer.set_bottom_in(middle_it_node_set)

            shape_regions = [dict(layer.shape_regions[0]),
                             dict(layer.shape_regions[1]),
                             dict(layer.shape_regions[2])]

            new_layer = LayerItem(None,
                                  new_layer_name,
                                  middle_it_node_set,
                                  bottom_in,
                                  shape_regions)

            self.blocks_model.blocks[layer.block].add_layer(new_layer)
        self.layers_changed.emit()

    def add_fracture_layer(self, i_node_set, layer_name=None):
        with undo.group("Add Fracture"):
            self._add_fracture_layer(i_node_set, layer_name)
        self.layers_changed.emit()

    def _add_fracture_layer(self, i_node_set, layer_name=None):
        """ Add fracture to interface specified by InterfaceNodeSetItem/InterpolatedNodeSetItem.
            Must be used inside `undo.group()`"""
        if layer_name is None:
            layer_name = self.get_default_layer_name("Fracture")

        shape_regions = [{}, {}, {}]
        for dim in range(3):
            for shape in i_node_set.get_shapes()[dim].values():
                shape_regions[dim][shape.id] = RegionItem.none

        new_layer = LayerItem(i_node_set.block,
                              layer_name,
                              i_node_set,
                              None,
                              shape_regions)

        self.blocks_model.blocks[i_node_set.block].add_layer(new_layer)
        return new_layer

    def add_fracture_to_new_block(self, i_node_set, layer_name=None):
        with undo.group("Add Fracture to its own Surface"):
            new_block = BlockLayersModel(self.regions_model)
            self.blocks_model.add_block(new_block)

            decomp, old_to_new_id = i_node_set.block.decomposition.copy_itself()
            decomp.block = new_block

            self.decompositions_model.add_decomposition(decomp)

            new_in = InterfaceNodeSetItem(decomp, i_node_set.interface)

            new_layer = self._add_fracture_layer(new_in, layer_name)
            new_block.gui_layer_selector.value = new_layer
            self.scenes_changed.emit()
            self.layers_changed.emit()

    def split_interface(self, i_node_set, layer_below, layer_above):
        with undo.group("Split Interface"):
            old_block = i_node_set.block
            if isinstance(i_node_set, InterfaceNodeSetItem):
                top_decomp = i_node_set.decomposition
                bot_decomp, old_to_new_id = top_decomp.copy_itself()
            else:
                top_decomp = i_node_set.bottom_itf_node_set.decomposition
                bot_decomp, old_to_new_id = top_decomp.copy_itself()

            layers = old_block.get_sorted_layers()
            idx = layers.index(layer_below)
            selected_idx = layers.index(old_block.gui_layer_selector.value)
            if selected_idx >= idx:
                old_block.gui_layer_selector.value = layers[0]
            new_block = BlockLayersModel(self.regions_model)
            new_block.gui_layer_selector.value = layer_below
            for layer in layers[idx:]:
                old_block.delete_layer(layer)
                new_block.add_layer(layer)

            if len(new_block.get_interface_node_sets()) == 0:
                new_i_node_set = InterfaceNodeSetItem(bot_decomp, i_node_set.interface)
                layer_below.set_top_in(new_i_node_set)
                for layer in new_block.layers_dict.values():
                    layer.update_shape_ids(old_to_new_id)
                    if layer is not layer_below:
                        layer.set_top_in(InterpolatedNodeSetItem(new_i_node_set,
                                                                 new_i_node_set,
                                                                 layer.top_in.interface))
                    if layer.is_stratum:
                        layer.set_bottom_in(InterpolatedNodeSetItem(new_i_node_set,
                                                                    new_i_node_set,
                                                                    layer.bottom_in.interface))
            elif len(old_block.get_interface_node_sets()) == 0:
                new_i_node_set = InterfaceNodeSetItem(top_decomp, i_node_set.interface)
                layer_above.set_bottom_in(new_i_node_set)
                for layer in old_block.layers_dict.values():
                    layer.set_top_in(InterpolatedNodeSetItem(new_i_node_set,
                                                           new_i_node_set,
                                                           layer.top_in.interface))
                    if layer is not layer_above and layer.is_stratum:
                        layer.set_bottom_in(InterpolatedNodeSetItem(new_i_node_set,
                                                                    new_i_node_set,
                                                                    layer.bottom_in.interface))
                for layer in new_block.layers_dict.values():
                    layer.update_shape_ids(old_to_new_id)
                    layer.top_in.change_decomposition(bot_decomp, bot_decomp)
                    if layer.is_stratum:
                        layer.bottom_in_in.change_decomposition(bot_decomp, bot_decomp)

            else:
                assert False, "This should not happen. Unless there can be more than 1 decomposition in block."

            self.blocks_model.add_block(new_block)

            bot_decomp.block = new_block
            self.decompositions_model.add_decomposition(bot_decomp)

            self.layers_changed.emit()
            self.scenes_changed.emit()

    def add_surface(self, surf: SurfaceItem):
        self.surfaces_model.add_surface(surf)

    def delete_surface(self, surf):
        for itf in self.interfaces_model.interfaces:
            if itf.surface is surf:
                return False
        self.surfaces_model.delete_surface(surf)
        return True

    def change_curr_block(self, block=None):
        """Changes currently active block to `block`. If `block` is None the first block will be used."""
        if block is None:
            block = self.blocks_model.get_sorted_blocks()[0]
        if block is not self.gui_block_selector.value:
            old_block = self.gui_block_selector.value
            self.gui_block_selector.value = block
            self.active_block_changed.emit(old_block.id)

    def add_shape_file(self, filename):
        if not self.shapes_model.is_file_open(filename):
            shp_item = self.shapes_model.add_file(filename)
            return shp_item.errors
        return None

    def decompositions_empty(self, ignore_shapes=False, ignore_surf=False, ignore_decomps=False):
        if not ignore_shapes and not self.shapes_model.is_empty():
            return False
        if not ignore_surf and not self.surfaces_model.is_empty():
            return False
        if not ignore_decomps:
            for decomp in self.decompositions_model.decomps:
                if not decomp.empty():
                    return False
        return True



