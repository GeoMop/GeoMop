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
from LayerEditor.simplification.polysimplify import VWSimplifier
from time import time

class ShpTransferData():

    def __init__(self):
        self.decomposition = PolygonDecomposition()
        self.polygons = []
        self.lines = []
        self.points = []

    def _get_data(self):
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

    def _point_in_diagram(self, searched_point):
        '''basically for item in list overload for location comparison
        :returns list of points already in diagram that collide with searched_point
        '''
        colided_points = []
        for point in cfg.diagram.points:
            if searched_point.x() == point.x and searched_point.y() == point.y:
                colided_points.append(point)
        return colided_points

    def _simplify_polyline(self, points):
        """Simplify a line defined by a list of points
        :arg points list of points defining polyline [QPointF,..]
        :returns simplified list of points [QPointF,..]"""
        simplified = []
        return simplified

    def transfer(self):
        #TODO: use line try
        print("hello")
        self._get_data()
        print(len(self.polygons))
        print(len(self.lines))
        print(len(self.points))

        for point in self.points:
            points_in_diagram = self._point_in_diagram(point)
            if not points_in_diagram:
                cfg.diagram._add_point(None, point)
            else:
                print("Tried to add solitary point to a position of existing point.")

        for line in self.lines:
            #TODO: polyline simplification requires different data hanling, i.e. polyline separation and individual addition
            # pp = np.array([[point.x(), point.y()] for point in polygon.polygon_points])
            # simplifier = VWSimplifier(pp)
            # polygon_points = simplifier.from_number(len(pp) / 2)
            # polygon_points = [QtCore.QPointF(p[0], p[1]) for p in polygon_points]
            # # print("Visvalingam: reduced to %s points from %s in %03f seconds" % (len(polygon_points), len(pp), end - start))
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
            pp = np.array([[point.x(), point.y()] for point in polygon.polygon_points])
            simplifier = VWSimplifier(pp)
            nb_reduced =
            polygon_points = simplifier.from_number()
            polygon_points = [QtCore.QPointF(p[0], p[1]) for p in polygon_points]
            # print("Visvalingam: reduced to %s points from %s in %03f seconds" % (len(polygon_points), len(pp), end - start))
            p_in_diagram = self._point_in_diagram(polygon_points[0])
            # TODO: line intersection
            # If is only for the case the polygon first point is on already existing point
            if not p_in_diagram:
                cfg.main_window.diagramScene._add_line(None, polygon_points[0])
            elif len(p_in_diagram) == 1:
                cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, polygon_points[0])
            else:
                print("TODO: I found more points at point1 location, these points should be merged")

            for point in polygon_points[1:]:
                p_in_diagram = self._point_in_diagram(point)
                if not p_in_diagram:
                    cfg.main_window.diagramScene._add_line(None, point)
                elif len(p_in_diagram) == 1:
                    cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, point, False)
                else:
                    print("TODO: I found more points at point1 location, these points should be merged")



            # first_point = cfg.main_window.diagramScene._last_line.p1
                #     cfg.main_window.diagramScene._add_`line(None, point, False)
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
            # p, _ = cfg.main_window.diagramScene._add_point(None, polygon.polygon_points[0])
            # cfg.main_window.diagramScene._add_line(p, polygon.polygon_points[0])
            # for point in polygon.polygon_points[1:-1]:
            #     cfg.main_window.diagramScene._add_line(None, point)
            # cfg.main_window.diagramScene._add_line(p, polygon.polygon_points[-1], False)
        #TODO: Creating line on another error
        #   - how does it change? Search from mouse release event
            # for polygon in polygons:
            #     spolygon = cfg.diagram.add_polygon(lines, label, not_history, copy)
            #     spolygon.qtpolygon = qtpolygon

            # for point in cfg.diagram.shp.datas.points.highlightened:
            #     print(point.id)
            # cfg.diagram.data.datas[0].av_highlight[j]

class ShpTransferView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ShpTransferView, self).__init__(parent)
        self.shpdata = ShpTransferData()
        grid = QtWidgets.QGridLayout(self)
        self.selection = []
        self.inputSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.inputSlider.setMinimum(0)
        self.inputSlider.setMaximum(100)
        self.inputSlider.setValue(80)
        self.inputSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.inputSlider.setTickInterval(5)
        self.inputSlider.valueChanged.connect(self._update_object_count)
        grid.addWidget(self.inputSlider)
        self.button = QtWidgets.QPushButton()
        self.button.setText("No selected polygons")
        self.button.clicked.connect(self.shpdata.transfer)
        grid.addWidget(self.button)
        self.label = QtWidgets.QLabel("Shapefile help panel: ")
        self.setLayout(grid)

    def _update_object_count(self):
        percentage = self.inputSlider.value()/100
        self.shpdata._get_data()
        if not self.shpdata.polygons:
            self.button.setText("No selected polygons")
        else:
            nb_points = np.floor(len(self.shpdata.polygons[0].polygon_points)*percentage)
            self.button.setText(str(nb_points)+'/'+str(len(self.shpdata.polygons[0].polygon_points)))