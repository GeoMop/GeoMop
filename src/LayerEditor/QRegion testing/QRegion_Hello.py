import sys
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        self.text = "hello world"
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Draw Demo')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor(Qt.red))
        qp.setFont(QFont('Arial', 20))
        qp.setBrush(QColor(200, 0, 0))
        self.drawShapes(qp)
        qp.end()

    def drawShapes(self, QPaint):

        # #TEST: DRAW LINE
        # QPaint.drawText(10, 50, "hello Python")
        # QPaint.setPen(QColor(Qt.blue))
        # QPaint.drawLine(10, 100, 100, 100)
        # QPaint.drawRect(10, 150, 150, 100)

        # #TEST: CUBIC SPLINE
        # path = QPainterPath(QPointF(10, 120))
        # path.cubicTo(QPointF(30,110), QPointF(60,140), QPointF(100,120))
        # QPaint.drawPath(path)

        # #TEST: POLYGON
        points = [10, 20, 10, 200, 250, 200, 250, 50]
        polygon = QPolygon();
        polygon.setPoints(points)
        # QPaint.drawPolygon(polygon)

        points = [40, 40, 200, 170, 200, 80]
        polygon2 = QPolygon();
        polygon2.setPoints(points)

        # #TEST: EDGE
        # points = [10, 50, 30, 50]
        # edge = QPolygon();
        # edge.setPoints(points)
        # QPaint.drawPolygon(edge)

        # #TEST: POINT
        # points = [10, 70]
        # point = QPolygon();
        # point.setPoints(points)
        # QPaint.drawPolygon(point)

        # REGIONS SETUP
        #clip = QRegion(QRect(0,0,400,300))
        clip = QRegion(polygon)
        clip -= QRegion(polygon2)
        QPaint.setClipRegion(clip)

        QPaint.drawPolygon(polygon)
        QPaint.drawPolygon(polygon2)

        # TEST: SETUP ELLIPSE INTERSECTING
        QPaint.setPen(QColor(Qt.yellow))
        QPaint.drawEllipse(100, 50, 100, 50)
        # QPaint.drawPixmap(220, 10, QPixmap("python.jpg"))
        # QPaint.fillRect(200, 175, 150, 100, QBrush(Qt.SolidPattern))


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()