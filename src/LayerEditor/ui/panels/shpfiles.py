"""
Tree widget panel

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

class ShpFiles(QtWidgets.QTableWidget):
    """Widget displays the config file structure in table.

    pyqtSignals:
        * :py:attr:`background_changed() <itemSelected>`
    """

    background_changed = QtCore.pyqtSignal()
    """Signal is sent whenbackground settings was changes.
    """

    def __init__(self, data, parent=None):
        """Initialize the class."""
        super(ShpFiles, self).__init__(parent)
        
        self.data = data
        self.setMinimumSize(250, 400)
        self.setMaximumWidth(450)
        self.setColumnCount(3)
        
        #self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()
        
        labels = ['File/Attr. value', 'Show',  'Set off']
        self.setHorizontalHeaderLabels(labels)
        self.reload()

    def reload(self):
        """Start of reload data from config.""" 
        row_count = 0
        for shp in self.data.datas:
            row_count += 1 + len(shp.av_names)           
        self.clearContents()
        self.setRowCount( row_count)
        i_row = 0
        for i in range(0, len(self.data.datas)):
            shp = self.data.datas[i]
            # description
            splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            splitter.setToolTip(shp. file)
            label = QtWidgets.QLabel(shp.file_name)
            splitter.addWidget(label)
            color_button = QtWidgets.QPushButton()
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(shp.color)
            icon = QtGui.QIcon(pixmap)
            color_button.setIcon(icon)
            color_button.setFixedSize( 16, 16 )
            color_button.clicked.connect(lambda: self.color_set(i, color_button))
            splitter.addWidget(color_button)
            attr_combo = QtWidgets.QComboBox()
            attr_combo.addItems(shp.attrs)
            attr_combo.setCurrentText(shp.attrs[shp.attr])
            attr_combo.currentIndexChanged.connect(lambda: self.attr_set(i, attr_combo))
            splitter.addWidget(attr_combo)
            self.setCellWidget(i_row, 0, splitter)          
            i_row += 1
            
            for j in range(0, len(shp.av_names)):
                self.setItem(i_row, 0, QtWidgets.QTableWidgetItem("  " + shp.av_names[j]))
                checkbox = QtWidgets.QCheckBox()
                checkbox.setChecked(shp.av_show[j])
                self.setCellWidget(i_row, 1, checkbox)
                checkbox.stateChanged.connect(lambda: self.show_set(i, j, checkbox))
                checkbox = QtWidgets.QCheckBox()
                checkbox.setChecked(shp.av_highlight[j])
                self.setCellWidget(i_row, 2, checkbox)
                checkbox.stateChanged.connect(lambda: self.highlight_set(i, j, checkbox))
                i_row += 1
        
        self.resizeColumnsToContents()
            
    def color_set(self, file_idx, color_button):
        """Shapefile color is changed, refresh diagram"""
        shp = self.data.datas[file_idx]
        color_dia = QtWidgets.QColorDialog()
        color_dia.setCustomColor(0,  shp.color)
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

    def show_set(self, file_idx, shp_idx, checkbox):
        """Some dislayed attribute value is changed, refresh diagram"""
        shp = self.data.datas[file_idx]
        shp.set_show(shp_idx, checkbox.isChecked())
         
    def highlight_set(self, file_idx, shp_idx, checkbox):
        """Some highlighted attribute value is changed, refresh diagram"""
        shp = self.data.datas[file_idx]
        shp.set_highlight(shp_idx, checkbox.isChecked()) 
