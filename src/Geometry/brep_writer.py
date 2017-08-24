import enum
import itertools
import numpy as np

class ParamError(Exception):
    pass

def check_matrix(mat, shape, values, idx=[]):
    '''
    Check shape and type of scalar, vector or matrix.
    :param mat: Scalar, vector, or vector of vectors (i.e. matrix). Vector may be list or other iterable.
    :param shape: List of dimensions: [] for scalar, [ n ] for vector, [n_rows, n_cols] for matrix.
    If a value in this list is None, the dimension can be arbitrary. The shape list is set fo actual dimensions
    of the matrix.
    :param values: Type or tuple of  allowed types of elements of the matrix. E.g. ( int, float )
    :param idx: Internal. Used to pass actual index in the matrix for possible error messages.
    :return:
    '''
    try:

        if len(shape) == 0:
            if not isinstance(mat, values):
                raise ParamError("Element at index {} of type {}, expected instance of {}.".format(idx, type(mat), values))
        else:

            if shape[0] is None:
                shape[0] = len(mat)
            l=None
            if not hasattr(mat, '__len__'):
                l=0
            elif len(mat) != shape[0]:
                l=len(mat)
            if not l is None:
                raise ParamError("Wrong len {} of element {}, should be  {}.".format(l, idx, shape[0]))
            for i, item in enumerate(mat):
                sub_shape = shape[1:]
                check_matrix(item, sub_shape, values, idx = [i] + idx)
                shape[1:] = sub_shape
        return shape
    except ParamError:
        raise
    except Exception as e:
        raise ParamError(e)


class Location:
    """
    Location defines an affine transformation in 3D space. Corresponds to the <location data 1> in the BREP file.
    BREP format allows to use different transformations for individual shapes.
    Location are numberd from 1. Zero index means identity location.
    """
    def __init__(self, matrix=None):
        """
        Constructor for elementary afine transformation.
        :param matrix: Transformation matrix 3x4. First three columns forms the linear transformation matrix.
        Last column is the translation vector.
        matrix==None means identity location (ID=0).
        """
        if matrix is None:
            self.matrix = None
            self.id = 0
            return

        # checks
        check_matrix(matrix, [3, 4], (int, float))
        self.matrix=matrix

    def _dfs(self, groups):
        """
        Deep first search that assign numbers to shapes
        :param groups: dict(locations=[], curves_2d=[], curves_3d=[], surfaces=[], shapes=[])
        :return: None
        """
        if not hasattr(self, 'id'):
            id=len(groups['locations'])+1
            self.id=id
            groups['locations'].append(self)

    def _brep_output(self,stream):
        stream.write("1\n")
        for row in self.matrix:
            for number in row:
                stream.write(" {}".format(number))
            stream.write("\n")

class ComposedLocation(Location):
    """
    Defines an affine transformation as a composition of othr transformations. Corresponds to the <location data 2> in the BREP file.
    BREP format allows to use different transformations for individual shapes.
    """
    def __init__(self, location_powers=[]):
        """

        :param location_powers: List of pairs (location, power)  where location is instance of Location and power is float.
        """
        locs, pows =  zip(*location_powers)
        l = len(locs)
        check_matrix(locs, [ l ], (Location, ComposedLocation) )
        check_matrix(pows, [ l ], int)

        self.location_powers=location_powers

        #for loc, pow in location_powers:
        #    stream.write(.format(loc.id, pow))

    def _dfs(self, groups):

        for location,power in self.location_powers:
            location._dfs(groups)
        Location._dfs(self, groups)

    def _brep_output(self,stream):
        stream.write("2 ")
        for loc, pow in self.location_powers:
            stream.write("{} {} ".format(loc.id, pow))
        stream.write("0\n")

def check_knots(deg, knots, N):
    total_multiplicity = 0
    for knot, mult in knots:
        # This condition must hold if we assume only (0,1) interval of curve or surface parameters.
        #assert float(knot) >= 0.0 and float(knot) <= 1.0
        total_multiplicity += mult
    assert total_multiplicity == deg + N + 1



scalar_types = (int, float, np.int64)

