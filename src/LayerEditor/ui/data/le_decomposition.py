from gm_base.polygons import polygons_io
from bgem.polygons.polygons import PolygonDecomposition

from LayerEditor.ui.tools import undo
import gm_base.geometry_files.format_last as gs


class LEDecomposition(PolygonDecomposition):
    def __init__(self, nodes=None, topology=None):
        super(LEDecomposition, self).__init__()
        if nodes is not None and topology is not None:
            self.deserialize(nodes, topology)
        self.block = None

    def empty(self):
        if not self.points and not self.segments and len(self.polygons) == 1:
            return True
        else:
            return False

    def new_point(self, pos, last_point):
        """Add continuous line and point, from self.last_point
        - **parameters**
            :pos: pos of new point
            :last_point: point from which the line begins
        """
        with undo.group("Added Point"):
            pt = self.add_point((pos.x(), -pos.y()))
            #self.block.init_regions_for_new_shape(0, pt.id)

            split_shapes_after_point = []

            if last_point is not None:
                split_shapes_after_point = list(self.last_split_shapes)
                for seg in self.add_line_for_points(last_point.pt, pt):
                    self.block.init_regions_for_new_shape(1, seg.id)
                    # for poly_id in self.polygons:
                    #     if poly_id != 0:
                    #         self.block.init_regions_for_new_shape(2, poly_id)

            for dim, id_old, id_new in self.last_split_shapes + split_shapes_after_point:
                # if some shape was split then copy region to the new shape
                if dim == 2 and id_old == 0:
                    continue
                for layer in self.block.layers_dict.values():
                    region = layer.get_shape_region(dim, id_old)
                    layer.set_region_to_shape(dim, id_new, region)

            self.initialize_regions()

            return pt

    def initialize_regions(self):
        """Initializes regions for all shapes which dont have defined regions. If region is defined it is ignored."""
        for dim in range(3):
            for item_id in self.decomp.shapes[dim]:
                self.block.init_regions_for_new_shape(dim, item_id)

    def delete_items(self, items):
        """Delete all points and segments"""
        with undo.group("Delete selected"):
            for dim, id in items:
                if dim == 1:
                    self.delete_segment(self.segments[id])

            for dim, id in items:
                if dim == 0:
                    self.delete_point(self.points[id])

    def copy_itself(self):
        """ Make new decomposition with identical topology and nodeset as this.
            Ids will change, so everything that uses shape ids needs to be updated using old_to_new_id"""
        receiver = undo.stack()._receiver
        nodes, topology = self.serialize()

        old_to_new_id = [{}, {}, {}]
        for dim in range(3):
            for shape in self.decomp.shapes[dim].values():
                old_to_new_id[dim][shape.id] = shape.index

        cpy = LEDecomposition(nodes, topology)

        cpy.block = self.block
        undo.stack().setreceiver(receiver)
        return cpy, old_to_new_id

    # Moved here from polygon_io.py
    def serialize(self):
        return polygons_io.serialize(self)

    def deserialize(self, nodes, topology):
        polgon_decomp = polygons_io.deserialize(nodes, topology)
        for key, value in polgon_decomp.__dict__.items():
            self.__dict__[key] = value
