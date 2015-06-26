import PyQt5.QtWidgets as QtWidgets
from data.meconfig import MEConfig as cfg

class TreeWidget(QtWidgets.QTreeView):

    def __init__(self):
        QtWidgets.QTreeView.__init__(self)
    
    def reload(self):
        """reload data from config"""
        
#    model = QtGui.QFileSystemModel()
#    model.setRootPath( QtCore.QDir.currentPath() )
#    self.setModel(model)
#    QtCore.QObject.connect(self.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.test)
#
#  @QtCore.pyqtSlot("QItemSelection, QItemSelection")
#  def test(self, selected, deselected):
#      print("hello!")
#      print(selected)
#      print(deselected) 
 

