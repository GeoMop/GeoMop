import unittest
import brep_writer as bw




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
        v1=bw.Vertex((0.0, 0.0, 0.0))
        v2=bw.Vertex((0.0, 1.0, 0.0))
        v3=bw.Vertex((1.0, 0.0, 0.0))

        v4=bw.Vertex((0.0, 0.0, 1.0))
        v5=bw.Vertex((0.0, 1.0, 1.0))
        v6=bw.Vertex((1.0, 0.0, 1.0))

        e1=bw.Edge([v1,v2]) # automatic orientation of edges
        e2=bw.Edge([v2,v3])
        e3=bw.Edge([v3,v1])

        e4=bw.Edge([v4,v5])
        e5=bw.Edge([v5,v6])
        e6=bw.Edge([v6,v4])

        e7=bw.Edge([v1,v4])
        e8=bw.Edge([v2,v5])
        e9=bw.Edge([v3,v6])

        f1=bw.Face([e1, e8, e4.m(), e7.m() ])
        f2=bw.Face([e2, e9, e5.m(), e8.m() ])
        f3=bw.Face([e3, e7, e6.m(), e4.m() ])
        f4=bw.Face([e1,e2,e3])
        f5=bw.Face([e4,e5,e6])

        shell = bw.Shell([f1,f2,f3,f4,f5])
        s1=bw.Solid([ shell ])

        c1=bw.Compound([s1])

        loc1=bw.Location([[0,0,1,0],[1,0,0,0],[0,1,0,0]])
        loc2=bw.Location([[0,0,1,0],[1,0,0,0],[0,1,0,0]]) #dej tam tu druhou z prikladu
        cloc=bw.ComposedLocation([(loc1,1),(loc2,1)])

        with open("test_prism.brep", "w") as f:
            bw.write_model(f, c1, bw.Location())

#pridej test s vice locations

if __name__ == '__main__':
    unittest.main()