class Curve3D:
    """
    Defines a 3D curve as B-spline. We shall work only with B-splines of degree 2.
    Corresponds to "B-spline Curve - <3D curve record 7>" from BREP format description.
    """
    def __init__(self, poles, knots, rational=False, degree=2):
        """
        Construct a B-spline in 3d space.
        :param poles: List of poles (control points) ( X, Y, Z ) or weighted points (X,Y,Z, w). X,Y,Z,w are floats.
                      Weighted points are used only for rational B-splines (i.e. nurbs)
        :param knots: List of tuples (knot, multiplicity), where knot is float, t-parameter on the curve of the knot
                      and multiplicity is positive int. Total number of knots, i.e. sum of their multiplicities, must be
                      degree + N + 1, where N is number of poles.
        :param rational: True for rational B-spline, i.e. NURB. Use weighted poles.
        :param degree: Positive int.
        """

        if rational:
            check_matrix(poles, [None, 4], scalar_types )
        else:
            check_matrix(poles, [None, 3], scalar_types)
        N = len(poles)
        check_knots(degree, knots, N)

        self.poles=poles
        self.knots=knots
        self.rational=rational
        self.degree=degree

    def _dfs(self, groups):
        if not hasattr(self, 'id'):
            id = len(groups['curves_3d']) + 1
            self.id = id
            groups['curves_3d'].append(self)


    def _brep_output(self,stream):
        # writes b-spline curve
        stream.write("7 {} 0  {} {} {} ".format(int(self.rational), self.degree, len(self.poles), len(self.knots)))
        for pole in self.poles:
            for value in pole:
                stream.write(" {}".format(value))
            stream.write(" ")
        for knot in self.knots:
            for value in knot:
                stream.write(" {}".format(value))
            stream.write(" ")
        stream.write("\n")

class Curve2D:
    """
    Defines a 2D curve as B-spline. We shall work only with B-splines of degree 2.
    Corresponds to "B-spline Curve - <2D curve record 7>" from BREP format description.
    """
    def __init__(self, poles, knots, rational=False, degree=2):
        """
        Construct a B-spline in 2d space.
        :param poles: List of points ( X, Y ) or weighted points (X,Y, w). X,Y,w are floats.
                      Weighted points are used only for rational B-splines (i.e. nurbs)
        :param knots: List of tuples (knot, multiplicity), where knot is float, t-parameter on the curve of the knot
                      and multiplicity is positive int. Total number of knots, i.e. sum of their multiplicities, must be
                      degree + N + 1, where N is number of poles.
        :param rational: True for rational B-spline, i.e. NURB. Use weighted poles.
        :param degree: Positive int.
        """

        N = len(poles)
        if rational:
            check_matrix(poles, [N, 3], scalar_types )
        else:
            check_matrix(poles, [N, 2], scalar_types)
        check_knots(degree, knots, N)

        self.poles=poles
        self.knots=knots
        self.rational=rational
        self.degree=degree

    def _dfs(self, groups):
        if not hasattr(self, 'id'):
            id = len(groups['curves_2d']) + 1
            self.id = id
            groups['curves_2d'].append(self)

    def _brep_output(self,stream):
        # writes b-spline curve
        stream.write("7 {} 0  {} {} {} ".format(int(self.rational), self.degree, len(self.poles), len(self.knots)))
        for pole in self.poles:
            for value in pole:
                stream.write(" {}".format(value))
            stream.write(" ")
        for knot in self.knots:
            for value in knot:
                stream.write(" {}".format(value))
            stream.write(" ")
        stream.write("\n")

