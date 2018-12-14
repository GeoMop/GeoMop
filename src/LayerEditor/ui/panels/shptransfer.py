import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from LayerEditor.leconfig import cfg
import os
import numpy as np
from gm_base.geomop_dialogs import GMErrorDialog
import gm_base.icon as icon
from ..data import SurfacesHistory
from gm_base.polygons.polygons import PolygonDecomposition
from ..gitems import Point
import copy
from LayerEditor.simplification.polysimplify import VWSimplifier
from time import time
import gm_base.polygons.aabb_lookup as aabb_lookup

class ShpTransferData:

    def __init__(self):
        self.decomposition = PolygonDecomposition()
        self._reset_data()

    def _reset_data(self):
        self.polygons = []
        self.lines = []
        self.points = []
        self.precision = 1e-3
        self.todo_steps = [True, True]

    def _reset_buttons(self):
        cfg.main_window.shpTransfer.load_button.setEnabled(True)
        cfg.main_window.shpTransfer.process_button.setEnabled(False)
        cfg.main_window.shpTransfer.transfer_button.setEnabled(False)

    def _is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def set_precision(self):
        precision = cfg.main_window.shpTransfer.precision_edit.text()
        if self._is_number(precision):
            self.precision = float(precision)

    def get_data(self):
        print("Extracting data from the shapefile")
        self._reset_data()
        self._reset_buttons()
        for shp in cfg.diagram.shp.datas:
            self.polygons.extend([polygon for polygon in shp.shpdata.polygons if polygon.highlighted])
            self.lines.extend([line for line in shp.shpdata.lines if line.highlighted])
            self.points.extend([point.p for point in shp.shpdata.points if point.highlighted])
        cfg.main_window.shpTransfer.process_button.setEnabled(True)
        self.todo_steps[0] = False
        return self.todo_steps[0]

### ------------------------------------- PROCESSING --------------------------------------

    def _simplify_polyline(self, points):
        """Simplify a line defined by a list of points
        :arg points list of points defining polyline [QPointF,..]
        :returns simplified list of points [QPointF,..]"""
        simplified = []
        return simplified

    def _extract_points(self):
        points = []
        points.extend(self.points)
        for line in self.lines:
            points.append(line.p1)
            points.append(line.p2)
        for polygon in self.polygons:
            points.extend(polygon.polygon_points)
        return points

    def process_data(self):
        if self.todo_steps[0]:
            print("Get data from shapefile first.")
            return
        print("Processing shapefile data")
        print(len(self.polygons))
        print(len(self.lines))
        print(len(self.points))
        # load all points and try to do weighted merge
        points = self._extract_points()
        for point in points:
            pass
        cfg.main_window.shpTransfer.process_button.setEnabled(False)
        cfg.main_window.shpTransfer.transfer_button.setEnabled(True)
        self.todo_steps[1] = False
        return self.todo_steps[1]

### ------------------------------------- TRANSFER --------------------------------------

    # Transfer function
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
        if any(self.todo_steps):
            print("Load and process the shapefile data before transferring to the diagram.")
            return

        for point in self.points:
            points_in_diagram = self._point_in_diagram(point)
            if not points_in_diagram:
                cfg.diagram._add_point(None, point)
            else:
                print("Tried to add solitary point to a position of existing point.")

        for line in self.lines:
            #TODO: polyline simplification requires different data handling, i.e. polyline separation and individual addition
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
                # TODO: merge the points instead

        for polygon in self.polygons:
            pp = np.array([[point.x(), point.y()] for point in polygon.polygon_points])
            simplifier = VWSimplifier(pp)
            nb_reduced = int(cfg.main_window.shpTransfer.transfer_button.text().split("/", 1)[0])
            if nb_reduced:
                polygon_points = simplifier.from_number(nb_reduced)
            else:
                print("Set desired reduction!")
                return
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

        cfg.main_window.shpTransfer.transfer_button.setEnabled(False)

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
        self.load_button = QtWidgets.QPushButton()
        self.load_button.setText("Load data")
        self.load_button.clicked.connect(self.shpdata.get_data)
        self.load_button.setEnabled(True)
        grid.addWidget(self.load_button, 0, 0, 1, 3)
        precision_label = QtWidgets.QLabel("Precision:", self)
        self.precision_edit = QtWidgets.QLineEdit()
        self.precision_edit.setText(str(self.shpdata.precision))
        self.precision_edit.editingFinished.connect(self.shpdata.set_precision)
        grid.addWidget(precision_label, 1, 0)
        grid.addWidget(self.precision_edit, 1, 1)
        self.process_button = QtWidgets.QPushButton()
        self.process_button.setText("Process data")
        self.process_button.clicked.connect(self.shpdata.process_data)
        self.process_button.setEnabled(False)
        grid.addWidget(self.process_button, 1, 2)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(sep, 2, 0, 1, 3)

        slider_label = QtWidgets.QLabel("Simplify to nb.points:", self)
        self.inputSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.inputSlider.setMinimum(0)
        self.inputSlider.setMaximum(100)
        self.inputSlider.setValue(80)
        self.inputSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.inputSlider.setTickInterval(5)
        self.inputSlider.valueChanged.connect(self._update_object_count)
        grid.addWidget(slider_label, 3, 0, 1, 1)
        grid.addWidget(self.inputSlider, 3, 1,  1, 2)
        self.transfer_button = QtWidgets.QPushButton()
        self.transfer_button.setText("No selected polygons")
        self.transfer_button.clicked.connect(self.shpdata.transfer)
        self.transfer_button.setEnabled(False)
        grid.addWidget(self.transfer_button, 4, 0,  1, 3)
        self.label = QtWidgets.QLabel("Shapefile help panel: ")
        self.setLayout(grid)

    def _update_object_count(self):
        if any(self.shpdata.todo_steps):
            self.transfer_button.setText("Finish data processing to continue..")
            return
        percentage = self.inputSlider.value()/100
        if not self.shpdata.polygons:
            self.transfer_button.setText("No selected polygons")
        else:
            nb_points = int(np.floor(len(self.shpdata.polygons[0].polygon_points)*percentage))
            self.transfer_button.setText(str(nb_points)+'/'+str(len(self.shpdata.polygons[0].polygon_points)))