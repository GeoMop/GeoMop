import pytest

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches as mp
from matplotlib import collections  as mc

from polygons import *
import numpy as np

class TestPoint:
    def test_insert_segment(self):
        decomp = PolygonDecomposition()
        pt0 = decomp.points.append(Point( [0.0, 0.0], None))
        assert pt0.insert_segment(np.array([10, 1])) == None

        pt1 = decomp.points.append(Point( [0.0, 1.0], None))
        seg0 = decomp.segments.append(Segment( (pt0, pt1)))
        seg0.next = [ (seg0, left_side), (seg0, right_side)]
        pt0.segment = (seg0, out_vtx)
        pt1.segment = (seg0, in_vtx)

        assert pt0.insert_segment(np.array([10, 1])) == ( (seg0, right_side), (seg0, left_side), None)
        assert pt0.insert_segment(np.array([-10, -1])) == ((seg0, right_side), (seg0, left_side), None)

        pt2 = decomp.points.append(Point([0.0, -1], None))
        seg1 = decomp.segments.append(Segment( (pt2, pt0) ))
        pt2.segment = (seg1, out_vtx)
        pt3 = decomp.points.append(Point([-1, 0], None))
        seg2 = decomp.segments.append(Segment( (pt0, pt3) ))
        pt2.segment = (seg1, in_vtx)
        seg0.next[right_side] = (seg1, right_side)
        seg1.next[right_side] = (seg1, left_side)
        seg1.next[left_side] = (seg2, left_side)
        seg2.next[left_side] = (seg2, right_side)
        seg2.next[right_side] = (seg0, left_side)

        assert pt0.insert_segment(np.array([10, 1])) == ((seg0, right_side), (seg1, right_side), None)
        assert pt0.insert_segment(np.array([-10, -1])) == ((seg1, left_side), (seg2, left_side), None)
        assert pt0.insert_segment(np.array([-10, +1])) == ((seg2, right_side), (seg0, left_side), None)

class TestPolygons:
    def plot_polygon(self, polygon):
        if polygon is None or polygon.displayed or polygon.outer_wire == None:
            return []
        if polygon.outer_wire.parent is not None:
            patches = self.plot_polygon( polygon.outer_wire.parent.polygon )
        else:
            patches = []
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

        # test new_segment, new_wire
        sg_c = decomp.new_segment(pt_a, pt_b)
        assert len(decomp.polygons) == 1
        assert len(decomp.outer_polygon.holes) == 1

        # test add_line - new_segment, add_dendrite
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
        sg_x, = res
        assert len(decomp.polygons) == 1
        assert len(decomp.outer_polygon.holes) == 2


        # test snap point - snap to line
        pt = decomp.snap_point([0.5, 5e-3])
        assert pt == (1, sg_c, 0.5)
        pt = decomp.snap_point([5e-3, 0.3])
        assert pt == (1, sg_d, 0.3)
        pt = decomp.snap_point([1+5e-3, 5e-3])
        assert pt == (0, pt_b, None)

        print(decomp)
        # test _split_segment

        result = decomp.add_line((2,1), (3,0))           # _join_wires
        sg_e, sg_f = result

        assert sg_e.vtxs[in_vtx].colocated((2,1), 0.001)
        assert sg_e.vtxs[out_vtx].colocated((2.5, 0.5), 0.001)
        assert sg_f.vtxs[out_vtx].colocated((2.5, 0.5), 0.001)
        assert sg_f.vtxs[in_vtx].colocated((3, 0), 0.001)

        assert sg_e.next[left_side] == (sg_e, right_side)
        sg_h = sg_e.next[right_side][0]
        assert sg_e.next[right_side] == (sg_h, left_side)
        assert sg_h.next[left_side] == (sg_h, right_side)
        assert sg_h.next[right_side] == (sg_f, left_side)
        assert sg_f.next[left_side] == (sg_f, right_side)
        sg_g = sg_f.next[right_side][0]
        assert sg_f.next[right_side] == (sg_g, right_side)
        assert sg_g.next[right_side] == (sg_g, left_side)
        assert sg_g.next[left_side] == (sg_e, left_side)
        decomp.add_line((2.5, 0), (3, 0.5))

        #self.plot_polygons(decomp)



        decomp.add_line( (-0.5, 1), (1, -0.5))  # new polygon
        print("Decomp:\n", decomp)
        self.plot_polygons(decomp)

#        decomp.add_point( [0.3, 0.3] )
#        decomp.add_line( (-0.1, -0.1), (0.3, 0.3) )
#        decomp.add_line( (0.3, 0.3), (1, 1))