class Surface:
    """
    Defines a B-spline surface in 3d space. We shall work only with B-splines of degree 2.
    Corresponds to "B-spline Surface - < surface record 9 >" from BREP format description.
    """
    def __init__(self, poles, knots, rational=False, degree=(2,2)):
        """
        Construct a B-spline in 3d space.
        :param poles: Matrix (list of lists) of Nu times Nv poles (control points).
                      Single pole is a points ( X, Y, Z ) or weighted point (X,Y,Z, w). X,Y,Z,w are floats.
                      Weighted points are used only for rational B-splines (i.e. nurbs)
        :param knots: Tuple (u_knots, v_knots). Both u_knots and v_knots are lists of tuples
                      (knot, multiplicity), where knot is float, t-parameter on the curve of the knot
                      and multiplicity is positive int. For both U and V knot vector the total number of knots,
                      i.e. sum of their multiplicities, must be degree + N + 1, where N is number of poles.
        :param rational: True for rational B-spline, i.e. NURB. Use weighted poles. BREP format have two independent flags
                      for U and V parametr, but only choices 0,0 and 1,1 have sense.
        :param degree: (u_degree, v_degree) Both positive ints.
        """

        if rational:
            check_matrix(poles, [None, None, 4], scalar_types )
        else:
            check_matrix(poles, [None, None, 3], scalar_types)

        assert len(poles) > 0
        assert len(poles[0]) > 0
        self.Nu = len(poles)
        self.Nv = len(poles[0])
        for row in poles:
            assert len(row) == self.Nv

        assert (not rational and len(poles[0][0]) == 3) or (rational and len(poles[0][0]) == 4)

        (u_knots, v_knots) = knots
        check_knots(degree[0], u_knots, self.Nu)
        check_knots(degree[1], v_knots, self.Nv)

        self.poles=poles
        self.knots=knots
        self.rational=rational
        self.degree=degree

    def _dfs(self, groups):
        if not hasattr(self, 'id'):
            id = len(groups['surfaces']) + 1
            self.id = id
            groups['surfaces'].append(self)

    def _brep_output(self,stream):
        #writes b-spline surface
        stream.write("9 {} {} 0 0 ".format(int(self.rational),int(self.rational))) #prints B-spline surface u or v rational flag - both same
        for i in self.degree: #prints <B-spline surface u degree> <_>  <B-spline surface v degree>
            stream.write(" {}".format(i))
        (u_knots, v_knots) = self.knots
        stream.write(" {} {}  {} {} ".format(self.Nu, self.Nv, len(u_knots), len(v_knots)))
            #prints  <B-spline surface u pole count> <_> <B-spline surface v pole count> <_> <B-spline surface u multiplicity knot count> <_>  <B-spline surface v multiplicity knot count> <B-spline surface v multiplicity knot count>
#        stream.write(" {}".format(self.poles)) #TODO: tohle smaz, koukam na format poles a chci: B-spline surface weight poles
        for pole in self.poles: #TODO: check, takovy pokus o poles
            for vector in pole:
                for value in vector:
                    stream.write(" {}".format(value))
                stream.write(" ")
            stream.write(" ")
        for knot in u_knots: #prints B-spline surface u multiplicity knots
            for value in knot:
                stream.write(" {}".format(value))
            stream.write(" ")
        for knot in v_knots: #prints B-spline surface v multiplicity knots
            for value in knot:
                stream.write(" {}".format(value))
            stream.write(" ")
        stream.write("\n")
            
class Approx:
    """
    Approximation methods for B/splines of degree 2.
    
    """
    @classmethod
    def plane(cls, vtxs):
        """
        Returns B-spline surface of a plane given by 3 points.
        We retun also list of UV coordinates of the given points.
        :param vtxs: List of tuples (X,Y,Z)
        :return: ( Surface, vtxs_uv )
        """
        assert len(vtxs) == 3, "n vtx: {}".format(len(vtxs))
        vtxs.append( (0,0,0) )
        vtxs = np.array(vtxs)
        vtxs[3] = vtxs[1] + vtxs[2] - vtxs[0]
        (surf, vtxs_uv) = cls.bilinear(vtxs)
        return (surf, vtxs_uv[0:3])

    @classmethod
    def bilinear(cls, vtxs):
        """
        Returns B-spline surface of a bilinear surface given by 4 corner points.
        We retun also list of UV coordinates of the given points.
        :param vtxs: List of tuples (X,Y,Z)
        :return: ( Surface, vtxs_uv )
        """
        assert len(vtxs) == 4, "n vtx: {}".format(len(vtxs))
        vtxs = np.array(vtxs)
        def mid(*idx):
            return np.mean( vtxs[list(idx)], axis=0)

        poles = [ [vtxs[0],  mid(0, 1), vtxs[1]],
                  [mid(0,2), mid(0,1,2,3), mid(1,3)],
                  [vtxs[2], mid(2,3), vtxs[3]]
                  ]
        knots = [(0.0, 3), (1.0, 3)]
        surface = Surface(poles, (knots, knots))
        vtxs_uv = [ (0, 0), (1, 0), (0, 1), (1,1) ]
        return (surface, vtxs_uv)




    @classmethod
    def _line(cls, vtxs):
        '''
        :param vtxs: List of tuples (X,Y) or (X,Y,Z)
        :return:
        '''
        assert len(vtxs) == 2
        vtxs = np.array(vtxs)
        mid = np.mean(vtxs, axis=0)
        poles = [ vtxs[0],  mid, vtxs[1] ]
        knots = [(0.0, 3), (1.0, 3)]
        return (poles, knots)

    @classmethod
    def line_2d(cls, vtxs):
        """
        Return B-spline approximation of line from two 2d points
        :param vtxs: [ (X0, Y0), (X1, Y1) ]
        :return: Curve2D
        """
        return Curve2D( *cls._line(vtxs) )

    @classmethod
    def line_3d(cls,  vtxs):
        """
        Return B-spline approximation of line from two 3d points
        :param vtxs: [ (X0, Y0, Z0), (X1, Y1, Z0) ]
        :return: Curve2D
        """
        return Curve3D(*cls._line(vtxs))

