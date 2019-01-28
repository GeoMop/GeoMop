from LayerEditor.leconfig import cfg


class Selection():
    """
    Selection operations
    """
    def __init__(self):
        self.selected = {}
        # Dict (dim, shape_id): shape


    def select(self, shape):
        dim = shape.dim
        id = shape.id
        shape_id = (dim, id)
        if not shape_id in self.selected:
            self.selected[shape_id] = shape
            shape.object.select()
        else:
            del self.selected[shape_id]
            shape.object.deselect()

    def select_point(self, point):
        """set point as selected"""
        self.select(point)


    def select_line(self, line, with_points):
        """set line as selected"""
        if not line in self.selected_lines:
            self.selected_lines.append(line)
            line.object.select_line()
            if with_points:
                self._select_point_if_lines_selected(line.p1)
                self._select_point_if_lines_selected(line.p2)
        else:
            self.selected_lines.remove(line)
            line.object.deselect_line()
            if with_points:
                self._select_point_if_lines_selected(line.p1)
                self._select_point_if_lines_selected(line.p2)

    def select_line(self, line):
        """ Select line with end points."""

    def _select_point_if_lines_selected(self, point):
        """select point if neighboring lines are selected"""
        all = True
        for line in point.lines:
            if line not in self.selected_lines:
                all = False
                break
        if all:
            if point not in self.selected_points:
                self.select_point(point)
        else:
            if point in self.selected_points:
                self.select_point(point)

    def select_polygon(self, polygon):
        """set polygon as selected"""
        if not polygon in self.selected_polygons:
            self.selected_polygons.append(polygon)
            polygon.object.select_polygon()
        else:
            self.selected_polygons.remove(polygon)
            polygon.object.deselect_polygon()

    def select_all(self):
        """select all items"""
        for shapes in [cfg.diagram.points, cfg.diagram.lines, cfg.diagram.polygons]:
            for shape in shapes:
                self.select(shape, select=True)

    def select_current_region(self):
        """select items which have set current region"""
        reg_id = cfg.layer_heads.selected_region_id

        for shapes in [cfg.diagram.points, cfg.diagram.lines, cfg.diagram.polygons]:
            for shape in shapes:
                if shape.get_region() == reg_id:
                    self.select(shape)

    def deselect_selected(self):
        """deselect all items"""
        for shapes in [cfg.diagram.points, cfg.diagram.lines, cfg.diagram.polygons]:
            for shape in shapes:
                self.select(shape, select=False)

    def get_selected_regions(self, diagram):
        """ For all layers of set diagram return:
            - selected region, if selected shapes have same regions and dimensions
            - previous point return applies to the highest dimension shape in case of mismatch
            - or None region if regions of the highest dimension are different
        """
        # ret = None
        # default = diagram.get_default_regions()
        # for selected in [self.selected_points, self.selected_lines, self.selected_polygons]:
        #     if selected:
        #         ret = None
        #         #
        #         for shape in selected:
        #             shape_regions = shape.get_regions()
        #             # regions in all layers of the same topology
        #             if ret is None:
        #                 ret = shape_regions
        #             else:
        #                 for i in range (0, len(default)):
        #                     if ret[i] != shape_regions[i]:
        #                         ret[i] = default[i]
        # if ret is None:
        #     return default

        """
        If exactly one shape is selected return all regions in block layers.
        """
        if len(self.selected) == 1:
            shape =  [self.selected.values()][0]
            return shape.get_regions()
        else:
            return None

    def delete_selected(self):
        """
        delete selected,
        returns list of objects to remove from diagram panel,
        if some objects in selection have associated region only sets all objects to None region
        """
        with_region = False
        for point in self.selected_points:
            if point.set_default_region():
                point.object.update_color()
                with_region = True
        for line in self.selected_lines:
            if line.set_default_region():
                line.object.update_color()
                with_region = True
        for polygon in self.selected_polygons:
            if polygon.set_default_region():
                polygon.object.update_color()
                with_region = True
        if with_region:
            return []

        objects_to_remove = []
        first = True
        for line in self.selected_lines:
            line_object = line.object
            line_object.release_line()
            objects_to_remove.append(line_object)
            if first:
                cfg.diagram.delete_line(line, "Delete selected")
                first = False
            else:
                cfg.diagram.delete_line(line, None)
        self.selected_lines = []
        removed = []
        for point in self.selected_points:
            if first:
                label = "Delete selected"
                first = False
            else:
                label = None
            if cfg.diagram.try_delete_point(point, label):
                point_object = point.object
                point_object.release_point()
                objects_to_remove.append(point_object)
                removed.append(point)
        for point in removed:
            self.selected_points.remove(point)
        return objects_to_remove

    def set_current_region(self):
        """
        Set region of selected shapes to current regions where dimension match.
        Restrict selection to these shapes
        """
        selected_region = cfg.layer_heads.selected_region
        layer_id = cfg.layer_heads.current_layer_id
        for shape in self.selected.values():
            if selected_region.cmp_shape_dim(layer_id, shape.dim):
                shape.set_region(selected_region)
                point.set_current_region
                shape.object.update_color()
            else:
                # deselect
                self.select(shape)


    def is_empty(self):
        """returns True if no shape selected"""
        return self.selected

    def max_selected_dim(self):
        if self.selected:
            return max([ dim for dim, id in self.selected.keys()])
        else:
            return 0