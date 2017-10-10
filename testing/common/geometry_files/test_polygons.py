import matplotlib.pyplot as plt
import numpy as np
from matplotlib import collections  as mc
from matplotlib import patches as mp

from geometry_files.polygons import *


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


class TestWire:
    def test_contains(self):
        decomp = PolygonDecomposition()
        sg_a, = decomp.add_line((0,0), (2,0))
        sg_b, = decomp.add_line((2, 0), (2, 2))
        sg_c, = decomp.add_line((2, 2), (0, 2))
        sg_d, = decomp.add_line((0, 2), (0, 0))
        in_wire = sg_a.wire[left_side]
        assert in_wire.contains_point([-1, 1]) == False
        assert in_wire.contains_point([-0.0001, 1]) == False
        assert in_wire.contains_point([+0.0001, 1]) == True
        assert in_wire.contains_point([1.999, 1]) == True
        assert in_wire.contains_point([2.0001, 1]) == False
        assert in_wire.contains_point([0, 1]) == True
        assert in_wire.contains_point([2, 1]) == False

    def test_join_wires(self):
        decomp = PolygonDecomposition()
        sg, = decomp.add_line((0, 0), (0, 2))
        pt0 = sg.vtxs[0]
        decomp.add_line((0, 0), (2, 0))
        decomp.add_line((0, 2), (2, 0))

        sg4, = decomp.add_line((.5,.5), (0.6,0.6))
        decomp.new_segment(sg4.vtxs[0], pt0)
        assert len(decomp.wires) == 3


