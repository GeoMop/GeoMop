from bgem.polygons.polygons import PolygonDecomposition

from LayerEditor.ui.tools import undo


class LEDecomposition(PolygonDecomposition):
    def __init__(self):
        super(LEDecomposition, self).__init__()
        self.block = None

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


