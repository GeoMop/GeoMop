import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

def getWhitePixmap(dx, dy):
    pixmap = QtGui.QPixmap(dx, dy)
    painter = QtGui.QPainter(pixmap)
    painter.setBrush(QtGui.QColor(QtCore.Qt.white))
    painter.drawRect(0, 0, dx, dy)
    return pixmap