orient_chars=['+', '-', 'i', 'e']

class Orient(enum.IntEnum):
    Forward=1
    Reversed=2
    Internal=3
    External=4

op=Orient.Forward
om=Orient.Reversed
oi=Orient.Internal
oe=Orient.External

class ShapeRef:
    """
    Auxiliary data class to store an object with its orientation
    and possibly location. Meaning of location in this context is not clear yet.
    Identity location (0) in all BREPs produced by OCC.
    All methods accept the tuple (shape, orient, location) and
    construct the ShapeRef object automatically.
    """
    def __init__(self, shape, orient=Orient.Forward, location=Location()):
        """
        :param shape: referenced shape
        :param orient: orientation of the shape, value is enum Orient
        :param location: A Location object. Default is None = identity location.
        """
        assert issubclass(type(shape), Shape)
        assert isinstance(orient, Orient)
        assert issubclass(type(location), Location)

        self.shape=shape
        self.orient=orient
        self.location=location

class ShapeFlag:
    """
    Auxiliary data class representing the shape flag word of BREP shapes.
    All methods set the flags automatically, but it can be overwritten.
    """
    def __init__(self, free, modified, IGNORED, orientable, closed, infinite, convex):

        self.flags = (free, modified, IGNORED, orientable, closed, infinite, convex)
        for i in self.flags:
            assert i in [0, 1]


class Shape:
    def __init__(self, childs):
        """
        Construct base Shape object.
        :param childs: List of tuples (shape, orient) or (shape, orient, location)
         to construct ShapeRef objects.
        """

        # convert list of shape reference tuples to ShapeRef objects
        # automaticaly wrap naked shapes into tuple.
        self.childs=[]
        for child in childs:
            if type(child) == tuple:
                args=child
            else:
                args=(child,)
            if not isinstance(args[0], tuple(self.sub_types)):
                raise ParamError("{} is not instance of {}".format(type(args[0]), self.sub_types) )
            self.childs.append(ShapeRef(*args))

        # Thes flags are produced by OCC for all other shapes safe vertices.
        self.flags=ShapeFlag(0,1,0,1,0,0,0)
        #shpname: Shape name, defined in childs
        self.shpname=None

    """
    Methods to simplify ceration of oriented references.
    """
    def p(self):
        return (self, Orient.Forward)

    def m(self):
        return (self, Orient.Reversed)

    def i(self):
        return (self, Orient.Internal)

    def e(self):
        return (self, Orient.External)

    def subshapes(self):
        # Return list of subshapes stored in child ShapeRefs.
        return [chld.shape for chld in self.childs]


    def append(self, shape_ref):
        """
        Append a reference to shild
        :param shape_ref: Either ShapeRef object or tuple passed to its constructor.
        :return: None
        """
        if type(shape_ref) != ShapeRef:
            shape_ref=ShapeRef(*shape_ref)
        self.childs.append(shape_ref)

    def set_flags(self, flags):
        """
        Set flags given as tuple.
        :param flags: Tuple of 8 flags.
        :return:
        """
        self.flags = ShapeFlag(*flags)

    def _dfs(self, groups):
        """
        Deep first search that assign numbers to shapes
        :param groups: dict(locations=[], curves_2d=[], curves_3d=[], surfaces=[], shapes=[])
        :return: None
        """
        if hasattr(self, 'id'):
            return
        id=len(groups['shapes'])+1
        self.id=id
        groups['shapes'].append(self)
        for sub_ref in self.childs:
            sub_ref.location._dfs(groups)
            sub_ref.shape._dfs(groups)

    def _brep_output(self, stream):
        stream.write("{}\n".format(self.shpname))

