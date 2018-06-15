import sys
import PyQt5.QtWidgets as QtWidgets

import pytest
pytest.importorskip("PyQt5.QtSvg")
import PyQt5.QtSvg as QtSvg


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    scene = QtWidgets.QGraphicsScene()
    view = QtWidgets.QGraphicsView(scene)
    
    class Node(QtSvg.QGraphicsSvgItem):
        def __init__(self, file, parent = None):
            QtSvg.QGraphicsSvgItem.__init__(self, file, parent)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

    item = Node("/home/pavel/work/workflow/test5.svg")

    scene.addItem(item)
    view.show()
    sys.exit(app.exec_())
