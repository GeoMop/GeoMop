"""
TODO:
- check how GMSH number surfaces standing alone,
  seems that it number object per dimension by the IN time in DFS from solids down to Vtx,
  just ignoring main compound, not sure how numbering works for free standing surfaces.

"""
import os
import sys

geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
#intersections_src = os.path.join(os.path.dirname(os.path.realpath(__file__)), "intersections","src")
sys.path.append(geomop_src)
#sys.path.append(intersections_src)

import json_data as js
import geometry_files.geometry_structures as gs
import gmsh_io
import numpy as np
import numpy.linalg as la
import math

import b_spline
import bspline as bs
import bspline_approx as bs_approx
#import bspline_plot as bs_plot
import brep_writer as bw


###
#netgen_install_prefix="/home/jb/local/"
#netgen_path = "opt/netgen/lib/python3/dist-packages"
#sys.path.append( netgen_install_prefix + netgen_path )

#import netgen.csg as ngcsg
#import netgen.meshing as ngmesh



def check_point_tol(A, B, tol):
    diff = B - A
    norm = la.norm(diff)
    if norm > tol:
        raise Exception("Points too far: {} - {} = {}, norm: {}".format(A,B,diff, norm))




class ShapeInfo:
    #count_by_dim = [0,0,0,0]
    """
    Class to capture information about individual shapes finally meshed by GMSH as independent objects.
    """

    _shapes_dim ={'Vertex':0, 'Edge':1, 'Face':2, 'Solid':3}

    def __init__(self, shape, i_reg=None, top=None, bot=None):
        self.shape = shape
        #self.dim = shapes_dim.get(type(shape).__name__)
        #assert self.dim is not None

        #self.dim_spec_id = self.count_by_dim[dim]
        #self.count_by_dim += 1

        if i_reg is None:
            self.free = False
        else:
            self.i_reg = i_reg
            self.top_iface = top
            self.bot_iface = bot
            self.free = True

    def set(self, i_reg, top, bot):
        assert not self.free
        self.i_reg = i_reg
        self.top_iface = top
        self.bot_iface = bot
        self.free = True

    def dim(self):
        return self._shapes_dim.get(type(self.shape).__name__, None)

    def vert_curve(self, v_to_z):
        z_min, z_max = v_to_z
        poles_uv = self.curve_z.poles.copy()
        poles_uv[:, 1] -= z_min
        poles_uv[:, 1] /= (z_max - z_min)
        return bs.Curve(self.curve_z.basis, poles_uv)

class Curve(gs.Curve):
    pass


class SurfaceApproximation(gs.SurfaceApproximation):
    """
    TODO: allow user to determine configuration of the approximation
    """
    pass


