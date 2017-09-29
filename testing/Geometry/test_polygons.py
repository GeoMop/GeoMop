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
        pt0 = Point( [0.0, 0.0], None)
        assert pt0.insert_segment(vec) == None

        pt1 = Point( [0.0, 1.0], None)
        seg0 = Segment( (pt0, pt1))
        seg0.next = [ (seg0, left_side), (seg0, right_side)]
        pt0.segment = (seg0, out_vtx)
        pt1.segment = (seg0, in_vtx)
        assert pt0.insert_segment(vec) == ( (seg0, right_side), (seg0, left_side), None)


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
        outer = decomp.outer_polygon

        # test add point
        pt_a = decomp.add_point(  [0, 0] )
        assert pt_a.poly == outer
        pt_b = decomp.add_point( [1, 0] )
        assert pt_a.poly == outer

        # test snap to point
        pt = decomp.snap_point([0, 5e-3])
        assert pt == (0, pt_a, None)
        pt = decomp.snap_point([5e-3, 5e-3])
        assert pt == (0, pt_a, None)
        pt = decomp.snap_point([1+5e-3, 5e-3])
        assert pt == (0, pt_b, None)

        # test new_segment and add_line - simple cases
        sg_c = decomp.new_segment(pt_a, pt_b)
        res = decomp.add_line( (0,0), (0,1) )
        assert len(res) == 1
        sg_d = res[0]
        assert sg_d.next[left_side] == (sg_d, right_side)
        assert sg_d.next[right_side] == (sg_c, left_side)
        assert sg_c.next[left_side] == (sg_c, right_side)
        assert sg_c.next[right_side] == (sg_d, left_side)
        assert pt_a.poly == None
        assert pt_a.segment == (sg_c, out_vtx)

        res = decomp.add_line( (2,0), (3,1) )


        # test snap point - snap to line
        pt = decomp.snap_point([0.5, 5e-3])
        assert pt == (1, sg_c, 0.5)
        pt = decomp.snap_point([5e-3, 0.3])
        assert pt == (1, sg_d, 0.3)
        pt = decomp.snap_point([1+5e-3, 5e-3])
        assert pt == (0, pt_b, None)

        print(decomp)
        decomp.add_line( (2.5,0), (3, 0.5))
        decomp.add_line((2,1), (3,0))           # _join_wires
        print(decomp)
        self.plot_polygons(decomp)


#        decomp.add_line( (-0.5, 1), (1, -0.5))  # new polygon
#        self.plot_polygons(decomp)

#        decomp.add_point( [0.3, 0.3] )
#        decomp.add_line( (-0.1, -0.1), (0.3, 0.3) )
#        decomp.add_line( (0.3, 0.3), (1, 1))
