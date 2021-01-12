from gm_base.polygons import polygons_io
from bgem.polygons.polygons import PolygonDecomposition

from LayerEditor.ui.tools import undo
import gm_base.geometry_files.format_last as gs


class LEDecomposition:
    def __init__(self, nodes=None, topology=None):
        self.poly_decomp = PolygonDecomposition()
        if nodes is not None and topology is not None:
            self.deserialize(nodes, topology)
        self.block = None

    @property
    def points(self):
        return self.poly_decomp.points

    @property
    def segments(self):
        return self.poly_decomp.segments

    @property
    def polygons(self):
        return self.poly_decomp.polygons

    def empty(self):
        if not self.poly_decomp.points and not self.poly_decomp.segments and len(self.poly_decomp.polygons) == 1:
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
            pt = self.poly_decomp.add_point((pos.x(), -pos.y()))
            #self.block.init_regions_for_new_shape(0, pt.id)

            split_shapes_after_point = []

            if last_point is not None:
                split_shapes_after_point = list(self.poly_decomp.last_split_shapes)
                for seg in self.poly_decomp.add_line_for_points(last_point.pt, pt):
                    self.block.init_regions_for_new_shape(1, seg.id)

            for dim, id_old, id_new in self.poly_decomp.last_split_shapes + split_shapes_after_point:
                # if some shape was split then copy region to the new shape
                if dim == 2 and id_old == 0:
                    # skip root polygon
                    continue
                for layer in self.block.layers_dict.values():
                    region = layer.get_shape_region(dim, id_old)
                    layer.set_region_to_shape(dim, id_new, region)

            self.initialize_regions()

            return pt

    def initialize_regions(self):
        """Initializes regions for all shapes which dont have defined regions. If region is defined it is ignored."""
        for dim in range(3):
            for item_id in self.poly_decomp.decomp.shapes[dim]:
                self.block.init_regions_for_new_shape(dim, item_id)

    def delete_items(self, items):
        """Delete all points and segments"""
        with undo.group("Delete selected"):
            for dim, id in items:
                if dim == 1:
                    self.poly_decomp.delete_segment(self.poly_decomp.segments[id])

            for dim, id in items:
                if dim == 0:
                    self.poly_decomp.delete_point(self.poly_decomp.points[id])

    def copy_itself(self):
        """ Make new decomposition with identical topology and nodeset as this.
            Ids will change, so everything that uses shape ids needs to be updated using old_to_new_id"""
        receiver = undo.stack()._receiver   # bgem changes the receiver which is not desired this fixes it
        nodes, topology = self.serialize()

        old_to_new_id = [{}, {}, {}]
        for dim in range(3):
            for shape in self.poly_decomp.decomp.shapes[dim].values():
                old_to_new_id[dim][shape.id] = shape.index

        cpy = LEDecomposition(nodes, topology)

        cpy.block = self.block
        undo.stack().setreceiver(receiver)  # bgem changes the receiver which is not desired this fixes it
        return cpy, old_to_new_id

    # Moved here from polygon_io.py
    def serialize(self):
        return polygons_io.serialize(self)

    def deserialize(self, nodes, topology):
        polgon_decomp = polygons_io.deserialize(nodes, topology)
        for key, value in polgon_decomp.__dict__.items():
            self.__dict__[key] = value
