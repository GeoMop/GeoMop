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
                if not line.p1 in self.selected_points:
                    self.select_point(line.p1)
                if not line.p2 in self.selected_points:
                    self.select_point(line.p2)
        else:
            self.selected_lines.remove(line)
            line.object.deselect_line()
            if with_points:
                if line.p1 in self.selected_points:
                    self.deselect_point(line.p1)
                if not line.p2 in self.selected_points:
                    self.deselect_point(line.p2)

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
