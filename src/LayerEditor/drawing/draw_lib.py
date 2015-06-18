import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

def getWhitePixmap(dx, dy):
    """Initialize white pixmap with set size"""
    pixmap = QtGui.QPixmap(dx, dy)
    painter = QtGui.QPainter(pixmap)
    painter.setBrush(QtGui.QColor(QtCore.Qt.white))
    painter.drawRect(-1, -1, dx+2, dy+2)
    return pixmap

def drawPictureTiPixmap(path, drawInRect, pixmap,  opaque):
    """
    Draw picture  in pixmap to set coordinate.
    """
    painter = QtGui.QPainter(pixmap)
    picture = QtGui.QPixmap(path)
    painter.setOpacity(opaque/100)
    painter.drawPixmap(drawInRect, picture, picture.rect())
