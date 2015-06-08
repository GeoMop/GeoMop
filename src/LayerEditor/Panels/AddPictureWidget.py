import os
from copy import deepcopy
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

_DEFAULT_LIST=[["LAYER_BELOW","LAYER ABOVE"],["Layer below","Layer above"]]

class AddPictureWidget(QWidget):
    pictureListChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super(AddPictureWidget, self).__init__(parent)    
          
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding))
        self.setMinimumSize(QSize(200, 500))
        
        self._list=deepcopy(_DEFAULT_LIST)
        
        self._listWidget = QListWidget()
        self._initList();
             
        self._addButton = QPushButton("Add")
        self._addButton.clicked.connect(self._addItem)
        self._deleteButton = QPushButton("Delete")
        self._deleteButton.clicked.connect(self._deleteItem) 
        
        grid = QGridLayout()
        grid.addWidget(self._addButton, 0, 0)
        grid.addWidget(self._deleteButton, 0, 1)
             
        self._fileName = QLineEdit()
        self._fileButton = QPushButton("...")
        self._fileButton.clicked.connect(self._addPicture)
        
        fileLayeout=QHBoxLayout()        
        fileLayeout.addWidget( self._fileName)        
        fileLayeout.addWidget( self._fileButton)
        
        label = QLabel("Picture File:")
        
        layout = QVBoxLayout()
        layout.addWidget(self._listWidget)
        layout.addLayout(grid)
        layout.addWidget(label)
        layout.addLayout(fileLayeout)
        self.setLayout(layout)
   
    def getPicturePaths(self):
        items=self._listWidget.selectedItems()
        pictures=[]
        
        for item in items:
            i=self._listWidget.row(item)
            pictures.append(self._list[0][i])
        return pictures
    
    def _initList(self):
        self._listWidget.addItems(_DEFAULT_LIST[1])
        self._listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._listWidget.itemSelectionChanged.connect(self._selectionChanged)

        for i in range(0,len(self._list)-1):
            item=self._listWidget.item(i)
            item.setToolTip(self._list[0][i])            
       
    def _addItem(self):
        path=self._fileName.text()
        if not path:
            return
        name=os.path.basename(path)
        if not name:
            return 
            
        self._list[0].append(path)
        self._list[1].append(name)
             
        item=QListWidgetItem(name)     
        self._listWidget.addItem(item)
        item.setToolTip(path) 
         
    def _deleteItem(self):
        items=self._listWidget.selectedItems()
        for item in items:
            i=self._listWidget.row(item)
            removeItemWidget(item)

            self._list[0].remove(i)
            self._list[1].remove(i)         
     
    def _addPicture(self):
        from os.path import expanduser
        home = expanduser("~")
        picture= QFileDialog.getOpenFileName(self,"Choose Picture", home,
                        "Images (*.png *.xpm *.jpg)")
        if picture[0]:
            self._fileName.setText(picture[0])
            
    def _selectionChanged(self):
        self.pictureListChanged.emit()
