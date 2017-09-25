import pytest
from polygons import *
import matplotlib.pyplot as plt
from matplotlib import collections  as mc


class TestPolygons:
    def plot_polygons(self, decomp):
        x_pts = []
        y_pts = []
        for p in decomp.points:
            x_pts.append(p.point[0])
            y_pts.append(p.point[1])
        plt.plot(x_pts, y_pts, 'bo', color = 'red')

        lines = []
        for s in decomp.segments:
            lines.append( [ (s.points[0].points[0], s.points[1].points[0]), (s.points[0].points[1], s.points[1].points[1]) ] )

        plt.plot(*lines, color ='green', linewidths=2)
        #lc = mc.LineCollection(lines, linewidths=2)
        #fig, ax = plt.subplots()
        #ax.add_collection(lc)

        for poly in decomp.polygons:
            if poly.id == 0:
                continue
            x_pts = []
            y_pts = []
            for e in poly.edges():
                x_pts.append(e.points[0].point[0])
                y_pts.append(e.points[0].point[1])
            plt.plot(x_pts, y_pts, color='blue')

    def test_decomp(self):
        decomp = PolygonDecomposition()
        decomp.set_tolerance(0.01)
        decomp.add_point(0, 0)
        self.plot_polygons(decomp)
        decomp.add_point(1, 0)
        decomp.connect(a, b)
        decomp.add_line( (0,0), (0,1) )
        decomp.add_line( (-0.5, 1), (1, -0.5))  # new polygon
        decomp.add_point( 0.3, 0.3)
        decomp.add_line( (-0.1, -0.1), (0.3, 0.3) )
        decomp.add_line( (0.3, 0.3), (1, 1))
        self.plot_polygons(decomp)