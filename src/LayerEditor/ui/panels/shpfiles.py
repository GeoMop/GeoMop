"""
Tree widget panel

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from ui.data.shp_structures import ShpDisp
from ui.menus.shpfiles import ShpFilesMenu

class ShpFiles(QtWidgets.QTableWidget):
    """Widget displays the config file structure in table.

    pyqtSignals:
        * :py:attr:`background_changed() <background_changed>`
        * :py:attr:`item_removed(int) <item_removed>`
    """
    
    background_changed = QtCore.pyqtSignal()
    """Signal is sent whenbackground settings was changes.
    """

    item_removed = QtCore.pyqtSignal(int)
    """Signal is sent when item is deleted from background settings
    """

    def __init__(self, data, parent=None):
        """Initialize the class."""
        super(ShpFiles, self).__init__(parent)
        
        self.data = data       
        self.setColumnCount(3)
        
        #self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()
        
        labels = ['File/Attr. value', 'Show',  'Set off']
        self.setHorizontalHeaderLabels(labels)
        self.reload()
    
    def reload(self):
        """Start of reload data from config.""" 
        row_count = 0
        
        self.s_checkboxes = []
        self.h_checkboxes = []
        
        for shp in self.data.datas:
            row_count += 1 + len(shp.av_names)           
        self.clearContents()
        self.setRowCount( row_count)
        i_row = 0
        for i in range(0, len(self.data.datas)):
            self.s_checkboxes.append([])
            self.h_checkboxes.append([])            
            shp = self.data.datas[i]
            
            # description
            # splitter.setToolTip(shp. file)
            pom_lamda = lambda ii, label: lambda pos: self.context_menu(pos, ii, label)
            label = QtWidgets.QLabel(shp.file_name)
            label.setToolTip(shp. file) 
            label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu);    
            label.customContextMenuRequested.connect(pom_lamda(i, label));
            self.setCellWidget(i_row, 0, label) 
            
            pom_lamda = lambda ii, button: lambda: self.color_set(ii, button)
            color_button = QtWidgets.QPushButton()
            pixmap = QtGui.QPixmap(25, 25)
            pixmap.fill(shp.color)
            icon = QtGui.QIcon(pixmap)
            color_button.setIcon(icon)
            color_button.setFixedSize( 25, 25 )
            color_button.clicked.connect(pom_lamda(i, color_button))
            self.setCellWidget(i_row, 1, color_button) 

            pom_lamda = lambda ii, combo: lambda: self.attr_set(ii, combo)
            attr_combo = QtWidgets.QComboBox()
            attr_combo.addItems(shp.attrs)
            attr_combo.setCurrentText(shp.attrs[shp.attr])
            attr_combo.currentIndexChanged.connect(pom_lamda(i, attr_combo))
            self.setCellWidget(i_row, 2, attr_combo) 
            i_row += 1
            
            s_pom_lamda = lambda ii, jj: lambda: self.show_set(ii, jj)
            h_pom_lamda = lambda ii, jj: lambda: self.highlight_set(ii, jj)
            for j in range(0, len(shp.av_names)):
                self.setItem(i_row, 0, QtWidgets.QTableWidgetItem("  " + shp.av_names[j]))
                self.s_checkboxes[i].append(QtWidgets.QCheckBox())
                self.s_checkboxes[i][j].setChecked(shp.av_show[j])
                self.setCellWidget(i_row, 1, self.s_checkboxes[i][j])
                self.s_checkboxes[i][j].stateChanged.connect(s_pom_lamda(i, j))
                self.h_checkboxes[i].append(QtWidgets.QCheckBox())
                self.h_checkboxes[i][j].setChecked(shp.av_highlight[j])
                self.setCellWidget(i_row, 2, self.h_checkboxes[i][j])
                self.h_checkboxes[i][j].stateChanged.connect(h_pom_lamda(i, j))
                i_row += 1
        
        self.resizeColumnsToContents()
            
    def context_menu(self, pos,  file_idx, label):
        """Call context menu above clicked label"""
        menu = ShpFilesMenu(label, self, file_idx)
        menu.exec_(label.mapToGlobal(pos))
        
    def remove(self, file_idx):
        """remove shape file context from panel"""
        self.item_removed.emit(file_idx)
        self.reload()
            
    def color_set(self, file_idx, color_button):
        """Shapefile color is changed, refresh diagram"""
        shp = self.data.datas[file_idx]
        color_dia = QtWidgets.QColorDialog(shp.color)
        i = 0
        for color in ShpDisp.BACKGROUND_COLORS:
            color_dia.setCustomColor(i,  color)            
            i += 1
        selected_color = color_dia.getColor()        
        
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(selected_color)
        icon = QtGui.QIcon(pixmap)
        color_button.setIcon(icon)
        
        shp.set_color(selected_color)
        self.background_changed.emit()
        
    def attr_set(self, file_idx, attr_combo):
        """Shapefile dislayed attribute is changed, refresh diagram"""
        shp = self.data.datas[file_idx]
        attr = attr_combo.currentIndex()
        shp.set_attr(attr)
        self.reload()
        self.background_changed.emit()

    def show_set(self, file_idx, shp_idx):
        """Some dislayed attribute value is changed, refresh diagram"""
        checkbox = self.s_checkboxes[file_idx][shp_idx]
        shp = self.data.datas[file_idx]
        shp.set_show(shp_idx, checkbox.isChecked())
        self.background_changed.emit()
         
    def highlight_set(self, file_idx, shp_idx):
        """Some highlighted attribute value is changed, refresh diagram"""
        checkbox = self.h_checkboxes[file_idx][shp_idx]
        shp = self.data.datas[file_idx]
        shp.set_highlight(shp_idx, checkbox.isChecked()) 
        self.background_changed.emit()
