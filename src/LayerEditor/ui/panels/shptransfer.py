import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from LayerEditor.leconfig import cfg
import os
import numpy as np
import numpy.linalg as la
from gm_base.geomop_dialogs import GMErrorDialog
import gm_base.icon as icon
from ..data import SurfacesHistory
from gm_base.polygons.polygons import PolygonDecomposition
from ..gitems import Point
import copy
from LayerEditor.simplification.polysimplify import VWSimplifier
from time import time
import gm_base.polygons.aabb_lookup as aabb_lookup


class Metapoint:

    def __init__(self, xy, weight=1, id=None):
        self.xy = np.array(xy)
        self.weight = weight
        self.id = id
        self.metalines = []


class Metaline:

    def __init__(self, mp1, mp2, id=None):
        # mp1, mp2 are Metapoints
        self.mp1 = mp1
        mp1.metalines.append(self)
        self.mp2 = mp2
        mp2.metalines.append(self)
        self.id = id
        self.metapolygons = []

    def replace_point(self, p_old, p_new):
        # Return error statement - False is unique, thus returned on success, True is obtained e.g. by any int cast
        if self.mp1 == p_old:
            self.mp1 = p_new
        elif self.mp2 == p_old:
            self.mp2 = p_new
        else:
            return True
        return False

class Polyline:

    def __init__(self, endpoints, lines):
        self.end1 = endpoints[0]
        self.end2 = endpoints[1]
        self.lines = lines

class Metapolygon:

    def __init__(self, id=None):
        self.id = id
        self.polylines = []
        self.metalines = []
        self.points_lookup = aabb_lookup.AABB_Lookup()
        self.segments_lookup = aabb_lookup.AABB_Lookup()

    def _get_line_end(self, p, polygon_lines):
        lines = []
        while not(len(p.metalines) <= 1 or len(p.metalines) > 2):
            for l in p.metalines:
                if l not in polygon_lines:
                    continue
                else:
                    polygon_lines.remove(l)
                    lines.append(l)
                    if l.mp1 == p:
                        p = l.mp2
                        break
                    elif l.mp2 == p:
                        p = l.mp1
                        break
                    else:
                        print("This is impossible!")
                        break
        return p, lines, polygon_lines

    def group_metalines(self):
        polygon_lines = self.metalines
        for line in polygon_lines:
            polygon_lines.remove(line)
            polyline = []
            endpoints = []
            for p in [line.mp1, line.mp2]:
                endpoint, temp_lines, polygon_lines = self._get_line_end(p, polygon_lines)
                endpoints.append(endpoint)
                polyline.extend(temp_lines)
            polyline = Polyline(endpoints, polyline)
            self.polylines.append(polyline)

    def verify_simple_loop(self):
        closed = 1
        lastline = self.metalines[0]
        startp = lastline.mp1
        point = lastline.mp2
        while not closed == 1:
            if len(point.metalines) == 1:
                closed = 2
            for l in point.metalines:
                if l not in self.metalines:
                    continue
                elif l == lastline:
                    continue
                else:
                    lastline = l
                    if l.mp1 == point:
                        point = l.mp2
                        break
                    elif l.mp2 == point:
                        point = l.mp1
                        break
                    else:
                        closed = 2
                        break
            if startp == point:
                closed = 0
        return closed


class ShpTransferData:

    def __init__(self):
        # self.poly_decomposition = PolygonDecomposition()
        self.points_lookup = aabb_lookup.AABB_Lookup()
        self.segments_lookup = aabb_lookup.AABB_Lookup()
        self._reset_data()

    def _reset_data(self):
        # raw elements from shapefiles
        self.shp_polygons = []
        self.shp_lines = []
        self.shp_points= []
        # elements processed in temporary metaobjects
        self.processed_points = []
        self.processed_segments = []
        self.processed_polygons = []
        # snap precission
        self.precision = 1e-2
        # counter at which step the data transfer is. Cannot transfer unprocessed data
        self.todo_steps = [True, True]

    @staticmethod
    def _reset_buttons():
        cfg.main_window.shpTransfer.load_button.setEnabled(True)
        cfg.main_window.shpTransfer.process_button.setEnabled(False)
        cfg.main_window.shpTransfer.transfer_button.setEnabled(False)

    @staticmethod
    def _is_number(s):
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
            self.shp_polygons.extend([polygon for polygon in shp.shpdata.polygons if polygon.highlighted])
            self.shp_lines.extend([line for line in shp.shpdata.lines if line.highlighted])
            self.shp_points.extend([point.p for point in shp.shpdata.points if point.highlighted])
        cfg.main_window.shpTransfer.process_button.setEnabled(True)
        self.todo_steps[0] = False
        return self.todo_steps[0]