class Surface(gs.Surface):
    """
    Represents a z(x,y) function surface given by grid of points, but optionaly approximated by a B-spline surface.
    """

    def set_file(self, geom_file_base):

        # allow relative position to the main layers.json file
        if self.grid_file:
            self.is_bumpy = True
            if self.grid_file[0] == '.':
                self.grid_file = os.path.join(os.path.dirname(geom_file_base), self.grid_file)
        else:
            self.is_bumpy = False


    def make_bumpy_surface(self):
        # load grid surface and make its approximation

        self.grid_surf = bs.GridSurface.load(self.grid_file)
        self.approx_surf = bs_approx.surface_from_grid(self.grid_surf, (16, 16))
        self.mat_xy = mat_xy = np.array(self.transform_xy)
        mat_z = np.array(self.transform_z)
        self.approx_surf.transform(mat_xy, mat_z)
        self.bw_surface = bw.surface_from_bs(self.approx_surf.make_full_surface())


    def make_flat_surface(self, xy_aabb):
        # flat surface
        corners = np.zeros( (3, 3) )
        corners[[1, 0], 0] = xy_aabb[0][0]  # min X
        corners[2, 0] = xy_aabb[1][0]  # max X
        corners[[1, 2], 1] = xy_aabb[0][1]  # min Y
        corners[0, 1] = xy_aabb[1][1]  # max Y
        corners[:,2] = self.depth

        basis = bs.SplineBasis.make_equidistant(2, 1)
        z_const = - self.depth
        poles = np.ones( (3, 3, 1 ) ) * z_const
        surf_z = bs.Surface( (basis, basis), poles)
        self.grid_surf = bs.Z_Surface(corners[:, 0:2], surf_z)
        self.approx_surf = self.grid_surf
        self.bw_surface = bw.surface_from_bs(self.approx_surf.make_full_surface())


    def plot_nodes(self, nodes):
        """
        Plot nodes with the surface boundary.
        :param nodes: array Nx2 of XY points
        """

        # plot nodes
        x_nodes = np.array(nodes)[:, 0]
        y_nodes = np.array(nodes)[:, 1]
        plt.plot(x_nodes, y_nodes, 'bo')

        # plot boundary
        vtx = np.array([[0, 1], [0, 0], [1, 0], [1, 1], [0, 1]])
        xy = self.grid_surf.uv_to_xy(vtx)

        # variants of the same (for debugging)
        # xy = self.approx_surf.uv_to_xy(vtx)
        # Just for bump surface:
        # xy = np.array([ self.mat_xy[0:2, 0:2].dot(v) + self.mat_xy[:,2] for v in xy_vtx ])
        # xy = self.grid_surf.quad

        plt.plot(xy[:, 0], xy[:, 1], color='green')
        plt.show()


    def check_nodes(self, nodes):
        """
        :param nodes:
        :return:
        """
        if self.is_bumpy:
            self.make_bumpy_surface()
            uv_nodes = self.approx_surf.xy_to_uv(np.array(nodes))
            for i, uv in enumerate(uv_nodes):
                if not ( 0.0 < uv[0] < 1.0 and 0.0 < uv[1] < 1.0 ):
                    raise IndexError("Node {}: {} is out of surface domain, uv: {}".format(i, nodes[i], uv))
        else:
            nod = np.array(nodes)
            nod_aabb = (np.amin(nod, axis=0), np.amax(nod, axis=0))
            self.make_flat_surface(nod_aabb)
            # self.plot_nodes(nodes)


    def approx_eval_z(self, x, y):
        return self.approx_surf.z_eval_xy_array(np.array([[x, y]]))[0]


    def eval_z(self, x, y):
        return self.grid_surf.eval_in_xy(np.array([ [x,y] ]).T)[0]


    @staticmethod
    def interpol(a, b, t):
        return (t * b + (1-t) * a)

    def line_intersect(self, a, b):
        # TODO:
        z = self.depth
        t = (a[2] - z) / (a[2] - b[2])
        # (1-t) = (z - bz) / (az - bz)
        x = self.interpol(a[0], b[0], t )
        y = self.interpol(a[1], b[1], t )
        return (x, y, z)


    def add_curve_to_edge(self, edge):
        axyz, bxyz = edge.points()

        n_points = 16
        x_points = np.linspace(axyz[0], bxyz[0], n_points)
        y_points = np.linspace(axyz[1], bxyz[1], n_points)
        xy_points = np.stack( (x_points, y_points), axis =1)
        xyz_points = self.approx_surf.eval_xy_array(xy_points)
        curve_xyz = bs_approx.curve_from_grid(xyz_points)
        start, end = curve_xyz.eval_array(np.array([0, 1]))
        check_point_tol( start, axyz, 1e-3)
        check_point_tol( end, bxyz, 1e-3)
        edge.attach_to_3d_curve((0.0, 1.0), bw.curve_from_bs(curve_xyz))

        # TODO: make simple line approximation
        xy_points = np.array([ axyz[0:2], bxyz[0:2]])
        uv_points = self.approx_surf.xy_to_uv(xy_points)
        curve_uv = bs_approx.line( uv_points )
        start, end = self.approx_surf.eval_array(curve_uv.eval_array(np.array([0, 1])))
        check_point_tol( start, axyz, 1e-3)
        check_point_tol( end, bxyz, 1e-3)
        edge.attach_to_2d_curve((0.0, 1.0), bw.curve_from_bs(curve_uv), self.bw_surface)

        # vertical curve
        poles_tz = curve_xyz.poles[:, 1:3].copy()
        # overhang = 0.1
        # scale = (1 - 2*overhang) / (bxyz[1] - axyz[1])
        # poles_tz[:, 0] -= axyz[1]
        # poles_tz[:, 0] *= scale
        # poles_tz[:, 0] += overhang


        poles_tz[:, 0] -= axyz[1]
        poles_tz[:, 0] /= (bxyz[1] - axyz[1])



        return bs.Curve(curve_xyz.basis, poles_tz)




class Segment(gs.Segment):
    pass

class Polygon(gs.Polygon):
    pass

