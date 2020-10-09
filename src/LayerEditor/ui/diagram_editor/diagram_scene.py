from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QGraphicsRectItem

from LayerEditor.ui.data.region import Region
from LayerEditor.ui.data.regions_model import RegionsModel
from LayerEditor.ui.tools import better_undo
from LayerEditor.ui.tools.cursor import Cursor

from bgem.polygons import polygons
from bgem.external import undo


from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment


class DiagramScene(QtWidgets.QGraphicsScene):
    regionsUpdateRequired = QtCore.pyqtSignal()
    TOLERANCE = 5

    def __init__(self, block, bounding_rect, parent):
        super().__init__(bounding_rect, parent)
        self.selection = block.selection
        self.block = block
        self.points = {}
        self.segments = {}
        self.polygons = {}
        """Maps to all graphical objects grouped by type {id:QGraphicsItem}"""

        self.regions_model = block.regions_model

        self.last_point = None
        self.aux_pt, self.aux_seg = self.create_aux_segment()
        self.hide_aux_line()

        self._press_screen_pos = QtCore.QPoint()

        # polygons
        self.decomposition = block.decomposition
        res = self.decomposition.get_last_polygon_changes()
        self.decomposition.set_tolerance(self.TOLERANCE)
        #assert res[0] == PolygonChange.add
        self.outer_id = res[1]
        """Decomposition of the a plane into polygons."""
        self.update_scene()
        self.pixmap_item = None
        temp = QGraphicsRectItem(self.sceneRect())
        temp.setBrush(QBrush(Qt.NoBrush))
        pen = temp.pen()
        pen.setCosmetic(True)
        temp.setPen(pen)
        self.addItem(temp)

    def get_shape(self, dim, shape_id) -> [GsPoint, GsSegment, GsPolygon]:
        """Get g_item defined by dimension and id"""
        if dim == 0:
            return self.points[shape_id]
        if dim == 1:
            return self.segments[shape_id]
        if dim == 2:
            return self.polygons[shape_id]


    def get_shape_color(self, shape_key):
        if self.block.gui_selected_layer is None:
            return "black"
        dim, shape_id = shape_key
        region = self.block.gui_selected_layer.shape_regions[dim][shape_id]

        if region is None:
            region = Region.none
        return region.color

    # def get_shape_region(self, shape_key):
    #     dim, shape_id = shape_key
    #     region_id = self.decomposition.decomp.shapes[dim][shape_id].attr
    #
    #     if region_id is None:
    #         region_id = Region.none.id
    #
    #     return region_id

    def create_aux_segment(self):
        pt_size = GsPoint.SIZE
        no_pen = QtGui.QPen(QtCore.Qt.NoPen)
        add_brush = QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.SolidPattern)
        pt = self.addEllipse(-pt_size, -pt_size, 2*pt_size, 2*pt_size, no_pen, add_brush)
        pt.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        pt.setCursor(Cursor.draw)
        pt.setZValue(100)
        add_pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.darkGreen), GsSegment.WIDTH)
        add_pen.setCosmetic(True)
        line = self.addLine(0,0,0,0, add_pen)
        line.setZValue(100)
        return pt, line

    def move_aux_segment(self, tip, origin=None):
        """
        Update tip point and show aux segment and point.
        :param tip: Tip point (QPointF)
        :param origin: Origin point (QPointF)
        """
        self.aux_pt.show()
        self.aux_seg.show()
        self.aux_pt.setPos(tip)
        if origin is None:
            origin = self.aux_seg.line().p1()
        self.aux_seg.setLine(QtCore.QLineF(origin, tip))
        if origin.x() == tip.x() and origin.y() == tip.y():
            self.aux_seg.hide()

    def hide_aux_line(self):
        self.aux_pt.hide()
        self.aux_seg.hide()

    def add_point(self, pos, gitem):
        if type(gitem) == GsPoint:
            return gitem
        else:
            #if type(gitem) == GsSegment:
            #pt = Point(pos.x(), pos.y(), Region.none)
            #pt = self.decomposition.add_free_point(None, (pos.x(), -pos.y()), self.outer_id)
            pt = self.decomposition.add_point((pos.x(), -pos.y()))
            if pt.id in self.points:
                gpt = self.points[pt.id]
            else:
                gpt = GsPoint(pt, self.block)
                #self.points.append(pt)
                self.points[pt.id] = gpt
                self.addItem(gpt)
            return gpt

    def add_segment(self, gpt1, gpt2):
        #seg = Segment(gpt1.pt, gpt2.pt, Region.none)
        #seg = self.decomposition.new_segment(gpt1.pt, gpt2.pt)
        seg_list = self.decomposition.add_line_for_points(gpt1.pt, gpt2.pt)
        # for seg in seg_list:
        #     gseg = GsSegment(seg)
        #     gseg.update_zoom(self._zoom_value)
        #     self.segments.append(seg)
        #     self.addItem(gseg)
        self.update_scene()

    def new_point(self, pos, gitem, close = False):
        #print("below: ", gitem)
        new_g_point = self.add_point(pos, gitem)
        if self.last_point is not None:
            self.add_segment(self.last_point, new_g_point)

        if not close:
            self.last_point = new_g_point
            pt = new_g_point.pos()
            self.move_aux_segment(pt, origin=pt)
        else:
            self.last_point = None
            self.hide_aux_line()
        return self.decomposition.last_split_shapes

    def mouse_create_event(self, event):
        #transform = self.parent().transform()
        #below_item = self.itemAt(event.scenePos(), transform)
        below_item = self.below_item(event.scenePos())
        close = event.modifiers() & Qt.ControlModifier
        with better_undo.group("New point"):
            split_items = self.new_point(event.scenePos(), below_item, close)
            event.accept()

            self.selection._selected.clear()
            self.update_scene()
            # update scene so new shapes would habe g_item for next step
            for item in split_items:
                # if some shape was splited then copy region to the new shape
                if item[0] == 2 and item[1] == 0:
                    continue
                g_old_item = self.get_shape(item[0], item[1])
                g_new_item = self.get_shape(item[0], item[2])
                for layer in self.block.layers:
                    region1 = layer.get_shape_region(g_new_item)
                    region = layer.get_shape_region(g_old_item)
                    layer.set_region_to_shape(g_new_item, region)
            self.update_scene()
            # update again because colors may have changed

    def below_item(self, scene_pos):
        below_item = None
        for item in self.items(scene_pos, deviceTransform=self.parent().transform()):
            if (item is self.aux_pt) or (item is self.aux_seg):
                continue
            below_item = item
            break
        return below_item

    def update_zoom(self, value):
        self.decomposition.set_tolerance(self.TOLERANCE/value)
        for g_seg in self.segments.values():
            g_seg.update_zoom(value)

    def update_all_points(self):
        for g_point in self.points.values():
            g_point.update()

    def update_all_segments(self):
        for g_seg in self.segments.values():
            g_seg.update()

    def update_all_polygons(self):
        for g_pol in self.polygons.values():
            g_pol.update()

    def mousePressEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        #print("P last: ", event.lastScenePos())
        #if event.button() == Qt.RightButton and self.last_point is None:
        #    self.mouse_create_event(event)

        self._press_screen_pos = event.screenPos()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        #print("R last: ", event.lastScenePos())
        below_item = self.below_item(event.scenePos())
        screen_pos_not_changed = event.screenPos() == self._press_screen_pos

        if event.button() == Qt.LeftButton and screen_pos_not_changed:
            self.mouse_create_event(event)

        if event.button() == Qt.RightButton and screen_pos_not_changed:
            item = None
            if below_item is not None:
                if type(below_item) is GsPoint:
                    item = below_item
                elif type(below_item) is GsSegment:
                    item = below_item
                elif type(below_item) is GsPolygon:
                    item = below_item

            if event.modifiers() & Qt.ShiftModifier:
                if item is not None:
                    self.selection.select_toggle_item(item)
            else:
                if item is not None:
                    self.selection.select_item(item)
                else:
                    self.selection.deselect_all()

        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        if self.last_point is not None:
            self.move_aux_segment(event.scenePos())
        super().mouseMoveEvent(event)

    def hide_aux_point_and_seg(self):
        self.last_point = None
        self.hide_aux_line()

    def keyPressEvent(self, event):
        """Standart key press event"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide_aux_point_and_seg()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.delete_selected()
        elif event.key() == QtCore.Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            self.selection.select_all()
        else:
            super(DiagramScene, self).keyPressEvent(event)

    def update_scene(self):
        # points
        to_remove = []
        de_points = self.decomposition.points
        for point_id in self.points:
            if point_id not in de_points:
                to_remove.append(point_id)
        for point_id in to_remove:
            self.removeItem(self.points[point_id])
            del self.points[point_id]
        for point_id, point in de_points.items():
            if point_id in self.points:
                self.points[point_id].update()
            else:
                gpt = GsPoint(point, self.block)
                self.points[point_id] = gpt
                self.addItem(gpt)

        # segments
        to_remove = []
        de_segments = self.decomposition.segments
        for segment_id in self.segments:
            if segment_id not in de_segments:
                to_remove.append(segment_id)
        for segment_id in to_remove:
            self.removeItem(self.segments[segment_id])
            del self.segments[segment_id]
        for segment_id, segment in de_segments.items():
            if segment_id in self.segments:
                self.segments[segment_id].update()
            else:
                gseg = GsSegment(segment, self.block)
                parent = self.parent()
                gseg.update_zoom(self.parent().zoom)
                self.segments[segment_id] = gseg
                self.addItem(gseg)

        # polygons
        to_remove = []
        de_polygons = self.decomposition.polygons
        for polygon_id in self.polygons:
            if polygon_id not in de_polygons:
                to_remove.append(polygon_id)
        for polygon_id in to_remove:
            self.removeItem(self.polygons[polygon_id])
            del self.polygons[polygon_id]
        for polygon_id, polygon in de_polygons.items():
            if polygon_id == self.outer_id:
                continue
            if polygon_id in self.polygons:
                self.polygons[polygon_id].update()
            else:
                gpol = GsPolygon(polygon, self.block)
                self.polygons[polygon_id] = gpol
                self.addItem(gpol)

        self.update()

    def delete_selected(self):
        with better_undo.group("Delete selected"):
            # segments
            for item in self.selection._selected:
                if type(item) is GsSegment:
                    self.decomposition.delete_segment(item.segment)

            # points
            for item in self.selection._selected:
                if type(item) is GsPoint:
                    self.decomposition.delete_point(item.pt)

            self.selection._selected.clear()

            self.update_scene()

    @staticmethod
    def get_shape_key(shape):
        if type(shape) is GsPoint:
            return 1, shape.pt.id

        elif type(shape) is GsSegment:
            return 2, shape.segment.id

        elif type(shape) is GsPolygon:
            return 3, shape.polygon_data.id

    # Modified from previous diagram
    #
    # def set_data(self):
    #     """set new shapes data"""
    #     for line in cfg.diagram.lines:
    #         l = GsSegment(line, self.block)
    #         self.add_graphical_object(l)
    #     for point in cfg.diagram.points:
    #         p = GsPoint(point, self.block)
    #         self.add_graphical_object(p)
    #     for polygon in cfg.diagram.polygons:
    #         if polygon.object is None:
    #             p = GsPolygon(polygon, self.block)
    #             self.add_graphical_object(p)
    #     #self._add_polygons()
    #
    # def add_graphical_object(self, obj):
    #     self.addItem(obj)
    #     # update the regions panel in case some region gets in use and therefore cannot be deleted.
    #     self.regionsUpdateRequired.emit()
    #
    # # Copied from previous diagram
    # def release_data(self, old_diagram):
    #     """release all shapes data"""
    #     for line in cfg.diagrams[old_diagram].lines:
    #         obj = line.object
    #         obj.release_line()
    #         self.remove_graphical_object(obj)
    #     for point in cfg.diagrams[old_diagram].points:
    #         obj = point.object
    #         obj.release_point()
    #         self.remove_graphical_object(obj)
    #     for polygon in cfg.diagrams[old_diagram].polygons:
    #         obj = polygon.object
    #         obj.release_polygon()
    #         self.remove_graphical_object(obj)
    #
    #
