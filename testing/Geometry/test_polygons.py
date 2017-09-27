import pytest

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches as mp
from matplotlib import collections  as mc

from polygons import *
import numpy as np

class TestPoint:
    def test_insert_segment(self):
        vec = np.array([10, 1])
        pt = Point( [0.0, 0.0], None)
        assert pt.insert_segment(vec) == (None, None, None,None)

        pt0 = Point( [0.0, 1.0], None)
        seg0 = Segment( (pt, pt0))
        seg0.next = [seg0, seg0]
        pt.segment = seg0
        pt0.segment = seg0
        assert pt.insert_segment(vec) == (seg0, seg0, right_side, None)


class TestPolygons:
    def plot_polygon(self, polygon):
        if polygon is None or polygon.displayed or polygon.outer_wire == None:
            return []
        patches = self.plot_polygon( polygon.outer_wire.polygon )
        pts = []
        for seg, side in polygon.outer_wire.outer_segments():
            pts.append(seg.vtxs[0].xy)
        patches.append(mp.Polygon(pts))
        return patches

    def plot_polygons(self, decomp):
        fig, ax = plt.subplots()

        # polygons
        for poly in decomp.polygons.values():
            poly.displayed = False

        patches = []
        for poly in decomp.polygons.values():
            patches.extend( self.plot_polygon(poly) )
        p = mc.PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)

        ax.add_collection(p)

        #lines = []
        for s in decomp.segments.values():
            #lines.append( [ (s.vtxs[0].xy[0], s.vtxs[1].xy[0]), (s.vtxs[0].xy[1], s.vtxs[1].xy[1]) ] )
            ax.plot((s.vtxs[0].xy[0], s.vtxs[1].xy[0]), (s.vtxs[0].xy[1], s.vtxs[1].xy[1]), color='green')


        #lc = mc.LineCollection(lines, linewidths=2)
        #fig, ax = plt.subplots()
        #ax.add_collection(lc)
        x_pts = []
        y_pts = []
        for pt in decomp.points.values():
            x_pts.append(pt.xy[0])
            y_pts.append(pt.xy[1])
        ax.plot(x_pts, y_pts, 'bo', color = 'red')

        plt.show()

    def test_decomp(self):

        decomp = PolygonDecomposition()
        decomp.set_tolerance(0.01)
        a = decomp.add_point(  [0, 0] )
        b = decomp.add_point( [1, 0] )
        c = decomp.new_segment(a, b)
        #self.plot_polygons(decomp)

        res = decomp.add_line( (0,0), (0,1) )
        assert len(res) == 1
        d = res[0]
        assert d.next[left_side] == d
        assert d.next[right_side] == c
        assert c.next[left_side] == c
        assert c.next[right_side] == d

        self.plot_polygons(decomp)
        decomp.add_line( (-0.5, 1), (1, -0.5))  # new polygon
        decomp.add_point( [0.3, 0.3] )
        decomp.add_line( (-0.1, -0.1), (0.3, 0.3) )
        decomp.add_line( (0.3, 0.3), (1, 1))