class Topology(gs.Topology):
    """
    TODO:
    - support for polygons with holes, here and in creation of faces and solids
    """
    def check(self, nodeset):
        """
        Check that topology is compatible with given nodeset.
        Check and possibly fix orientation of polygons during first call.
        :param nodeset:
        :return:
        """
        if hasattr(self, 'n_nodes'):
            # already checked with other nodeset, just check nodeset size
            assert len(nodeset.nodes) == self.n_nodes, \
                "Nodeset (id: {}) size {} is not compatible with topology (id: {}) with size {}"\
                .format(nodeset.id, len(nodeset.nodes), self.id, self.n_nodes)
            return

        nodes = nodeset.nodes
        self.n_nodes = len(nodes)
        self.n_segments = len(self.segments)
        for segment in self.segments:
            for nid in segment.node_ids:
                assert 0 <= nid < len(nodes), "Node ID: {} of topology (id: {}) is out of nodeset (id: {}".format(nid, self.id, nodeset.id)

        for poly in self.polygons:
            self.orient_polygon(poly)


    def orient_polygon(self, poly):
        """
        Find orientation of polygon segments so that they have same orientation within the polygon.
        TODO: Make orientation counter clock wise.
        :param poly:
        :return:
        """
        last_node = None
        first_node = poly.segment_ids
        oriented_ids = []
        segs = poly.segment_ids
        for i_seg, i_seg_next in zip(segs, segs[1:] + segs[:1]):
            segment = self.segments[i_seg]
            next_segment = self.segments[i_seg_next]
            nodes = segment.node_ids
            if nodes[1] in next_segment.node_ids:
                oriented_ids.append( self.code_oriented_segment(i_seg, False) )
            else:
                assert nodes[0] in next_segment.node_ids, "Wrong order of polygon edges."
                oriented_ids.append(self.code_oriented_segment(i_seg, True))
        poly.segment_ids = oriented_ids


    def code_oriented_segment(self, id_seg, reversed):
        """
        Coded segment id with orientation.
        :param id_seg:
        :param reversed:
        :return:
        """
        return id_seg + reversed*self.n_segments


    def orient_segment(self, id_seg):
        """
        Decode segment_id withi polygon to the true segment ID end orientation.
        :param id_seg:
        :return:
        """
        if id_seg >= len(self.segments):
            return id_seg - self.n_segments, True
        else:
            return id_seg, False

class NodeSet(gs.NodeSet):
    pass


class Interface:
    def __init__(self, surface, nodes, topology):
        self.surface = surface
        self.topology = topology
        self.surface.check_nodes(nodes)
        if nodes is not None:
            self.nodes = [ (X[0], X[1], self.surface.approx_eval_z(X[0], X[1])) for X in nodes]
        self.make_shapes()


    def make_shapes(self):


        self.vertices = [ ShapeInfo(bw.Vertex(node)) for node in self.nodes]

        self.edges = []
        for segment in self.topology.segments:
            #nodes_id, surface_id = segment
            na, nb = segment.node_ids
            edge = bw.Edge( [self.vertices[na].shape, self.vertices[nb].shape] )
            curve_z = self.surface.add_curve_to_edge(edge)
            si = ShapeInfo(edge)
            si.curve_z = curve_z
            self.edges.append( si )

        self.faces = []
        n_segments = len(self.topology.segments)
        for poly in self.topology.polygons:
            #segment_ids, surface_id = poly      # segment_id > n_segments .. reversed edge
            edges = []
            for id_seg in poly.segment_ids:
                i_seg, reversed = self.topology.orient_segment(id_seg)
                edge = self.edges[i_seg].shape
                if reversed:
                    edges.append(edge.m())
                else:
                    edges.append(edge)
            wire = bw.Wire(edges)
            face = bw.Face([wire], surface = self.surface.bw_surface)
            self.faces.append( ShapeInfo(face) )


    def interpolate_interface(self, a_surface, a_nodes, b_surface, b_nodes):
        assert len(a_nodes) == len(b_nodes)
        self.nodes=[]
        for (ax, ay), (bx, by) in zip(a_nodes, b_nodes):
            az = a_surface.depth
            bz = b_surface.depth
            line = ( (ax, ay, az), (bx,by,bz) )
            x,y,z = self.surface.line_intersect( *line )
            self.nodes.append( (x,y,z) )

    def iter_shapes(self):
        for s_list in [ self.vertices, self.edges, self.faces ]:
            for shp in s_list:
                yield shp

class SurfaceNodeSet(gs.SurfaceNodeSet):

    def init(self, lg):
        self.surface = lg.surfaces[self.surface_id]
        self.nodeset = lg.node_sets[self.nodeset_id]
        self.topology = lg.topologies[self.nodeset.topology_id]
        self.topology.check(self.nodeset)

    def make_interface(self, lg ):
        if lg.interfaces[self.surface_id] is not None:
            return lg.interfaces[self.surface_id]

        self.init(lg)
        iface = Interface(self.surface, self.nodeset.nodes, self.topology)

        lg.interfaces[self.surface_id] = iface
        return iface

