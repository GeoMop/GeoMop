import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from LayerEditor.leconfig import cfg
import os
import numpy as np
from gm_base.geomop_dialogs import GMErrorDialog
import gm_base.icon as icon
from ..data import SurfacesHistory
from gm_base.geometry_files.polygons import PolygonDecomposition, PolygonChange
from ..gitems import Point
import copy

class ShpTransferData():

    def __init__(self):
        self.decomposition = PolygonDecomposition()
        self.polygons = []
        self.lines = []
        self.points = []

    def _point_in_diagram(self, searched_point):
        '''basically for item in list overload for location comparison
        :returns list of points already in diagram that collide with searched_point
        '''
        colided_points = []
        for point in cfg.diagram.points:
            if searched_point.x() == point.x and searched_point.y() == point.y:
                colided_points.append(point)
        return colided_points

    def transfer(self):
        #TODO: use line try
        added_points = []
        added_lines = []
        added_polygons = []
        print("hello")
        self.get_data()
        print(len(self.polygons))
        print(len(self.lines))
        print(len(self.points))
        for point in self.points:
            cfg.diagram._add_point(None, point)
        for line in self.lines:
            start_points = self._point_in_diagram(line.p1)
            if not start_points:
                cfg.main_window.diagramScene._add_line(None, line.p1)
                cfg.main_window.diagramScene._add_line(None, line.p2, False)
            elif len(start_points) == 1:
                cfg.main_window.diagramScene._add_line(start_points[0].object, line.p1)
                cfg.main_window.diagramScene._add_line(None, line.p2, False)
            else:
                print("TODO: I found more points at point1 location, these should be merged")

        for polygon in self.polygons:
            # first_point = cfg.diagram.
            # cfg.main_window.diagramScene._add_line(None, point)
            p_in_diagram = self._point_in_diagram(polygon.polygon_points[0])
            # If is only for the case the polygon first point is on already existing point
            # TODO: line intersection
            if not p_in_diagram:
                cfg.main_window.diagramScene._add_line(None, polygon.polygon_points[0])
            elif len(p_in_diagram) == 1:
                cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, polygon.polygon_points[0])
            else:
                print("TODO: I found more points at point1 location, these should be merged")

            for point in polygon.polygon_points[1:]:
                p_in_diagram = self._point_in_diagram(point)
                if not p_in_diagram:
                    cfg.main_window.diagramScene._add_line(None, point)
                elif len(p_in_diagram) == 1:
                    cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, point, False)
                else:
                    print("TODO: I found more points at point1 location, these should be merged")

            # first_point = cfg.main_window.diagramScene._last_line.p1
                #     cfg.main_window.diagramScene._add_line(None, point, False)
                    # added_points.append(p)
                    # last_point = points
                    # continue
                # p1 = added_points[-1]
                # p2 = cfg.diagram.add_point(point.x(), point.y())
                # cfg.main_window.diagramScene._add_line(None, point)
                # _, l = cfg.diagram.add_line(p1, p2.x, p2.y)
                # added_points.append(p2)
                # if not last_point:
                # added_lines.append(l)
                # last_point = point
            # cfg.main_window.diagramScene._add_line(p, polygon.polygon_points[-1],False)
            # cfg.diagram.merge_point(first_point, cfg.main_window.diagramScene._last_line.p1, None)
            # l = cfg.diagram.join_line(added_points[-1], added_points[0])
            # added_lines.append(l)
        # cfg.main_window.diagramScene.update_changes(added_points, [], [], added_lines, [])

            # single polygon without checking
            p, _ = cfg.main_window.diagramScene._add_point(None, polygon.polygon_points[0])
            cfg.main_window.diagramScene._add_line(p, polygon.polygon_points[0])
            for point in polygon.polygon_points[1:-1]:
                cfg.main_window.diagramScene._add_line(None, point)
            cfg.main_window.diagramScene._add_line(p, polygon.polygon_points[-1], False)
        #TODO: Creating line on another error
        #   - how does it change? Search from mouse release event
            # for polygon in polygons:
            #     spolygon = cfg.diagram.add_polygon(lines, label, not_history, copy)
            #     spolygon.qtpolygon = qtpolygon

            # for point in cfg.diagram.shp.datas.points.highlightened:
            #     print(point.id)
            # cfg.diagram.data.datas[0].av_highlight[j]
    def get_data(self):
        polygons = []
        lines = []
        points = []
        for shp in cfg.diagram.shp.datas:
            polygons = [polygon for polygon in shp.shpdata.polygons if polygon.highlighted]
            lines = [line for line in shp.shpdata.lines if line.highlighted]
            points = [point.p for point in shp.shpdata.points if point.highlighted]
        for polygon in polygons:
            self.polygons.append(polygon)
        for line in lines:
            self.lines.append(line)
        for point in points:
            self.points.append(point)



class ShpTransferView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ShpTransferView, self).__init__(parent)
        self.shpdata = ShpTransferData()
        grid = QtWidgets.QGridLayout(self)
        self.selection = []
        self.button = QtWidgets.QPushButton()
        self.button.clicked.connect(self.shpdata.transfer)
        grid.addWidget(self.button)
        self.label = QtWidgets.QLabel("Shapefile help panel: ")
        grid.addWidget(self.label)
        self.setLayout(grid)