from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QBrush, QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsRectItem

from LayerEditor.ui.data.block_layers_model import BlockLayersModel
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.region_item import RegionItem
from LayerEditor.ui.data.shp_structures import ShapeItem
from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.data.tools.selector import Selector
from LayerEditor.ui.diagram_editor.graphics_items.abstract_graphics_item import AbstractGraphicsItem
from LayerEditor.ui.diagram_editor.graphics_items.diagram_item import DiagramItem
from LayerEditor.ui.diagram_editor.graphics_items.grid import Grid
from LayerEditor.ui.tools.cursor import Cursor

from LayerEditor.ui.diagram_editor.graphics_items.gs_point import GsPoint
from LayerEditor.ui.diagram_editor.graphics_items.gs_polygon import GsPolygon
from LayerEditor.ui.diagram_editor.graphics_items.gs_segment import GsSegment
from LayerEditor.ui.view_panel.overlay_tree_item import OverlayTreeItem


class DiagramScene(QtWidgets.QGraphicsScene):
    regionsUpdateRequired = QtCore.pyqtSignal()

    def __init__(self, bounding_rect, parent):
        super().__init__(bounding_rect, parent)
        self.block_model = parent.le_model.blocks_model
        self.selection = None

        self.gs_surf_grid = None
        # holds graphics object for surface grid so it can be deleted when not needed

        self.overlays = []  # do not modify directly! use appropriate methods!!!
        self.active_diagram = Selector(None)
        self.update_scene()
        # self.change_main_diagram()

        self.change_main_diagram(self.block_model.gui_block_selector.value.id)

        self.last_point = None
        self.aux_pt, self.aux_seg = self.create_aux_segment()
        self.hide_aux_line()

        self._press_screen_pos = QtCore.QPoint()

        self.pixmap_item = None

        self.init_area = QGraphicsRectItem(self.sceneRect())
        self.init_area.setBrush(QBrush(Qt.NoBrush))
        pen = self.init_area.pen()
        pen.setCosmetic(True)
        self.init_area.setPen(pen)
        self.addItem(self.init_area)
        self.init_area.setVisible(parent._show_init_area)
        self.init_area.setZValue(-1000)

    def change_opacity(self, data_item, opacity):
        self.find_overlay(data_item).setOpacity(opacity)

    def find_overlay(self, data_object):
        for overlay in self.overlays:
            if overlay.data_item is data_object:
                return overlay

    def create_graphic_object(self, data_object):
        if isinstance(data_object, LayerItem):
            item = DiagramItem(data_object, self.parent().zoom)
            item.disable_editing()

        elif isinstance(data_object, ShapeItem):
            item = data_object.shpdata.object

        elif isinstance(data_object, SurfaceItem):
            item = Grid(*data_object.get_curr_quad())
        else:
            assert "Invalid data_object"
        return item

    def update_depth(self):
        for z, overlay in enumerate(self.overlays):
            overlay.setZValue(-z)

    def insert_overlay(self, data_item, opacity):
        g_item = self.create_graphic_object(data_item)
        g_item.setVisible(True)
        self.overlays.append(g_item)
        self.addItem(g_item)
        g_item.setOpacity(opacity)
        self.update_depth()

    def remove_overlay(self, data_item):
        item = self.find_overlay(data_item)
        self.overlays.remove(item)
        self.removeItem(item)
        self.update_depth()

    @property
    def block(self):
        return self.block_model.gui_block_selector.value

    def get_diagram_index(self, block):
        for index in range(len(self._diagrams)):
            if block is self._diagrams[index].block:
                return index

    def update_visibility(self, block_id, checked):
        self._diagrams[self.get_diagram_index(self.block_model[block_id])].setVisible(checked)

    def change_main_diagram(self, block_id):
        """Sets new main graphics object for editing"""
        if self.active_diagram.value is not None:
            self.active_diagram.value.disable_editing()
            self.removeItem(self.active_diagram.value)
            old_block_id = self.active_diagram.value.layer.block.id
            self.block_model[old_block_id].gui_layer_selector.value_changed.disconnect(self.change_layer_in_diagram)

        self.active_diagram.value = self.create_graphic_object(self.block_model[block_id].gui_layer_selector.value)
        self.addItem(self.active_diagram.value)
        self.active_diagram.value.enable_editing()
        self.block_model[block_id].gui_layer_selector.value_changed.connect(self.change_layer_in_diagram)

        self.selection = self.active_diagram.value.layer.block.selection
        self.selection.set_diagram(self.active_diagram.value)

    def change_layer_in_diagram(self, layer_id):
        self.change_main_diagram(self.active_diagram.value.layer.block.id)

    def get_shape_color(self, shape_key):
        if self.block.gui_layer_selector.value is None:
            return "black"
        dim, shape_id = shape_key
        region = self.block.gui_layer_selector.value.shape_regions[dim][shape_id]

        if region is None:
            region = RegionItem.none
        return region.color

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


    def user_items_rect(self):
        """ Returns bounding rect of all items added by user.
            Those exclude any frames and other possible cosmetic items."""
        rect = QRectF()
        for point in self.points.values():
            rect = rect.united(point.mapToScene(point.boundingRect()).boundingRect())

        if self.parent().root_shp_item.childItems():
            root = self.parent().root_shp_item
            rect = rect.united(root.mapToScene(root.boundingRect()).boundingRect())

        if self.gs_surf_grid is not None:
            rect = rect.united(self.gs_surf_grid.mapToScene(self.gs_surf_grid.boundingRect()).boundingRect())

        return rect

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

    def new_point(self, pos, close=False):
        new_g_point = self.active_diagram.value.add_point(pos, self.last_point)

        if not close:
            self.last_point = new_g_point
            pt = new_g_point.pos()
            self.move_aux_segment(pt, origin=pt)
        else:
            self.last_point = None
            self.hide_aux_line()

        self.update_scene()

    def mouse_create_event(self, event):
        close = event.modifiers() & Qt.ControlModifier
        event.accept()
        self.selection._selected.clear()
        self.new_point(event.scenePos(), close)

    def below_item(self, scene_pos):
        below_item = None
        for item in self.items(scene_pos, deviceTransform=self.parent().transform()):
            if (item is self.aux_pt) or (item is self.aux_seg):
                continue
            below_item = item
            break
        return below_item

    def update_zoom(self, value):
        for overlay in self.overlays:
            if hasattr(overlay, 'update_zoom'):
                overlay.update_zoom(value)

    def mousePressEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        if event.button() == Qt.RightButton and self.last_point is None:
            self.parent().setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            for item in self.items():
                item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            if self.selection is not None:
                self.selection.deselect_all()
        self._press_screen_pos = event.screenPos()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        :param event: QGraphicsSceneMouseEvent
        :return:
        """
        below_item = self.below_item(event.scenePos())
        screen_pos_not_changed = (event.screenPos() - self._press_screen_pos).manhattanLength() < 5

        if event.button() == Qt.LeftButton and screen_pos_not_changed:
            self.mouse_create_event(event)

        if event.button() == Qt.RightButton and screen_pos_not_changed:
                self.selection_start_point = event.pos()
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
                        if self.selection is not None:
                            self.selection.deselect_all()

        super().mouseReleaseEvent(event)
        if event.button() == Qt.RightButton:
            self.parent().setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            for item in self.items():
                item.block_select_change = True
                item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
                item.block_select_change = False

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super(DiagramScene, self).focusOutEvent(event)
        self.parent().setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mouseMoveEvent(self, event):
        # if event.buttons() & Qt.RightButton:
        #     rect_path = QPainterPath()
        #     rect_path.addRect(QRectF(self.selection_start_point, event.pos()))
        #     self.setSelectionArea(rect_path, self.parent().transform())
        #     for item in self.selectedItems():
        #         self.selection.add_selected_item(item)

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
        # Show grid in this scene defined by parent view
        # parent_surf_grid = self.parent().gs_surf_grid
        # if parent_surf_grid is not self.gs_surf_grid:
        #     self.removeItem(self.gs_surf_grid)
        #     if parent_surf_grid is not None:
        #         self.addItem(parent_surf_grid)
        #     self.gs_surf_grid = parent_surf_grid
        #
        # not_updated_indices = list(range(len(self._diagrams)))
        # for block in self.block_model.items():
        #     diagram_exists = False
        #     for index in not_updated_indices:
        #         diagram = self._diagrams[index]
        #         if diagram.block is block:
        #             not_updated_indices.remove(index)
        #             diagram_exists = True
        #             diagram.update_item()
        #             break
        #     if not diagram_exists:
        #         self.add_diagram(DiagramItem(block, self.parent().zoom))
        # for index in not_updated_indices:
        #     self.remove_diagram(self._diagrams[index])

        for overlay in self.overlays:
            overlay.update_item()

        if self.active_diagram.value is not None:
            self.active_diagram.value.update_item()
            self.active_diagram.value.update_zoom(self.parent().zoom)

        self.update()

    def setSceneRect(self, rect: QtCore.QRectF) -> None:
        super(DiagramScene, self).setSceneRect(rect)
        self.init_area.setRect(rect)

    def delete_selected(self):
        self.active_diagram.value.decomposition.delete_items(self.selection.get_selected_shape_dim_id())
        self.update_scene()
        self.selection.deselect_all()