# ------------------------------------- PROCESSING --------------------------------------

    def _get_new_point_id(self):
        i = None
        for i in range(len(self.processed_points)+1):
            if [p.id for p in self.processed_points if p.id == i]:
                continue
            else:
                break
        return i

    def _get_new_line_id(self):
        i = None
        for i in range(len(self.processed_segments)+1):
            # pass if list is not empty, i.e. element with this id exists
            if [l.id for l in self.processed_segments if l.id == i]:
                continue
            else:
                break
        return i

    def _get_new_poly_id(self):
        i = None
        for i in range(len(self.processed_polygons)+1):
            # pass if list is not empty, i.e. element with this id exists
            if [poly.id for poly in self.processed_polygons if poly.id == i]:
                continue
            else:
                break
        return i

    # def _extract_points(self):
    #     points = []
    #     points.extend(self.shp_points)
    #     for line in self.shp_lines:
    #         points.append(line.p1)
    #         points.append(line.p2)
    #     for polygon in self.shp_polygons:
    #         points.extend(polygon.polygon_points)
    #     return points
    #
    # def _extract_lines(self):
    #     lines = []
    #     lines.extend(self.shp_lines)
    #     for polygon in self.shp_polygons:
    #         for i in range(len(polygon.polygon_points)):
    #             lines.append([polygon.polygon_points[i-1],polygon.polygon_points[i]])
    #     return lines
    #
    # def _extract_data(self):
    #
    #     points = self._extract_points()
    #     lines = self._extract_lines()
    #     polygons = self._extract_polygons()
    #     return points, lines, polygons

    def _add_point_processed(self, pt, lookup = None):
        if lookup:
            lookup.add_object(pt.id, aabb_lookup.make_aabb([pt.xy], margin=self.precision))
        else:
            self.points_lookup.add_object(pt.id, aabb_lookup.make_aabb([pt.xy], margin=self.precision))
        # id list is common for all point lookups
        self.processed_points.append(pt)

    def _add_segment_processed(self, seg, lookup = None):
        if lookup:
            lookup.add_object(seg.id, aabb_lookup.make_aabb([seg.mp1.xy, seg.mp2.xy], margin=self.precision))
        else:
            self.segments_lookup.add_object(seg.id, aabb_lookup.make_aabb([seg.mp1.xy, seg.mp2.xy], margin=self.precision))
        # id list is common for all segment lookups
        self.processed_segments.append(seg)

    def _add_polygon_processed(self, poly):
        self.processed_polygons.append(poly)

    def _rm_point(self, pt, lookup = None):
        if lookup:
            lookup.rm_object(pt.id)
        else:
            self.points_lookup.rm_object(pt.id)
        self.processed_points.remove(pt)

    def _rm_segment(self, seg, lookup = None):
        if lookup:
            lookup.rm_object(seg.id)
        else:
            self.segments_lookup.rm_object(seg.id)
        self.processed_segments.remove(seg)

    def _rm_polygon_processed(self, poly):
        self.processed_polygons.remove(poly)

    @staticmethod
    def pt_dist(pt, point):
        return la.norm(pt.xy - point)

    def _merge_points_weighted(self, p1, p2, p_lookup):
        p1.xy = (p1.xy * p1.weight + p2.xy * p2.weight)/(p1.weight + p2.weight)
        p1.weight += p2.weight
        # TODO: Fork merging - one point -> two lines -> two end points are merged. Now both lines are kept..
        # candidates = self.segments_lookup.closest_candidates(point)
        if p1.id < p2.id:
            p1.id = p2.id
        for line in p2.metalines:
            p1.metalines.append(line)
            line.replace_point(p2, p1)
        self._rm_point(p2, p_lookup)
        return p1

    def snapadd_metapoints(self, points, p_lookup=None):
        # p_lookup allows to create objects with snapping in target group
        added_metapoints = []
        for pt in points:
            point = Metapoint([pt.x(), pt.y()], id = self._get_new_point_id())
            if p_lookup:
                candidates = p_lookup.closest_candidates(point.xy)
            else:
                candidates = self.points_lookup.closest_candidates(point.xy)
            # look which points should be merged
            to_merge = []
            for pt_id in candidates:
                pt = [p for p in self.processed_points if p.id == pt_id][0]
                if self.pt_dist(pt, point.xy) < self.precision:
                    to_merge.append(pt)
            # do weighted merge
            for p in to_merge:
                point = self._merge_points_weighted(point, p, p_lookup)
            # add the weighted point or just the point if there was nothing to merge
            self._add_point_processed(point, p_lookup)
            added_metapoints.append(point)
        return added_metapoints

    def snapadd_metalines(self, lines, p_lookup=None, s_lookup=None):
        added_metalines = []
        for l in lines:
            mp1 = self.snapadd_metapoints([l[0]], p_lookup)[0]
            mp2 = self.snapadd_metapoints([l[1]], p_lookup)[0]
            # case mp1 a mp2 are merged, i.e. 0 length line, dont create line - DUH!
            if not (mp1 in self.processed_points and mp2 in self.processed_points):
                continue
            line = Metaline(mp1, mp2, id=self._get_new_line_id())
            # TODO: line overlaps - see TODO in points merging method
            self._add_segment_processed(line, s_lookup)
            added_metalines.append(line)
        return added_metalines

    def process_polygons(self, polygons):
        # polygon.polygon_points are passed in ordered manner - create metalines from the raw data
        processed_polygons = []
        for poly in polygons:
            lines = []
            for i in range(len(poly.polygon_points)-1):
                lines.append([poly.polygon_points[i-1], poly.polygon_points[i]])
            polygon = Metapolygon(id=self._get_new_poly_id())
            metalines = self.snapadd_metalines(lines, polygon.points_lookup, polygon.segments_lookup)
            polygon.metalines.extend(metalines)
            if polygon.verify_simple_loop():
                self._add_polygon_processed(polygon)
                processed_polygons.append(polygon)
        return processed_polygons

    # def _simplify_polyline(self, points):
    #     """Simplify a line defined by a list of points
    #     :arg points list of points defining polyline [QPointF,..]
    #     :returns simplified list of points [QPointF,..]"""
    #     simplified = []
    #     return simplified

    def process_data(self):
        if self.todo_steps[0]:
            print("Get data from shapefile first.")
            return
        print("Processing shapefile data")
        print(len(self.shp_polygons))
        print(len(self.shp_lines))
        print(len(self.shp_points))

        # extract all data from polygons and create appropriate lines (and verify loop)
        self.process_polygons(self.shp_polygons)

        # load all lines and create its points
        lines = []
        for l in self.shp_lines:
            lines.append([l.p1, l.p2])
        self.snapadd_metalines(lines)

        # load all standalone points and try to do weighted merge
        self.snapadd_metapoints(self.shp_points)

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

        for polygon in self.processed_polygons:
            polygon_points = []
            for metaline in polygon.metalines:
                polygon_points.append(metaline.mp1)
            pp = np.array([p.xy for p in polygon_points])
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
                cfg.main_window.diagramScene._add_line(None, point)
            p_in_diagram = self._point_in_diagram(polygon_points[0])
            cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, point, False)

        cfg.main_window.shpTransfer.transfer_button.setEnabled(False)

        # TODO: major overhaul
        # for point in self.processed_points:
        #     points_in_diagram = self._point_in_diagram(point)
        #     if not points_in_diagram:
        #         cfg.diagram._add_point(None, point)
        #     else:
        #         print("Tried to add solitary point to a position of existing point.")
        #
        # for line in self.lines:
        #     #TODO: polyline simplification requires different data handling, i.e. polyline separation and individual addition
        #     # pp = np.array([[point.x(), point.y()] for point in polygon.polygon_points])
        #     # simplifier = VWSimplifier(pp)
        #     # polygon_points = simplifier.from_number(len(pp) / 2)
        #     # polygon_points = [QtCore.QPointF(p[0], p[1]) for p in polygon_points]
        #     # # print("Visvalingam: reduced to %s points from %s in %03f seconds" % (len(polygon_points), len(pp), end - start))
        #     start_points = self._point_in_diagram(line.p1)
        #     if not start_points:
        #         cfg.main_window.diagramScene._add_line(None, line.p1)
        #         cfg.main_window.diagramScene._add_line(None, line.p2, False)
        #     elif len(start_points) == 1:
        #         cfg.main_window.diagramScene._add_line(start_points[0].object, line.p1)
        #         cfg.main_window.diagramScene._add_line(None, line.p2, False)
        #     else:
        #         print("TODO: I found more points at point1 location, these should be merged")
        #         # TODO: merge the points instead
        #
        # for polygon in self.shp_polygons:
        #     pp = np.array([[point.x(), point.y()] for point in polygon.polygon_points])
        #     simplifier = VWSimplifier(pp)
        #     nb_reduced = int(cfg.main_window.shpTransfer.transfer_button.text().split("/", 1)[0])
        #     if nb_reduced:
        #         polygon_points = simplifier.from_number(nb_reduced)
        #     else:
        #         print("Set desired reduction!")
        #         return
        #     polygon_points = [QtCore.QPointF(p[0], p[1]) for p in polygon_points]
        #     # print("Visvalingam: reduced to %s points from %s in %03f seconds" % (len(polygon_points), len(pp), end - start))
        #     p_in_diagram = self._point_in_diagram(polygon_points[0])
        #     # TODO: line intersection
        #     # If is only for the case the polygon first point is on already existing point
        #     if not p_in_diagram:
        #         cfg.main_window.diagramScene._add_line(None, polygon_points[0])
        #     elif len(p_in_diagram) == 1:
        #         cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, polygon_points[0])
        #     else:
        #         print("TODO: I found more points at point1 location, these points should be merged")
        #
        #     for point in polygon_points[1:]:
        #         p_in_diagram = self._point_in_diagram(point)
        #         if not p_in_diagram:
        #             cfg.main_window.diagramScene._add_line(None, point)
        #         elif len(p_in_diagram) == 1:
        #             cfg.main_window.diagramScene._add_line(p_in_diagram[0].object, point, False)
        #         else:
        #             print("TODO: I found more points at point1 location, these points should be merged")
        #
        # cfg.main_window.shpTransfer.transfer_button.setEnabled(False)


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
        if not self.shpdata.shp_polygons:
            self.transfer_button.setText("No selected polygons")
        else:
            nb_points = int(np.floor(len(self.shpdata.processed_points)*percentage))
            self.transfer_button.setText(str(nb_points)+'/'+str(len(self.shpdata.processed_points)))