"""
Shapes with no special parameters, only flags and subshapes.
Writer can be generic implemented in bas class Shape.
"""

class Compound(Shape):
    def __init__(self, shapes=[]):
        self.sub_types =  [CompoundSolid, Solid, Shell, Wire, Face, Edge, Vertex]
        super().__init__(shapes)
        self.shpname = 'Co'

class CompoundSolid(Shape):
    def __init__(self, solids=[]):
        self.sub_types = [Solid]
        super().__init__(solids)
        self.shpname = 'CS'

class Solid(Shape):
    def __init__(self, shells=[]):
        self.sub_types = [Shell]
        super().__init__(shells)
        self.shpname='So'

class Shell(Shape):
    def __init__(self, faces=[]):
        self.sub_types = [Face]
        super().__init__(faces)
        self.shpname='Sh'


class Wire(Shape):
    def __init__(self, edges=[]):
        self.sub_types = [Edge]
        super().__init__(edges)
        self.shpname='Wi'

"""
Shapes with special parameters.
Specific writers are necessary.
"""

class Face(Shape):
    """
    Face class.
    Like vertex and edge have some additional parameters in the BREP format.
    """

    def __init__(self, wires, surface=None, location=Location(), tolerance=0.0):
        """
        :param wires: List of wires, or list of edges, or list of ShapeRef tuples of Edges to construct a Wire.
        :param surface: Representation of the face, surface on which face lies.
        :param location: Location of the surface.
        :param tolerance: Tolerance of the representation.
        """
        assert(len(wires) > 0)
        # auto convert list of edges into wire
        if type(wires[0]) == Edge:
            wires = [ Wire(wires) ]
        elif type(wires[0]) == tuple:
            assert type(wires[0][0]) == Edge
            wires = [ Wire(wires) ]

        # check that wires are closed
        for wire in wires:
            if not self.is_closed_wire(wire):
                raise Exception("Trying to make face from non-closed wire.")
        self.sub_types = [Wire]
        super().__init__(wires)
        if surface is None:
            self.repr=[]
        else:
            self.repr=[(surface, location)]
        self.tol=tolerance
        self.restriction_flag =0
        self.shpname = 'Fa'

    def is_closed_wire(self, wire):
        vtx_set = {}
        for edge in wire.subshapes():
            for vtx in edge.subshapes():
                vtx_set[vtx] = 0
                vtx.n_edges += 1
        closed =  True
        for vtx in vtx_set.keys():
            if vtx.n_edges % 2 != 0:
                closed = False
            vtx.n_edges = 0
        return closed


    def _dfs(self, groups):
        Shape._dfs(self,groups)
        if not self.repr:
            self.implicit_surface()
        assert len(self.repr) == 1
        for repr, loc in self.repr:
            repr._dfs(groups)
            loc._dfs(groups)

        # update geometry representation of edges (add 2D curves)
        for edge in self.subshapes():
            edge._dfs(groups)

            
    def implicit_surface(self):
        """
        Construct a surface if surface is None. Works only for
        3 and 4 vertices (plane or bilinear surface)
        Should be called in _dfs just after all child shapes are passed.
        :return: None
        """
        edges = {}
        vtxs = {}
        for wire in self.subshapes():
            for edge in wire.subshapes():
                edges[edge.id] =  edge
                for vtx in edge.subshapes():
                    vtxs[vtx.id] = vtx.point
        if len(vtxs) == 3:
            constructor = Approx.plane
        elif len(vtxs) == 4:
            constructor = Approx.bilinear
        else:
            raise Exception("Too many vertices {} for implicit surface construction.".format(len(vtxs)))
        (ids, points) = zip(*vtxs.items())
        (surface, vtxs_uv) =  constructor(list(points))
        self.repr = [(surface, Location())]

        # set representation of edges
        assert len(ids) == len(vtxs_uv)
        id_to_uv = dict(zip(ids, vtxs_uv))
        for edge in edges.values():
            e_vtxs = edge.subshapes()
            v0_uv = id_to_uv[e_vtxs[0].id]
            v1_uv = id_to_uv[e_vtxs[1].id]
            edge.attach_to_plane( surface, v0_uv, v1_uv )

        # TODO: Possibly more general attachment of edges to @D curves for general surfaces, but it depends
        # on organisation of intersection curves.

