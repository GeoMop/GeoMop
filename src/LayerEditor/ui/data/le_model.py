import os

from PyQt5.QtCore import QObject, QPointF, pyqtSignal
from PyQt5.QtGui import QPolygonF

from LayerEditor.ui.data.block_item import BlockItem
from LayerEditor.ui.data.le_decomposition import LEDecomposition
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
    _layers_changed = pyqtSignal()
    """The structure of layers and interfaces was changed"""
    scenes_changed = pyqtSignal(int, bool)
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

        self.init_area = QPolygonF([QPointF(point[0], -point[1]) for point in geo_model.supplement.init_area]).boundingRect()
        """Initialization area (polygon x,y coordinates) for scene"""
        self.init_zoom_pos_data = geo_model.supplement.zoom
        """Used only for initializing DiagramView after that is None and DiagramView holds those informations"""

        self.gui_curr_block = self.decompositions_model.decomps[geo_model.supplement.last_node_set].block
        """helper attribute, holds currently active block"""

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
            self.gui_curr_block.gui_selected_layer.set_gui_selected_region(reg)
            self.emit_region_list_changed()
            self.emit_invalidate_scene()
        return reg

    def delete_region(self, reg):
        with undo.group("Delete new region"):
            self.regions_model.delete_region(reg)
            self.emit_region_list_changed()
            self.emit_invalidate_scene()

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
            self.emit_layer_changed()

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
            self.emit_layer_changed()

    def delete_layer(self, layer: LayerItem):
        with undo.group("Delete Layer"):
            if len(layer.block.layers_dict) == 1:
                self._delete_block(layer.block)
            else:
                layer.block.delete_layer(layer)
                self.emit_layer_changed()


    def delete_block(self, block: BlockItem):
        with undo.group("Delete Block"):
            self._delete_block(block)

    def _delete_block(self, block: BlockItem):
        """Deletes block and all decompositions. Must be used inside `undo.group()`"""
        for i_node_set in block.get_interface_node_sets():
            self.decompositions_model.delete_decomposition(i_node_set.decomposition)
        self.blocks_model.delete_block(block)

        self.emit_layer_changed()
        self.emit_scenes_changed(block, False)

    # @classmethod
    # def reload_surfaces(cls, id=None):
    #     """Reload surface panel"""
    #     if cls.main_window is not None:
    #         cls.main_window.wg_surface_panel.change_surface(id)
    #
    # @classmethod
    # def get_curr_surfaces(cls):
    #     """Get current surface id from surface panel"""
    #     return  cls.main_window.wg_surface_panel.get_surface_id()
    #
    # @classmethod
    # def add_shapes_to_region(cls, is_fracture, layer_id, layer_name, topology_idx, regions):
    #     """Add shape to region"""
    #     le_data.Diagram.add_shapes_to_region(is_fracture, layer_id, layer_name, topology_idx, regions)
    #
    # @classmethod
    # def get_shapes_from_region(cls, is_fracture, layer_id):
    #     """Get shapes from region"""
    #     return le_data.Diagram.get_shapes_from_region(is_fracture, layer_id)
    #
    # @classmethod
    # def open_shape_file(cls, file):
    #     """Open and add shape file"""
    #     if cls.diagram is not None:
    #         if not cls.diagram.shp.is_file_open(file):
    #             try:
    #                 disp = cls.diagram.add_file(file)
    #                 if len(disp.errors)>0:
    #                     err_dialog = GMErrorDialog(cls.main_window)
    #                     err_dialog.open_error_report_dialog(disp.errors, msg="Shape file parsing errors:" ,  title=file)
    #                 return True
    #             except Exception as err:
    #                 err_dialog = GMErrorDialog(cls.main_window)
    #                 err_dialog.open_error_dialog("Can't open shapefile", err)
    #     return False

    def save(self):
        geo_model = LayerGeometry()
        geo_model.version = [0, 5, 5]
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

        self.surfaces_model.clear_indexing()
        self.decompositions_model.clear_indexing()
        self.regions_model.clear_indexing()
        self.interfaces_model.clear_indexing()
        return geo_model

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
        geo_model.version = [0, 5, 5]

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
        with undo.group("Split Layer"):
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

            self.emit_layer_changed()

    def prepend_layer(self, first_layer: LayerItem, new_layer_name: str, elevation: float):
        """ Prepends layer before firs_layer
            :first_layer: must be first layer in block"""
        with undo.group("Split Layer"):
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

            self.emit_layer_changed()


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

            new_layer = LayerItem(layer.block,
                                  new_layer_name,
                                  middle_it_node_set,
                                  bottom_in,
                                  shape_regions)

            self.blocks_model.blocks[layer.block].add_layer(new_layer)

            self.emit_layer_changed()

    def add_fracture_layer(self, i_node_set, layer_name=None):
        with undo.group("Add Fracture"):
            self._add_fracture_layer(i_node_set, layer_name)

    def _add_fracture_layer(self, i_node_set, layer_name=None):
        """ Add fracture to interface specified by InterfaceNodeSetItem/InterpolatedNodeSetItem.
            Must be used inside `undo.group()`"""
        if layer_name is None:
            layer_name = "Fracture_1"
            idx = 2
            while not self.is_layer_name_unique(layer_name):
                layer_name = f"Fracture_{idx}"
                idx += 1

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
        self.emit_layer_changed()

        return new_layer

    def add_fracture_to_new_block(self, i_node_set, layer_name=None):
        with undo.group("Add Fracture to its own Surface"):
            new_block = BlockItem(self.regions_model)
            self.blocks_model.add_block(new_block)

            decomp, old_to_new_id = i_node_set.block.decomposition.copy_itself()
            decomp.block = new_block

            self.decompositions_model.add_decomposition(decomp)

            new_in = InterfaceNodeSetItem(decomp, i_node_set.interface)

            new_layer = self._add_fracture_layer(new_in, layer_name)
            new_block.gui_selected_layer = new_layer

            self.emit_layer_changed()
            self.emit_scenes_changed(new_block, added=True)

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
            selected_idx = layers.index(old_block.gui_selected_layer)
            if selected_idx >= idx:
                old_block.gui_selected_layer = layers[0]
            new_block = BlockItem(self.regions_model)
            new_block.gui_selected_layer = layer_below
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

            self.emit_layer_changed()
            self.emit_scenes_changed(new_block, added=True)

    def change_curr_block(self, block):
        old_block = self.gui_curr_block
        self.gui_curr_block = block
        self.active_block_changed.emit(old_block.id)

    @undo.undoable
    def emit_layer_changed(self):
        self._layers_changed.emit()
        yield "Layers change signal emitted"
        self._layers_changed.emit()

    @undo.undoable
    def emit_invalidate_scene(self):
        self.invalidate_scene.emit()
        yield "Layers change signal emitted"
        self.invalidate_scene.emit()

    @undo.undoable
    def emit_region_list_changed(self):
        self.region_list_changed.emit()
        yield "Layers change signal emitted"
        self.region_list_changed.emit()

    @undo.undoable
    def emit_scenes_changed(self, block, added=True):
        self.scenes_changed.emit(block.id, added)
        yield "Scene " + ("added" if added else "deleted") + "signal emitted"
        self.scenes_changed.emit(block.id, not added)
