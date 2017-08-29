import unittest
import brep_writer as bw
import sys



class TestConstructors(unittest.TestCase):
    def test_Location(self):
        print( "test locations")
        la = bw.Location([[1, 0, 0, 4], [0, 1, 0, 8], [0, 0, 1, 12]])
        lb = bw.Location([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
        lc = bw.ComposedLocation([ (la, 2), (lb, 1) ])
        ld = bw.ComposedLocation([ (lb, 2), (lc, 3) ])
        with self.assertRaises(bw.ParamError):
            bw.Location([1,2,3])
        with self.assertRaises(bw.ParamError):
            bw.Location([[1], [2], [3]])
        with self.assertRaises(bw.ParamError):
            a = 1
            b = 'a'
            lb = bw.Location([[a, b, a, b], [a, b, a, b], [a, b, a, b]])

    def test_Shape(self):

        # check sub types
        with self.assertRaises(bw.ParamError):
            bw.Wire(['a', 'b'])
        v=bw.Vertex([1,2,3])
        with self.assertRaises(bw.ParamError):
            bw.Wire([v, v])


    def test_Vertex(self):
        with self.assertRaises(bw.ParamError):
            bw.Vertex(['a','b','c'])


class TestPlanarGeomeries(unittest.TestCase):


    def test_cube(self):
        # 0, 0; top, bottom
        v1=bw.Vertex((0.0, 0.0, 1.0))
        v2=bw.Vertex((0.0, 0.0, 0.0))

        v3=bw.Vertex((0.0, 1.0, 1.0))
        v4=bw.Vertex((0.0, 1.0, 0.0))

        v5=bw.Vertex((1.0, 0.0, 1.0))
        v6=bw.Vertex((1.0, 0.0, 0.0))

        # vertical edges
        e1=bw.Edge([v1,v2])
        e2=bw.Edge([v3,v4])
        e3=bw.Edge([v5,v6])

        # face v12 - v34
        # top
        e4=bw.Edge([v1,v3])
        # bottom
        e5=bw.Edge([v2,v4])
        f1 = bw.Face([e1, e4.m(), e2.m(), e5])

        # face v34 - v56
        # top
        e6=bw.Edge([v3, v5])
        # bottom
        e7=bw.Edge([v4, v6])
        f2 = bw.Face([e2, e6.m(), e3.m(), e7])

        # face v56 - v12
        # top
        e8=bw.Edge([v5, v1])
        # bottom
        e9=bw.Edge([v6, v2])
        f3 = bw.Face([e3, e8.m(), e1.m(), e9])

        # top cup
        f4 = bw.Face([e4, e6, e8])
        # bot cup
        f5 = bw.Face([e5, e7, e9])

        shell = bw.Shell([f1.m(), f2.m(), f3.m(), f4.m(), f5])
        s1=bw.Solid([ shell ])

        c1=bw.Compound([s1])

        loc1=bw.Location([[0,0,1,0],[1,0,0,0],[0,1,0,0]])
        loc2=bw.Location([[0,0,1,0],[1,0,0,0],[0,1,0,0]]) #dej tam tu druhou z prikladu
        cloc=bw.ComposedLocation([(loc1,1),(loc2,1)])

        with open("test_prism.brep", "w") as f:
            bw.write_model(f, c1, cloc)
            #bw.write_model(sys.stdout, c1, cloc)

#pridej test s vice locations

if __name__ == '__main__':
    unittest.main()