class Edge(Shape):
    """
    Edge class. Special edge flags have unclear meaning.
    Allow setting representations of the edge, this is crucial for good mash generation.
    """

    class Repr(enum.IntEnum):
        Curve3d = 1
        Curve2d = 2
        #Continuous2d=3


    def __init__(self, vertices, tolerance=0.0):
        """
        :param vertices: List of shape reference tuples, see ShapeRef class.
        :param tolerance: Tolerance of the representation.
        """
        assert(len(vertices) == 2)

        # automaticaly convert vertices to their ShapeRefs
        if type(vertices[0]) == Vertex:
            vertices[0]=(vertices[0], Orient.Forward)
        if type(vertices[1]) == Vertex:
            vertices[1]=(vertices[1], Orient.Reversed)

        assert vertices[0]

        self.sub_types = [Vertex]
        super().__init__(vertices)
        self.tol = tolerance
        self.repr = []
        self.edge_flags=(1,1,0)
        self.shpname = 'Ed'

    def set_edge_flags(self, same_parameter, same_range, degenerated):
        self.edge_flags=(same_parameter,same_range, degenerated)

    def points(self):
        '''
        :return: List of coordinates of the edge vertices.
        '''
        return [ vtx.point for vtx in self.subshapes()]

    def attach_to_3d_curve(self, t_range, curve, location=Location()):
        """
        Add vertex representation on a 3D curve.
        :param t_range: Tuple (t_min, t_max).
        :param curve: 3D curve object (Curve3d)
        :param location: Location object. Default is None = identity location.
        :return: None
        """
        self.repr.append( (self.Repr.Curve3d, t_range, curve, location) )

    def attach_to_2d_curve(self, t_range, curve, surface, location=Location()):
        """
        Add vertex representation on a 2D curve.
        :param t_range: Tuple (t_min, t_max).
        :param curve: 2D curve object (Curve2d)
        :param surface: Surface on which the curve lies.
        :param location: Location object. Default is None = identity location.
        :return: None
        """
        self.repr.append( (self.Repr.Curve2d, t_range, curve, surface, location) )

    def attach_to_plane(self, surface, v0, v1):
        """
        Construct and attach 2D line in UV space of the 'surface'
        :param surface: A Surface object.
        :param v0: UV coordinate of the first edge point
        :param v1: UV coordinate of the second edge point
        :return:
        """

        self.attach_to_2d_curve((0.0, 1.0), Approx.line_2d([v0, v1]), surface)

    def implicit_curve(self):
        """
        Construct a line 3d curve if there is no 3D representation.
        Should be called in _dfs.
        :return:
        """
        vtx_points = self.points()
        self.attach_to_3d_curve((0.0,1.0), Approx.line_3d( vtx_points ))


    #def attach_continuity(self):

    def _dfs(self, groups):
        Shape._dfs(self,groups)
        if not self.repr:
            self.implicit_curve()
        assert len(self.repr) > 0
        for repr in self.repr:
            if repr[0]==self.Repr.Curve2d:
                repr[2]._dfs(groups) #curve
                repr[3]._dfs(groups) #surface
                repr[4]._dfs(groups) #location
            elif repr[0]==self.Repr.Curve3d:
                repr[2]._dfs(groups) #curve
                repr[3]._dfs(groups) #location