class InterpolatedNodeSet(gs.InterpolatedNodeSet):

    def make_interface(self, lg):
        if lg.interfaces[self.surface_id] is not None:
            return lg.interfaces[self.surface_id]

        surface = lg.surfaces[self.surface_id]
        a, b = self.surf_nodesets
        a.init(lg)
        b.init(lg)
        assert a.topology.id == b.topology.id
        topology = a.topology
        if a.nodeset_id == b.nodeset_id:
            iface = Interface(surface, a.nodeset.nodes, topology)
        else:
            assert a.surface_id != b.surface_id
            iface = Interface(surface, None, topology)
            iface.interpolate_interface(a.surface, a.nodeset.nodes, b.surface, b.nodeset.nodes)

        lg.interfaces[self.surface_id] = iface
        return iface


class Region(gs.Region):

    def init(self, topo_dim, extrude):
        assert topo_dim == self.topo_dim, "Region ('{}') topology dimension ({})  do not match layer dimension ({}).".format( self.name, self.topo_dim, topo_dim)
        if self.not_used:
            return
        if hasattr(self, 'dim'):
            assert self.dim == topo_dim + extrude, "dim: %d tdim: %d ext: %d"%(self.dim, topo_dim, extrude)
        else:
            self.dim = topo_dim + extrude

        # fix names of boundary regions
        if self.boundary:
            if self.name[0] != '.':
                self.name = '.' + self.name
        else:
            while len(self.name) > 0 and self.name[0] == '.':
                self.name = self.name[1:]
            assert len(self.name) > 0, "Empty name of region after removing leading dots."
                

    def is_active(self, dim):
        active = not self.not_used
        if active:
            assert dim == self.dim, "Can not create shape of dim: {} in region '{}' of dim: {}.".format(dim, self.name, self.dim)
        return active

#class GeoLayer(gs.GeoLayer):
#    pass

class FractureLayer(gs.FractureLayer):
    def init(self, lg):
        self.i_top = self.top.make_interface(lg)
        self.topology = self.i_top.topology
        self.regions = lg.regions
        for dim, reg_list in enumerate([self.node_region_ids, self.segment_region_ids, self.polygon_region_ids]):
            for i_reg in reg_list:
                self.regions[i_reg].init(topo_dim=dim, extrude = False)

    def make_shapes(self):
        """
        Make shapes in main
        :return:
        """

        # no point regions
        #for i, i_reg in enumerate(self.node_region_ids):
        #    if self.regions[i_reg].is_active(0):
        #        shapes.append( (self.i_top.vertices[i], i_reg) )

        for i, i_reg in enumerate(self.segment_region_ids):
            if self.regions[i_reg].is_active(1):
                self.i_top.edges[i].set(i_reg, self.i_top, self.i_top)

        for i, i_reg in enumerate(self.polygon_region_ids):
            if self.regions[i_reg].is_active(2):
                self.i_top.faces[i].set(i_reg, self.i_top, self.i_top)

        return []