class TestPolygons:
    def plot_polygon(self, polygon):
        if polygon is None or polygon.displayed or polygon.outer_wire == None:
            return []
        if polygon.outer_wire.parent is not None:
            patches = self.plot_polygon( polygon.outer_wire.parent.polygon )
        else:
            patches = []
        pts = [ pt.xy for pt in polygon.vertices() ]

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
        p = mc.PatchCollection(patches, color='blue', alpha=0.2)

        ax.add_collection(p)


        for s in decomp.segments.values():
            ax.plot((s.vtxs[0].xy[0], s.vtxs[1].xy[0]), (s.vtxs[0].xy[1], s.vtxs[1].xy[1]), color='green')

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
        assert decomp.get_last_polygon_changes() == (PolygonChange.add, outer.id, outer.id)

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
        assert len(decomp.outer_polygon.outer_wire.childs) == 1
        assert decomp.get_last_polygon_changes() == (PolygonChange.none, None, None)


        # test line matching existing segment
        sg_c = decomp.new_segment(pt_a, pt_b)
        sg_c = decomp.new_segment(pt_b, pt_a)

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
        assert decomp.get_last_polygon_changes() == (PolygonChange.shape, outer.id, None)

        res = decomp.add_line( (2,0), (3,1) )
        sg_x, = res
        assert len(decomp.polygons) == 1
        assert len(decomp.outer_polygon.outer_wire.childs) == 2


        # test snap point - snap to line
        pt = decomp.snap_point([0.5, 5e-3])
        assert pt == (1, sg_c, 0.5)
        pt = decomp.snap_point([5e-3, 0.3])
        assert pt == (1, sg_d, 0.3)
        pt = decomp.snap_point([1+5e-3, 5e-3])
        assert pt == (0, pt_b, None)

        print(decomp)
        # test _split_segment, new segment - add_dendrite
        result = decomp.add_line((2,1), (3,0))
        sg_e, sg_f = result
        assert decomp.get_last_polygon_changes() == (PolygonChange.shape, outer.id, None)

        assert sg_e.vtxs[out_vtx].colocated((2,1), 0.001)
        assert sg_e.vtxs[in_vtx].colocated((2.5, 0.5), 0.001)
        assert sg_f.vtxs[out_vtx].colocated((2.5, 0.5), 0.001)
        assert sg_f.vtxs[in_vtx].colocated((3, 0), 0.001)

        assert sg_e.next[right_side] == (sg_e, left_side)
        sg_h = sg_e.next[left_side][0]
        assert sg_e.next[left_side] == (sg_h, left_side)
        assert sg_h.next[left_side] == (sg_h, right_side)
        assert sg_h.next[right_side] == (sg_f, left_side)
        assert sg_f.next[left_side] == (sg_f, right_side)
        sg_g = sg_f.next[right_side][0]
        assert sg_f.next[right_side] == (sg_g, right_side)
        assert sg_g.next[right_side] == (sg_g, left_side)
        assert sg_g.next[left_side] == (sg_e, right_side)
        sg_o, sg_p = decomp.add_line((2.5, 0), (3, 0.5))

        # test add_point on segment
        decomp.add_point((2.25, 0.75))
        #self.plot_polygons(decomp)


        # test new_segment - split polygon
        decomp.add_line( (-0.5, 1), (0.5, 0))
        assert decomp.get_last_polygon_changes() == (PolygonChange.add, outer.id, 2)

        # test split_segment in vertex
        decomp.add_line( (2,0.5), (2,-0.5))

        # test new_segment - join_wires
        assert len(decomp.wires) == 4
        assert len(decomp.polygons) == 2

        print(decomp)
        sg_m, = decomp.add_line((0, 1), (2, 1))
        print(decomp)



        assert len(decomp.wires) == 3
        assert len(decomp.polygons) == 2
        assert decomp.get_last_polygon_changes() == (PolygonChange.shape, outer.id, None)

        #self.plot_polygons(decomp)

        # delete segment - split wire
        decomp.delete_segment(sg_m)
        assert len(decomp.wires) == 4
        assert len(decomp.polygons) == 2
        #self.plot_polygons(decomp)
        assert decomp.get_last_polygon_changes() == (PolygonChange.shape, outer.id, None)

        # other split wire
        pt_op = sg_p.vtxs[out_vtx]
        decomp.delete_segment(sg_f)
        assert len(decomp.wires) == 5
        assert len(decomp.polygons) == 2
        #self.plot_polygons(decomp)

        #test split_segment connected on both sides; split non outer polygon
        seg_y, = decomp.add_line( (0,0.25), (0.25, 0.25))
        assert decomp.get_last_polygon_changes() == (PolygonChange.split, 2, 3)

        # test _join_segments - _split_segment inversion
        seg1 = sg_e
        mid_point = seg1.vtxs[in_vtx]
        seg0 = sg_e.next[left_side][0]
        decomp._join_segments(mid_point, seg0, seg1)

        # print("Decomp:\n", decomp)
        decomp.delete_point(pt_op)
        # self.plot_polygons(decomp)

        # test join polygons
        decomp.delete_segment(seg_y)
        assert decomp.get_last_polygon_changes() == (PolygonChange.join, 2, 3)

        # test add_free_point
        decomp.add_free_point(100, (3.0, 0.3), decomp.outer_polygon.id)
        decomp.remove_free_point(100)

    def test_split_poly(self):

        decomp = PolygonDecomposition()
        sg_a, = decomp.add_line((0,0), (2,0))
        sg_b, = decomp.add_line((2, 0), (2, 2))
        sg_c, = decomp.add_line((2, 2), (0, 2))
        sg_d, = decomp.add_line((0, 2), (0, 0))
        # closed outer polygon


        assert sg_a.next == [ (sg_d, 0), (sg_b, 1)]
        assert sg_b.next == [ (sg_a, 0), (sg_c, 1)]
        assert sg_c.next == [ (sg_b, 0), (sg_d, 1)]
        assert sg_d.next == [ (sg_c, 0), (sg_a, 1)]

        external_wire = list(decomp.outer_polygon.outer_wire.childs)[0]
        assert sg_a.wire[right_side] == external_wire
        assert sg_b.wire[right_side] == external_wire
        assert sg_c.wire[right_side] == external_wire
        assert sg_d.wire[right_side] == external_wire
        #self.plot_polygons(decomp)


        assert len(decomp.polygons) == 2
        sg_e, =decomp.add_line((0.5, 0.5), (1, 0.5))
        decomp.add_line((1, 0.5), (1, 1))
        decomp.add_line((1, 1), (0.5, 1))
        seg_in_x, = decomp.add_line((0.5, 1), (0.5, 0.5))
        # closed inner polygon
        print("Decomp:\n", decomp)



        # join nested wires
        sg_x = decomp.new_segment( sg_a.vtxs[out_vtx], sg_e.vtxs[out_vtx] )
        #self.plot_polygons(decomp)
        #print("Decomp:\n", decomp)
        decomp.delete_segment(sg_x)

        #self.plot_polygons(decomp)
        #print("Decomp:\n", decomp)
        # join polygons - nested case
        decomp.delete_segment(seg_in_x)
        #self.plot_polygons(decomp)

    def test_split_poly_1(self):
        # Test splitting of points and holes.
        decomp = PolygonDecomposition()
        decomp.add_line((0, 0), (1,0))
        decomp.add_line((0, 0), (0, 1))
        decomp.add_line((1, 1), (1, 0))
        decomp.add_line((1, 1), (0, 1))
        decomp.add_point( (0.2,0.2))
        decomp.add_point( (0.8, 0.2))
        decomp.add_line((0.2, 0.6), (0.3,0.6))
        decomp.add_line((0.8, 0.6), (0.7, 0.6))
        #self.plot_polygons(decomp)
        decomp.add_line((0.5,0), (0.5,1))
        #self.plot_polygons(decomp)


    def test_join_poly(self):
        decomp = PolygonDecomposition()
        sg0, = decomp.add_line((0, 0), (0, 2))
        decomp.add_line((0, 0), (2, 0))
        sg2, = decomp.add_line((0, 2), (2, 0))
        decomp.delete_segment(sg2)

    def test_make_indices(self):
        decomp = PolygonDecomposition()
        sg0, = decomp.add_line((0, 0), (0, 2))
        decomp.add_line((0, 0), (2, 0))
        sg2, = decomp.add_line((0, 2), (2, 0))
        decomp.make_indices()
        assert sg2.index == 2
        assert decomp.polygons[1].index == 0
        assert decomp.polygons[2].index == 1

    def test_check_displacement(self):
        decomp = PolygonDecomposition()
        sg, = decomp.add_line((0, 0), (0, 2))
        pt0 = sg.vtxs[0]
        decomp.add_line((0, 0), (2, 0))
        decomp.add_line((0, 2), (2, 0))
        pt = decomp.add_point((.5,.5))
        decomp.add_line((0, 0), (.5,.5))
        decomp.add_line((2, 0), (.5,.5))
        decomp.add_line( (.5,.5), (0, 2))

        step = decomp.check_displacment([pt0, pt], (1.0, 1.0), 0.1)
        assert la.norm( step - np.array([0.45, 0.45]) ) < 1e-6

        decomp.move_points([pt], step)
        assert la.norm( pt.xy - np.array([0.95, 0.95]) ) < 1e-6


    def test_join_segments(self):
        decomp = PolygonDecomposition()
        sg0, = decomp.add_line((0,0), (1,0))
        mid_pt = sg0.vtxs[1]
        sg1, = decomp.add_line((2,0), (1,0))
        sg2, = decomp.add_line((2, 0), (3, 0))
        decomp._join_segments(sg0.vtxs[1], sg0, sg1)
        decomp._join_segments(sg0.vtxs[1], sg0, sg2)