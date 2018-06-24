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
import copy

class ShpTransferData():

    def __init__(self):
        self.decomposition = PolygonDecomposition()
        self.polygons = []
        self.lines = []
        self.points = []

    def transfer(self):
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
            cfg.main_window.diagramScene._add_line(None, line.p1)
            cfg.main_window.diagramScene._add_line(None, line.p2)
        for polygon in self.polygons:
            last_point = None
            for point in polygon.polygon_points[0:-1]:
                if not last_point:
                    p = cfg.diagram.add_point(point.x(), point.y())
                    added_points.append(p)
                    last_point = point
                    continue
                p1 = added_points[-1]
                p2 = cfg.diagram.add_point(point.x(), point.y())
                _, l = cfg.diagram.add_line(p1, p2.x, p2.y)
                added_points.append(p2)
                added_lines.append(l)
                last_point = point
            l = cfg.diagram.join_line(added_points[-1], added_points[0])
            added_lines.append(l)
        cfg.main_window.diagramScene.update_changes(added_points, [], [], added_lines, [])

        #TODO: Diagram structures 972 adds line to polygon operation which asks for the last polygon decomposition change
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