class StratumLayer(gs.StratumLayer):
    def init(self, lg):
        self.i_top = self.top.make_interface(lg)
        self.i_bot = self.bottom.make_interface(lg)
        assert self.i_top.topology.id == self.i_bot.topology.id
        self.topology = self.i_top.topology
        self.regions = lg.regions
        for tdim, reg_list in enumerate([self.node_region_ids, self.segment_region_ids, self.polygon_region_ids]):
            for i_reg in reg_list:
                self.regions[i_reg].init(topo_dim=tdim, extrude = True)

    def plot_vert_face(self, v_to_z, si_top, si_bot):
        top_curve = si_top.vert_curve(v_to_z)
        bot_curve = si_bot.vert_curve(v_to_z)
        bs_plot.plot_curve_2d(top_curve, poles=True)
        bs_plot.plot_curve_2d(bot_curve, poles=True)
        plt.show()



    def make_vert_bw_surface(self, si_top, si_bot, edge_start, edge_end):
        top_box = si_top.curve_z.aabb()
        bot_box = si_bot.curve_z.aabb()
        top_z = top_box[1][1] # max
        bot_z = bot_box[0][1] # min

        # XYZ of corners, vUV, U is horizontal start to end, V is vartical bot to top
        v00, v10 = np.array(si_bot.shape.points()).copy()
        v01, v11 = np.array(si_top.shape.points()).copy()
        v00[2] = v10[2] = bot_z
        v11[2] = v01[2] = top_z

        # allow just vertical extrusion, same XY on bot and top
        assert la.norm(v00[0:2] - v01[0:2]) < 1e-10
        assert la.norm(v10[0:2] - v11[0:2]) < 1e-10
        surf = bs_approx.plane_surface([v00, v10, v01], overhang=0.0)
        bw_surf = bw.surface_from_bs(surf)

        v_to_z = [bot_z, top_z]
        #self.plot_vert_face(v_to_z, si_top, si_bot)

        top_curve = si_top.vert_curve(v_to_z)
        uv_v_top = top_curve.eval_array(np.array([0, 1]))
        assert np.all( 0 < uv_v_top ) and np.all( uv_v_top < 1), \
            "Top surface under bottom surface for layer id = {}.".format(self.id)
        xyz_v_top = surf.eval_array(uv_v_top)

        bot_curve = si_bot.vert_curve(v_to_z)
        uv_v_bot = bot_curve.eval_array(np.array([0, 1]))
        assert np.all( 0 < uv_v_bot) and np.all(uv_v_bot < 1), \
            "Top surface under bottom surface for layer id = {}.".format(self.id)
        xyz_v_bot = surf.eval_array(uv_v_bot)

        # check precision of corners
        v00, v10 = si_bot.shape.points()
        v01, v11 = si_top.shape.points()
        for new, orig in zip( list(xyz_v_bot) + list(xyz_v_top), [v00, v10, v01, v11]):
            check_point_tol(new, orig, 1e-3)

        # attach 2D curves to horizontal edges
        si_top.shape.attach_to_2d_curve((0.0, 1.0), bw.curve_from_bs(top_curve), bw_surf )
        si_bot.shape.attach_to_2d_curve((0.0, 1.0), bw.curve_from_bs(bot_curve), bw_surf )

        # attach 2D and 3D curves to vertical edges
        curve = bs_approx.line( [v00, v01] )
        edge_start.attach_to_3d_curve((0.0, 1.0), bw.curve_from_bs(curve))
        edge_start.attach_to_plane(bw_surf, uv_v_bot[0], uv_v_top[0])

        curve = bs_approx.line( [v10, v11] )
        edge_end.attach_to_3d_curve((0.0, 1.0), bw.curve_from_bs(curve))
        edge_end.attach_to_plane(bw_surf, uv_v_bot[1], uv_v_top[1])

        return bw_surf

    def make_shapes(self):
        shapes = []

        vert_edges=[]

        for i, i_reg in enumerate(self.node_region_ids):
            edge = bw.Edge( [self.i_bot.vertices[i].shape, self.i_top.vertices[i].shape] )
            edge.implicit_curve()
            edge_info = ShapeInfo(edge)
            vert_edges.append(edge_info)
            if self.regions[i_reg].is_active(1):
                edge_info.set( i_reg, self.i_top, self.i_bot)
            shapes.append(edge_info)
        assert len(vert_edges) == self.topology.n_nodes, "n_vert_edges: %d n_nodes: %d"%(len(vert_edges), self.topology.n_nodes)
        assert len(vert_edges) == len(self.node_region_ids)

        vert_faces = []
        for i, i_reg in enumerate(self.segment_region_ids):
            segment = self.topology.segments[i]
            # make face oriented to the right side of the segment when looking from top

            edge_start = vert_edges[segment.node_ids[0]].shape
            si_bot = self.i_bot.edges[i]
            edge_bot = si_bot.shape
            edge_end = vert_edges[segment.node_ids[1]].shape
            si_top = self.i_top.edges[i]
            edge_top = si_top.shape

            # make planar surface
            # attach curves to top and bot edges
            vert_surface = self.make_vert_bw_surface(si_top, si_bot, edge_start, edge_end)


            # edges oriented counter clockwise = positively oriented face
            wire = bw.Wire([edge_start.m(), edge_bot, edge_end, edge_top.m()])
            face = bw.Face([wire], surface = vert_surface)
            face_info = ShapeInfo(face)
            vert_faces.append(face_info)
            if self.regions[i_reg].is_active(2):
                face_info.set(i_reg, self.i_top, self.i_bot)
            shapes.append(face_info)
        assert len(vert_faces) == len(self.topology.segments)
        assert len(vert_faces) == len(self.segment_region_ids)

        for i, i_reg in enumerate(self.polygon_region_ids):

            polygon = self.topology.polygons[i]
            segment_ids = polygon.segment_ids  # segment_id > n_segments .. reversed edge

            # we orient all faces inwards (assuming normal oriented up for counter clockwise edges, right hand rule)
            # assume polygons oriented upwards
            faces = []
            for id_seg in segment_ids:
                i_seg, reversed = self.topology.orient_segment(id_seg)
                if reversed:
                    faces.append( vert_faces[i_seg].shape.m() )
                else:
                    faces.append( vert_faces[i_seg].shape )
            faces.append( self.i_top.faces[i].shape )
            faces.append( self.i_bot.faces[i].shape.m() )
            shell = bw.Shell( faces )
            solid = bw.Solid([shell])
            solid_info = ShapeInfo(solid)
            if self.regions[i_reg].is_active(3):
                solid_info.set(i_reg, self.i_top, self.i_bot)
            shapes.append(solid_info)

        return shapes

