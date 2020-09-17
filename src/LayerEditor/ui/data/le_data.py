import os

from PyQt5.QtCore import QObject

from LayerEditor.ui.data.block_model import BlockModel
from LayerEditor.data.layer_geometry_serializer import LayerGeometrySerializer
from LayerEditor.ui.data.regions_model import RegionsModel
from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene
from LayerEditor.ui.diagram_editor.diagram_view import DiagramView
from gm_base.geometry_files.format_last import InterfaceNodeSet
from gm_base.polygons import polygons_io


class LEData(QObject):
    """Main data class for Layer Editor"""

    # diagrams = []
    # """List of diagram data"""
    # history = None
    # """History for current geometry data"""
    # blocks = []
    # """Blocks structure"""
    # regions = None
    # """Structure for managing regions"""
    # curr_diagram =  None
    # """Current diagram data"""
    # le_serializer = None
    # """Data from geometry file"""
    # curr_file = None
    # """Name of open file"""
    # curr_file_timestamp = None
    # """
    # Timestamp of opened file, if editor text is
    # imported or new timestamp is None
    # """
    # #path = None
    # """Current geometry data file path"""
    # geomop_root = os.path.dirname(os.path.dirname(
    #               os.path.dirname(os.path.realpath(__file__))))
    # """Path to the root directory of the GeoMop installation."""
    # layer_heads = None
    # # Data model for Regions panel.

    def __init__(self, in_file=None):
        super(LEData, self).__init__()
    #     # self.history = GlobalHistory(cls)
    #     # cls.layers = le_data.Layers(cls.history)
    #     # cls.reinit()
    #     self.regions = Regions()
        self.curr_file = in_file
        """Current file (could be moved to config?)."""
        self.blocks = {}  # {topology_id: BlockModel}
        """dict of all blocks in geometry"""
        self.diagram_view = DiagramView()
        """View is common for all layers and blocks."""
        if self.curr_file is None:
            self.curr_file_timestamp = None
        else:
            try:
                self.curr_file_timestamp = os.path.getmtime(in_file)
            except OSError:
                self.curr_file_timestamp = None
        """Timestamp is used for detecting file changes while file is loaded in LE."""

        geo_model = LayerGeometrySerializer(in_file)
        """Access to LayerGeometry."""

        if in_file is None:
            geo_model.set_default_data()

        self.regions = RegionsModel(self, geo_model.get_regions())
        """Manages regions."""

        self.init_blocks(geo_model)

    def init_blocks(self, geo_model):
        for top_idx, top in enumerate(geo_model.get_topologies()):
            self.blocks[top_idx] = BlockModel(self)

        for layer in geo_model.get_layers():
            if isinstance(layer.top, InterfaceNodeSet):
                ns_idx = layer.top.nodeset_id
                node_set = geo_model.get_node_set(ns_idx)
                if node_set.topology_id not in self.diagram_view.scenes:
                    topology = geo_model.get_topologies()[node_set.topology_id]
                    decomp = polygons_io.deserialize(node_set.nodes, topology)
                    self.blocks[node_set.topology_id].decomposition = decomp

                    diagram_scene = DiagramScene(self.blocks[node_set.topology_id],
                                                 self.diagram_view)

                    self.blocks[node_set.topology_id].selection.set_diagram(diagram_scene)
                    self.diagram_view.scenes[node_set.topology_id] = diagram_scene

            top_idx = geo_model.get_gl_topology(layer)
            self.blocks[top_idx].init_add_layer(layer)


    # # def reinit(self):
    # #     """Release all diagram data"""
    # #     self.layer_heads = regions.LayerHeads(self)
    # #     le_data.Diagram.reinit(self.layer_heads, self.history)
    #
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

    # def add_region(self, color, name, reg_id, dim, step, boundary=False, not_used=False):
    #     """Add region"""
    #     self.regions.add_region(color, name, reg_id, dim, step, boundary, not_used)

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
    #
    def changed(cls):
        """is file changed"""
        return False
        #return cls.history.is_changes()

    # @classmethod
    # def add_region(cls, color, name, dim, step,  boundary, not_used):
    #     """Add region"""
    #     le_data.Diagram.add_region(color, name, dim, step,  boundary, not_used)
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
    # def set_curr_diagram(cls, i):
    #     """Set i diagram as edited. Return old diagram id"""
    #     ret = cls.diagram_id()
    #     cls.diagram = cls.diagrams[i]
    #     return ret
    #
    # @classmethod
    # def diagram_id(cls):
    #     """Return current diagram id"""
    #     if not cls.diagram in cls.diagrams:
    #         return None
    #     return cls.diagrams.index(cls.diagram)
    #
    # @classmethod
    # def get_curr_diagram(cls):
    #     """Get id of diagram that is edited."""
    #     return cls.diagrams.index(cls.diagram)
    #
    # @classmethod
    # def insert_diagrams_copies(cls, dup, oper):
    #     """Insert diagrams after set diagram and
    #     move topologies accoding oper"""
    #     for i in range(0, dup.count):
    #         if dup.copy:
    #             cls.diagrams.insert(dup.insert_id, cls.diagrams[dup.insert_id-1].dcopy())
    #         else:
    #             cls.diagrams.insert(dup.insert_id, cls.make_middle_diagram(dup))
    #     if oper is le_data.TopologyOperations.insert:
    #         cls.diagrams[dup.insert_id].move_diagram_topologies(dup.insert_id, cls.diagrams)
    #     elif oper is le_data.TopologyOperations.insert_next:
    #         cls.diagrams[dup.insert_id].move_diagram_topologies(dup.insert_id+1, cls.diagrams)
    #
    # @classmethod
    # def insert_diagrams(cls, diagrams, id, oper):
    #     """Insert diagrams after set diagram and
    #     move topologies accoding oper"""
    #     for i in range(0, len(diagrams)):
    #         cls.diagrams.insert(id+i, diagrams[i])
    #         cls.diagrams[id+i].join()
    #     if oper is le_data.TopologyOperations.insert or \
    #         oper is le_data.TopologyOperations.insert_next:
    #         cls.diagrams[id].move_diagram_topologies(id+len(diagrams), cls.diagrams)
    #
    # @classmethod
    # def remove_and_save_diagram(cls, idx):
    #     """Remove diagram from list and save it in history variable"""
    #     cls.diagrams[idx].release()
    #     cls.history.removed_diagrams.append(cls.diagrams[idx])
    #     curr_id = cls.diagram_id()
    #     del cls.diagrams[idx]
    #     le_data.Diagram.fix_topologies(cls.diagrams)
    #     return curr_id == idx
    #
    # @classmethod
    # def make_middle_diagram(cls, dup):
    #     """return interpolated new diagram in set elevation"""
    #     # TODO: instead copy compute middle diagram
    #     return cls.diagrams[dup.dup1_id].dcopy()
    #
    #
    #
    # @staticmethod
    # def get_current_view(location):
    #     """Return current view"""
    #     return CurrentView(location)
    #
    # @classmethod
    # def set_main(cls, main_window):
    #     """Init class wit static method"""
    #     cls.main_window = main_window
    #     CurrentView.set_cfg(cls)
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

    def make_geo_model(self):
        geo_model = LayerGeometrySerializer()
        region_id_to_idx = self.regions.save(geo_model)
        for block in self.blocks.values():
            block.save(geo_model, region_id_to_idx)


        return geo_model

    def save_file(self, file=None):
        """save to json file"""
        if file is None:
            file = self.curr_file

        self.make_geo_model().save(file)
        #self.history.saved()

        self.curr_file = file
        try:
            self.curr_file_timestamp = os.path.getmtime(file)
        except OSError:
            self.curr_file_timestamp = None

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


    # @classmethod
    # def open_recent_file(cls, file_name):
    #     """
    #     read file from recent files
    #
    #     return: if file have good format (boolean)
    #     """
    #     try:
    #         cls.open_file(file_name)
    #         cls.config.update_current_workdir(file_name)
    #         cls.config.add_recent_file(file_name)
    #         return True
    #     except (RuntimeError, IOError) as err:
    #         if cls.main_window is not None:
    #             err_dialog = GMErrorDialog(cls.main_window)
    #             err_dialog.open_error_dialog("Can't open file", err)
    #         else:
    #             raise err
    #     return False
    #

    def save_to_string(self):
        return self.make_geo_model().save()