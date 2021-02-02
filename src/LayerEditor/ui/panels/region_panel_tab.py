from contextlib import contextmanager

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import QObject

from LayerEditor.ui.tools import undo

import gm_base.icon as icon
from gm_base.geomop_dialogs import GMErrorDialog
from ..data.region_item import RegionItem
from ..dialogs.regions import AddRegionDlg
from ..helpers.combo_box import ComboBox
from ...widgets.line_edit import LineEdit


@contextmanager
def nosignal(qt_obj: QObject):
    """
    Context manager for blocking signals inside some signal handlers.
    TODO: move to some common module
    """
    old_state = qt_obj.blockSignals(True)
    yield qt_obj
    qt_obj.blockSignals(old_state)


class RegionLayerTab(QtWidgets.QWidget):
    """
    Single Tab of the Region panel. One tab for every layer in the current topology block.
    """

    def __init__(self, le_model, layer, parent):
        """
        Constructor, just make widgets and set reference to parent and layer_heads.
        Reinit must be called explicitly to fill the widget content.
        """
        super().__init__(parent)
        self._parent = parent

        self.le_model = le_model
        # Reference model for region panel
        self.layer = layer
        # Layer to which this Tab is related.
        self._layer_name = layer.name
        # Name of the layer.
        # auxiliary map from region ID to index in the combo box.

        self._make_widgets()
        self._update_region_list()

    @property
    def curr_region(self):
        """ Current region. """
        return self.layer.gui_region_selector.value

    @property
    def region_color(self):
        return QtGui.QColor(self.curr_region.color)

    def _make_widgets(self):
        """Make grid of widgets of the single region tab.
           Do not fill the content.
        """
        grid = QtWidgets.QGridLayout()

        self.wg_region_combo = ComboBox()
        self.wg_region_combo.currentIndexChanged.connect(self._combo_set_region)
        grid.addWidget(self.wg_region_combo, 0, 0)

        self.wg_add_button = QtWidgets.QPushButton()
        self.wg_add_button.setIcon(icon.get_app_icon("add"))
        self.wg_add_button.setToolTip('Create new region')
        self.wg_add_button.clicked.connect(self._parent.add_region)
        grid.addWidget(self.wg_add_button, 0, 1)

        self.wg_remove_button = QtWidgets.QPushButton()
        self.wg_remove_button.setIcon(icon.get_app_icon("remove"))
        self.wg_remove_button.clicked.connect(self._parent.remove_region)
        grid.addWidget(self.wg_remove_button, 0, 2)

        # name
        self.wg_name = LineEdit()
        self.wg_name.editingFinished.connect(self._name_editing_finished)
        self.wg_name.textChanged.connect(self._region_name_changed)
        grid.addWidget(self.wg_name, 1, 1, 1, 2)
        name_label = QtWidgets.QLabel("Name:", self)
        name_label.setToolTip("Name of the region.")
        name_label.setBuddy(self.wg_name)
        grid.addWidget(name_label, 1, 0)

        # color button
        self.wg_color_button = QtWidgets.QPushButton()
        self.wg_color_button.setFixedSize(25, 25)
        self.wg_color_button.clicked.connect(self._set_color)
        grid.addWidget(self.wg_color_button, 2, 1)
        color_label = QtWidgets.QLabel("Color:", self)
        color_label.setBuddy(self.wg_color_button)
        grid.addWidget(color_label, 2, 0)

        # dimension (just label)
        wg_dim_label = QtWidgets.QLabel("Dimension:", self)
        grid.addWidget(wg_dim_label, 3, 0)
        self.wg_dims = QtWidgets.QLabel("", self)
        grid.addWidget(self.wg_dims, 3, 1)

        # boundary
        self.wg_boundary = QtWidgets.QCheckBox()
        self.wg_boundary.clicked.connect(self._boundary_changed)
        grid.addWidget(self.wg_boundary, 4, 1)
        wg_boundary_label = QtWidgets.QLabel("Boundary:", self)
        wg_boundary_label.setBuddy(self.wg_boundary)
        grid.addWidget(wg_boundary_label, 4, 0)

        # not use
        self.wg_notused = QtWidgets.QCheckBox()
        self.wg_notused.clicked.connect(self._not_used_checked)
        grid.addWidget(self.wg_notused, 5, 1)
        wg_notused_label = QtWidgets.QLabel("Inactive:", self)
        wg_notused_label.setBuddy(self.wg_notused)
        grid.addWidget(wg_notused_label, 5, 0)

        # mesh step
        self.wg_mesh_step_edit = QtWidgets.QLineEdit()
        self.wg_mesh_step_edit.setMinimumWidth(80)
        self.wg_mesh_step_edit.setMaximumWidth(80)
        validator = QtGui.QDoubleValidator()
        validator.setRange(0.0, 1e+7, 7)  # assuming unit in meters and dimesion fo the whole earth :-)
        self.wg_mesh_step_edit.setValidator(validator)
        self.wg_mesh_step_edit.editingFinished.connect(self._set_mesh_step)
        grid.addWidget(self.wg_mesh_step_edit, 6, 1)

        wg_mesh_step_label = QtWidgets.QLabel("Mesh step:", self)
        wg_mesh_step_label.setBuddy(self.wg_mesh_step_edit)
        grid.addWidget(wg_mesh_step_label, 6, 0)

        # self._set_visibility(layer_id, region.dim != RegionDim.none)
        sp1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sp2 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 7, 0)
        grid.addItem(sp2, 7, 1)

        self.setLayout(grid)

    def _update_region_list(self):
        """
        Update combobox according to the region list.
        :return:
        """
        with nosignal(self.wg_region_combo) as combo:
            combo.clear()
            for reg in self.le_model.regions_model.items():
                combo.addItem(self.make_combo_label(reg), reg)
        self._update_region_content()


    def make_combo_label(self, region):
        """Region label for the combo box."""
        return region.name + " (" + AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim] + ")"


    def _update_region_content(self):
        """
        Update widgets according to selected region.
        :return:
        """
        with nosignal(self.wg_region_combo) as o:
            o.setCurrentIndex(self.wg_region_combo.findData(self.curr_region))
        region = self.curr_region

        region_used = self.le_model.is_region_used(self.curr_region)
        is_default = self.curr_region == RegionItem.none
        if is_default:
            self.wg_remove_button.setEnabled(False)
            self.wg_remove_button.setToolTip('Default region cannot be removed!')
            self.wg_boundary.setEnabled(False)
            self.wg_mesh_step_edit.setEnabled(False)
        elif region_used:
            self.wg_remove_button.setEnabled(False)
            self.wg_remove_button.setToolTip('Region is still in use!')
        else:
            self.wg_remove_button.setEnabled(True)
            self.wg_remove_button.setToolTip('Remove selected region')

        self.wg_name.setText(region.name)

        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(self.region_color)
        self.wg_color_button.setIcon(QtGui.QIcon(pixmap))
        self._parent._update_tab_head(self)

        self.wg_dims.setText(AddRegionDlg.REGION_DESCRIPTION_DIM[region.dim])
        self.wg_boundary.setChecked(region.boundary)
        self.wg_notused.setChecked(region.not_used)
        self.wg_mesh_step_edit.setText("{:.6G}".format(region.mesh_step))

        none_widgets = [self.wg_boundary, self.wg_color_button, self.wg_name, self.wg_notused, self.wg_mesh_step_edit]
        if is_default:
            for wg in none_widgets:
                wg.setEnabled(False)
        else:
            for wg in none_widgets:
                wg.setEnabled(True)

        self.update()

    # ======= Internal signal handlers
    def _combo_set_region(self, combo_id):
        """
        Handle change in region combo box.
        """
        region = self.wg_region_combo.itemData(combo_id)
        self._set_region_to_selected_shapes(region)

    def _set_region_to_selected_shapes(self, region):
        self.layer.gui_region_selector.value = region
        selected_shapes = self.le_model.blocks_model.gui_block_selector.value.selection.get_selected_shape_dim_id()
        self.layer.set_region_to_selected_shapes(region, selected_shapes)
        self._parent.update_tabs()
        self.le_model.invalidate_scene.emit()

    def is_region_name_unique(self, new_name):
        """ Returns True if new name is unique otherwise False.
            If the name is the same as current name None is returned"""
        if new_name == self.curr_region.name:
            return None
        for name in self.le_model.regions_model.get_region_names():
            if name == new_name:
                return False
        return True

    def _name_editing_finished(self):
        """
        Handler of region name change.
        :return:
        """
        new_name = self.wg_name.text().strip()
        if self.is_region_name_unique(new_name):
            with undo.group("Set Name"):
                self.curr_region.set_name(new_name)
                # This line doesnt do anything at first but it gets registered in undo redo system.
                # That will cause region panel to switch to region which was changed by undoing/redoing.
                self.wg_name.blockSignals(True)
                self._parent.update_tabs()
        else:
            self.wg_name.setText(self.curr_region.name)
        self.wg_name.setToolTip("")
        # for some reason upon deleting this tab in update_tabs(), wg_name emits editingFinished again,
        # which causes problems

    def _region_name_changed(self, new_name):
        unique = self.is_region_name_unique(new_name.strip())
        if unique is None or unique:
            self.wg_name.mark_text_valid()
            self.wg_name.setToolTip("")
        else:
            self.wg_name.mark_text_invalid()
            self.wg_name.setToolTip("This name already exist")

    def _set_color(self):
        """Region color is changed, refresh diagram"""
        color_dialog = QtWidgets.QColorDialog(self.region_color)
        for icol, color in enumerate(AddRegionDlg.BACKGROUND_COLORS):
            color_dialog.setCustomColor(icol, color)
        selected_color = color_dialog.getColor()

        if selected_color.isValid():
            with undo.group("Set Color"):
                self.curr_region.set_color(selected_color.name())
                self.layer.set_gui_selected_region(self.curr_region)
                # This line doesnt do anything at first but it gets registered in undo redo system.
                # That will cause region panel to switch to region which was changed by undoing/redoing.
        self._parent.update_tabs()


    def _boundary_changed(self):
        with undo.group("Change regions boundary setting"):
            self.curr_region.set_boundary(self.wg_boundary.isChecked())
            self.layer.set_gui_selected_region(self.curr_region)
            # This line doesnt do anything at first but it gets registered in undo redo system.
            # That will cause region panel to switch to region which was changed by undoing/redoing.

    def _not_used_checked(self):
        """
        Region not used property is changed
        TODO: possibly make as region type : [regular, boundary, not used]
        """
        with undo.group("Change regions not used setting"):
            self.curr_region.set_not_used(self.wg_notused.isChecked())
            self.layer.set_gui_selected_region(self.curr_region)
            # This line doesnt do anything at first but it gets registered in undo redo system.
            # That will cause region panel to switch to region which was changed by undoing/redoing.

    def _set_mesh_step(self):
        step_value = float(self.wg_mesh_step_edit.text())
        if step_value != self.curr_region.mesh_step:
            self.wg_mesh_step_edit.setText("{:.6G}".format(step_value))
            with undo.group("Set Mesh Step"):
                self.curr_region.set_region_mesh_step(step_value)
                self.layer.set_gui_selected_region(self.curr_region)
                # This line doesnt do anything at first but it gets registered in undo redo system.
                # That will cause region panel to switch to region which was changed by undoing/redoing.