class UserSupplement(gs.UserSupplement):
    pass


class LayerGeometry(gs.LayerGeometry):

    el_type_to_dim = {15: 0, 1: 1, 2: 2, 4: 3}

    """
        - create BREP B-spline approximation from Z-grids (Bapprox)
        - load other surfaces
        - create BREP geometry from it (JB)

        - write BREP geometry into a file (JE)
        - visualize BREP geometry or part of it
        - call GMSH to create the mesh (JB)
        //- convert mesh into GMSH file format from Netgen
        - name physical groups (JB)
        - scale the mesh nodes verticaly to fit original interfaces (JB, Jakub)
        - find rivers and assign given regions to corresponding elements (JB, Jakub)
    """

    @staticmethod
    def set_ids(xlist):
        for i, item in enumerate(xlist):
            item.id = i

    def init(self):
        # keep unique interface per surface
        self.interfaces = len(self.surfaces) * [None]
        self.brep_shapes=[]     # Final shapes in top compound to being meshed.

        self.set_ids(self.surfaces)
        self.set_ids(self.topologies)
        #self.set_ids(self.nodesets)

        # load and construct grid surface functions
        for surf in self.surfaces:
            surf.set_file(self.filename_base)


        # initialize layers, neigboring layers refer to common interface
        for id, layer in enumerate(self.layers):
            layer.id = id
            layer.init(self)



    def construct_brep_geometry(self):
        """
        Algorithm for creating geometry from Layers:

        3d_region = CompoundSolid of Soligs from extruded polygons
        2d_region, .3d_region = Shell of:
            - Faces from extruded segments (vertical 2d region)
            - Faces from polygons (horizontal 2d region)
        1d_region, .2d_region = Wire of:
            - Edges from extruded points (vertical 1d regions)
            - Edges from segments (horizontal 1d regions)

        1. on every noncompatible interface make a subdivision of segments and polygons for all topologies on it
            i.e. every segment or polygon cen get a list of its sub-segments, sub-polygons

        2. Create Vertexes, Edges and Faces for points, segments and polygons of subdivision on interfaces, attach these to
           point, segment and polygon objects of subdivided topologies

        3. For every 3d layer:

                for every segment:
                    - create face, using top and bottom subdivisions, and pair of verical edges as boundary
                for every polygon:
                    - create list of faces for top and bottom using BREP shapes of polygon subdivision on top and bottom
                    - make shell and solid from faces of poligon side segments and top and bottom face

                for every region:
                    create compound object from its edges/faces/solids

        4. for 2d layer:
                for every region:
                    make compoud of subdivision BREP shapes

        """
        self.split_to_blocks()

        #self.vertices={}            # (interface_id, interface_node_id) : bw.Vertex
        #self.extruded_edges = {}    # (layer_id, node_id) : bw.Edge, orented upward, Loacl to Layer


        self.all_shapes=[]
        self.free_shapes =[]

        for block in self.blocks:
            for layer in block:
                self.all_shapes += layer.make_shapes()


        for i_face in self.interfaces:
            for shp in i_face.iter_shapes():
                self.all_shapes.append(shp)

        self.free_shapes = [ shp_info for shp_info in self.all_shapes if shp_info.free ]
        # sort down from solids to vertices
        self.free_shapes.sort(key=lambda shp: shp.dim(), reverse=True)
        self.free_shapes = [shp_info.shape for shp_info in self.free_shapes]

        compound = bw.Compound(self.free_shapes)
        compound.set_free_shapes()
        self.brep_file = os.path.abspath(self.filename_base + ".brep")
        with open(self.brep_file, 'w') as f:
            bw.write_model(f, compound, bw.Location() )


        # ignore shapes without ID - not part of the output
        self.all_shapes = [ si for si in self.all_shapes if hasattr(si.shape,  'id') ]
        self.compute_bounding_box()

        # prepare dict: (dim, shape_id) : shape info
        self.all_shapes.sort(key=lambda si: si.shape.id, reverse=True)
        shape_by_dim=[[] for i in range(4)]
        for shp_info in self.all_shapes:
            dim = shp_info.dim()
            shape_by_dim[dim].append(shp_info)

        self.shape_dict = {}
        for dim, shp_list in enumerate(shape_by_dim):
            for gmsh_shp_id, si in enumerate(shp_list):
                self.shape_dict[(dim, gmsh_shp_id + 1)] = si

        # debug listing
        #xx=[ (k, v.shape.id) for k, v in self.shape_dict.items()]
        #xx.sort(key=lambda x: x[0])
        #for i in xx:
        #    print(i[0][0], i[0][1], i[1])

    def split_to_blocks(self):
        blocks=[]
        block=[]
        last_id=None
        for layer in self.layers:
            if last_id == None:
                last_id = layer.topology.id
            if layer.topology.id == last_id:
                block.append(layer)
            else:
                last_id = layer.topology.id
                blocks.append(block)
                block=[]
        blocks.append(block)
        self.blocks=blocks

    def compute_bounding_box(self):
        min_vtx = np.ones(3) * (np.inf)
        max_vtx = np.ones(3) * (-np.inf)
        assert len(self.all_shapes) > 0, "Empty list of shapes to mesh."
        for si in self.all_shapes:
            if hasattr(si.shape, 'point'):
                min_vtx = np.minimum(min_vtx, si.shape.point)
                max_vtx = np.maximum(max_vtx, si.shape.point)
        assert np.all(min_vtx < np.inf)
        assert np.all(max_vtx > -np.inf)
        self.aabb = [ min_vtx, max_vtx ]


    def mesh_step_estimate(self):
        char_length = np.max(self.aabb[1] - self.aabb[0])
        mesh_step = char_length / 20
        print("Char length: {} mesh step: {}", char_length, mesh_step)
        return mesh_step


    def call_gmsh(self, mesh_step):
        if mesh_step == 0.0:
            mesh_step = self.mesh_step_estimate()
        self.geo_file = self.filename_base + ".tmp.geo"
        with open(self.geo_file, "w") as f:
            print('Merge "%s";\n'%(self.brep_file), file=f)
            print('Field[1] = MathEval;\n', file=f)
            print('Field[1].F = "%f";\n'%(mesh_step), file=f)
            print('Background Field = 1;\n', file=f)

        from subprocess import call
        gmsh_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../gmsh/gmsh.exe")
        if not os.path.exists(gmsh_path):
            gmsh_path = "gmsh"
        call([gmsh_path, "-3", self.geo_file])



    def deform_mesh(self):
        """
        In fact three different algorithms are necessary:
        I. Modification of extruded mesh, surfaces are horizontal planes.
        II. Small modification of curved mesh, modify just surface nodes and possibly
            small number of neighbouring elements.
        III. Big modification o curved mesh, need to evaluate discrete surface. Line/triangle intersection, need BIH.
        :return:
        """
        # The I. algorithm:
        # new empty nodes list
        # go through volume elements; every volume region should have reference to its top and bot interface;
        # move nodes of volume element
        nodes_shift = { id: [] for id, el in self.mesh.nodes.items()}
        for id, elm in self.mesh.elements.items():
            el_type, tags, nodes = elm
            if len(tags) < 2:
                raise Exception("Less then 2 tags.")
            dim = self.el_type_to_dim[el_type]
            shape_id = tags[1]
            shape_info = self.shape_dict[ (dim, shape_id) ]
            if not shape_info.free:
                continue
            for i_node in nodes:
                x,y,z = self.mesh.nodes[i_node]
                top_ref_z = shape_info.top_iface.surface.depth
                top_z = shape_info.top_iface.surface.eval_z(x,y)
                bot_ref_z = shape_info.bot_iface.surface.depth
                bot_z = shape_info.bot_iface.surface.eval_z(x, y)
                assert bot_ref_z >= z and z >= top_ref_z, "{} >= {} >= {}".format(bot_ref_z, z, top_ref_z)
                if shape_info.top_iface.surface.id == shape_info.bot_iface.surface.id:
                    z_shift = top_z - z
                else:
                    t = (z - bot_ref_z) / (top_ref_z - bot_ref_z)
                    z_shift = (1 - t) * bot_z + t * top_z - z
                nodes_shift[i_node].append( z_shift )

        for id, shift_list in nodes_shift.items():
            assert len(shift_list) != 0, "Node: {}".format(id)
            mean_shift = sum(shift_list) / float(len(shift_list))
            assert sum([ math.fabs(x - mean_shift) for x in shift_list]) / float(len(shift_list)) < math.fabs(mean_shift)/100.0,\
                "{} List: {}".format(id, shift_list)
            self.mesh.nodes[id][2] += mean_shift

    def modify_mesh(self):
        self.tmp_msh_file = self.filename_base + ".tmp.msh"
        self.mesh = gmsh_io.GmshIO()
        with open(self.tmp_msh_file, "r") as f:
            self.mesh.read(f)

        # deform mesh, nontrivial evaluation of Z for the interface mesh
        #self.deform_mesh()


        new_elements = {}
        for id, elm in self.mesh.elements.items():
            el_type, tags, nodes = elm
            if len(tags) < 2:
                raise Exception("Less then 2 tags.")
            dim = self.el_type_to_dim[el_type]
            shape_id = tags[1]
            shape_info = self.shape_dict[ (dim, shape_id) ]

            if not shape_info.free:
                continue
            region = self.regions[shape_info.i_reg]
            if not region.is_active(dim):
                continue
            assert region.dim == dim
            physical_id = shape_info.i_reg + 10000
            if region.name in self.mesh.physical:
                assert self.mesh.physical[region.name][0] == physical_id
            else:
                self.mesh.physical[region.name] = (physical_id, dim)
            tags[0] = physical_id
            new_elements[id] = (el_type, tags, nodes)
        self.mesh.elements = new_elements
        self.msh_file = self.filename_base + ".msh"
        with open(self.msh_file, "w") as f:
            self.mesh.write_ascii(f)



    # def mesh_export(self, mesh, filename):
    #     """ export Netgen mesh to neutral format """
    #
    #     print("export mesh in neutral format to file = ", filename)
    #
    #     f = open(filename, 'w')
    #
    #     points = mesh.Points()
    #     print(len(points), file=f)
    #     for p in points:
    #         print(p.p[0], p.p[1], p.p[2], file=f)
    #
    #     volels = mesh.Elements3D();
    #     print(len(volels), file=f)
    #     for el in volels:
    #         print(el.index, end="   ", file=f)
    #         for p in el.points:
    #             print(p.nr, end=" ", file=f)
    #         print(file=f)

    # def mesh_netgen(self):
    #     """
    #     Use Netgen python interface to make a mesh.
    #     :return:
    #     """
    #
    #     geo = ngcsg.CSGeometry("shaft.geo")
    #
    #     param = ngmesh.MeshingParameters()
    #     param.maxh = 10
    #     print(param)
    #
    #     m1 = ngcsg.GenerateMesh(geo, param)
    #     m1.SecondOrder()
    #
    #     self.mesh_export(m1, "shaft.mesh")
    #
    #     ngcsg.Save(m1, "mesh.vol", geo)
    #     print("Finished")
    #
    # def netgen_to_gmsh(self):
    #     pass



