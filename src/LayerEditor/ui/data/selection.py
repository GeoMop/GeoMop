from leconfig import cfg


class Selection():
    """
    Selection operations
    """
    def __init__(self):
        self.selected_points = []
        """list of selected points"""
        self.selected_lines = []
        """list of selected lines"""
        self.selected_polygons = []
        """list of selected polygons"""

    def select_point(self, point):
        """set point as selected"""
        if not point in self.selected_points:
            self.selected_points.append(point)
            point.object.select_point()
        else:
            self.selected_points.remove(point)
            point.object.deselect_point()

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
        for line in cfg.diagram.lines:
            if line not in self.selected_lines:
                self.select_line(line, False)
        for point in cfg.diagram.points:
            if point not in self.selected_points:
                self.select_point(point)
        for polygon in cfg.diagram.polygons:
            if polygon not in self.selected_polygons:
                self.select_polygon(polygon)

    def select_current_region(self):
        """select items which have set current region"""
        regions = cfg.diagram.regions
        region = regions.current_regions[regions.current_layer_id]
        reg_ind = regions.regions.index(region)
        for line in cfg.diagram.lines:
            if line.get_region() == reg_ind:
                self.select_line(line, False)
        for point in cfg.diagram.points:
            if point.get_region() == reg_ind:
                self.select_point(point)
        for polygon in cfg.diagram.polygons:
            if polygon.get_region() == reg_ind:
                self.select_polygon(polygon)

    def deselect_selected(self):
        """deselect all items"""
        for line in self.selected_lines:
           line.object.deselect_line()
        for point in self.selected_points:
            point.object.deselect_point()
        for polygon in self.selected_polygons:
            polygon.object.deselect_polygon()
        self.selected_points = []
        self.selected_lines = []
        self.selected_polygons = []
        
    def get_selected_regions(self, diagram):
        """ For all layers of set diagram return: 
            - selected region, if selected shapes have same regions
            - or None region if regions is different
        """
        ret = None
        default = diagram.get_default_regions()
        for selected in [self.selected_points, self.selected_lines, self.selected_polygons]:
            for shape in selected:
                next =  shape.get_regions()
                if ret is None:
                    ret = next
                else:
                    for i in range (0, len(default)):
                        if ret[i]!=next[i]:
                            ret[i]=default[i]
        if ret is None:
            return default
        return ret

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
        set current region to selected shapes of appropriate dimension,
        restricts selection to this shapes
        """
        for point in self.selected_points.copy():
            if point.set_current_region():
                point.object.update_color()
            else:
                self.select_point(point)
        for line in self.selected_lines.copy():
            if line.set_current_region():
                line.object.update_color()
            else:
                self.select_line(line, False)
        for polygon in self.selected_polygons.copy():
            if polygon.set_current_region():
                polygon.object.update_color()
            else:
                self.select_polygon(polygon)

    def is_empty(self):
        """returns True if no shape selected"""
        return len(self.selected_points) == 0 and \
            len(self.selected_lines) == 0 and \
            len(self.selected_polygons) == 0