class Vertex(Shape):
    """
    Vertex class.
    Allow setting representations of the vertex but seems it is not used in BREPs produced by OCC.
    """

    class Repr(enum.IntEnum):
        Curve3d = 1
        Curve2d = 2
        Surface = 3

    def __init__(self, point, tolerance=0.0):
        """
        :param point: 3d point (X,Y,Z)
        :param tolerance: Tolerance of the representation.
        """
        check_matrix(point, [3], (int, float))

        super().__init__(childs=[])
        # These flags are produced by OCC for vertices.
        self.flags = ShapeFlag(0, 1, 0, 1, 1, 0, 1)
        # Coordinates in the 3D space. [X, Y, Z]
        self.point=point
        # tolerance of representations.
        self.tolerance=tolerance
        # List of geometrical representations of the vertex. Possibly not necessary for meshing.
        self.repr=[]
        # Number of edges in which vertex is used. Used internally to check closed wires.
        self.n_edges = 0
        self.shpname = 'Ve'

    def attach_to_3d_curve(self, t, curve, location=Location()):
        """
        Add vertex representation on a 3D curve.
        :param t: Parameter of the point on the curve.
        :param curve: 3D curve object (Curve3d)
        :param location: Location object. Default is None = identity location.
        :return: None
        """
        self.repr.append( (self.Repr.Curve3d, t, curve, location) )

    def attach_to_2d_curve(self, t, curve, surface, location=Location()):
        """
        Add vertex representation on a 2D curve on a surface.
        :param t: Parameter of the point on the curve.
        :param curve: 2D curve object (Curve2d)
        :param surface: Surface on which the curve lies.
        :param location: Location object. Default is None = identity location.
        :return: None
        """
        self.repr.append( (self.Repr.Curve2d, t, curve, surface, location) )

    def attach_to_surface(self, u, v, surface, location=Location()):
        """
        Add vertex representation on a 3D curve.
        :param u,v: Parameters u,v  of the point on the surface.
        :param surface: Surface object.
        :param location: Location object. Default is None = identity location.
        :return: None
        """
        self.repr.append( (self.Repr.Surface, u,v, surface, location) )

    def _dfs(self, groups):
        Shape._dfs(self,groups)
        for repr in self.repr:
            if repr[0]==self.Repr.Curve2d:
                repr[2]._dfs(groups) #curve
                repr[3]._dfs(groups) #surface
                repr[4]._dfs(groups) #location
            elif repr[0]==self.Repr.Curve3d:
                repr[2]._dfs(groups) #curve
                repr[3]._dfs(groups) #location


def index_all(compound,location):
    print("Index")
    print(compound.__class__.__name__) #prints class name

    groups=dict(locations=[], curves_2d=[], curves_3d=[], surfaces=[], shapes=[])
    compound._dfs(groups)#pridej jako parametr dictionary listu jednotlivych grup. v listech primo objekty
    location._dfs(groups)
    print(groups)
    return groups


def write_model(stream, compound, location):

    groups = index_all(compound=compound,location=location)

    stream.write("DBRep_DrawableShape\n")
    stream.write("CASCADE Topology V1, (c) Matra-Datavision\n")
    stream.write("Locations {}\n".format(len(groups['locations'])))
    for loc in groups['locations']:
        loc._brep_output(stream)

    stream.write("Curves {}\n".format(len(groups['curves_3d'])))
    for curve in groups['curves_3d']:
        curve._brep_output(stream)

    stream.write("Curve2ds {}\n".format(len(groups['curves_2d'])))
    for curve in groups['curves_2d']:
        curve._brep_output(stream)

    stream.write("Surfaces {}\n".format(len(groups['surfaces'])))
    for surface in groups['surfaces']:
        surface._brep_output(stream)

    for shape in groups['shapes']: #pridej .reverse a zkontroluj, jestli je to metoda reverse nebo funkce reversed
        shape._brep_output(stream)

    #vygeneruje hlavicku... stream write
    # vytvori hlavicku pro locations
    # for all locations (for loc in groups['locations']:
    #   loc._brep_output(stream) -> tuhle metodu implemntuj v tride pro loc, at si to genetuje sama
    #pak for cyklus pro  to same pro curves_2d, curves 3d atd.
    #pro shapes je potreba zapisovat pozpatku (protoze nejdriv mam naindexovane nejvyssi shapy)

    """
    Write the counpound into the stream.
    :param stream: Output stream.
    :param compound: Compoud to output together with all subshapes, curves, surfaces and locations.
    :param location: Global location of the model.
    :return: None

    Algorithm:
    0. Compound is formed by various objects groups (Locations, 3d curves, 2d curves, surfaces, shapes)
    linked together by references. This forms an directed acyclic graph (DAG).
    1. Perform deep first search of the compound, assign unique numbers to all objects within its group,
       counting from 1. Good way to do this is to implement simple dfs method in Shape class and override it
       in Face, Edge, Vertex to include include references to their representations. DFS should also
       fill lists of individual groups passed through in a dictionary.
    2. Write down individual groups, shapes in reversed order.
    """
    pass