def construct_derived_geometry(gs_obj):
    if issubclass(gs_obj.__class__, js.JsonData):
        geo_name = gs_obj.__class__.__name__
        class_obj = getattr(sys.modules[__name__], geo_name)
        geo_obj =  class_obj.__new__(class_obj)
        for key, item in  gs_obj.__dict__.items():
            item = construct_derived_geometry(item)
            geo_obj.__dict__[key] = item
    elif isinstance(gs_obj, (list, tuple)):
        new_item = [ construct_derived_geometry(i) for i in gs_obj ]
        geo_obj = gs_obj.__class__(new_item)
    elif isinstance(gs_obj, dict):
        for k, v in gs_obj.items():
            gs_obj[k] = construct_derived_geometry(value)
        geo_obj = gs_obj
    else:
        geo_obj = gs_obj
    return geo_obj


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('layers_file', help="Input Layers file (JSON).")
    parser.add_argument("--mesh-step", type=float, default=0.0, help="Maximal global mesh step.")
    args = parser.parse_args()

    from geometry_files.geometry import GeometrySer
    layers_file = args.layers_file
    filename_base = os.path.splitext(layers_file)[0]
    geom_serializer = GeometrySer(layers_file)
    gs_lg = geom_serializer.read()
    lg = construct_derived_geometry(gs_lg)
    lg.filename_base = filename_base

    lg.init()   # initialize the tree with ids and references where necessary

    lg.construct_brep_geometry()
    #geom.mesh_netgen()
    #geom.netgen_to_gmsh()

    lg.call_gmsh(args.mesh_step)
    lg.modify_mesh()

