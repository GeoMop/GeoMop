"""
TODO:
- check how GMSH number surfaces standing alone,
  seems that it number object per dimension by the IN time in DFS from solids down to Vtx,
  just ignoring main compound, not sure how numbering works for free standing surfaces.

"""
import sys
import os

geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

import json_data as js
import geometry_files.geometry_structures as gs
from geometry_files.geometry import GeometrySer
import brep_writer as bw
import gmsh_io


###
netgen_install_prefix="/home/jb/local/"
netgen_path = "opt/netgen/lib/python3/dist-packages"
sys.path.append( netgen_install_prefix + netgen_path )

import netgen.csg as ngcsg
import netgen.meshing as ngmesh


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


class Curve(gs.Curve):
    pass

class Surface(gs.Surface):
    def z_eval(self, X):
        x, y = X
        z_shift = self.transform[3][2]
        return z_shift

    @staticmethod
    def interpol(a, b, t):
        return (t * b + (1-t) * a)

    def line_intersect(self, a, b):
        z = self.transform[3][2]
        t = (a[2] - z) / (a[2] - b[2])
        # (1-t) = (z - bz) / (az - bz)
        x = self.interpol(a[0], b[0], t )
        y = self.interpol(a[1], b[1], t )
        return (x, y, z)

class Segment(gs.Segment):
    pass

class Polygon(gs.Polygon):
    pass

class Topology(gs.Topology):
    """
    TODO:
    - support for polygons with holes, here and in creation of faces and solids
    """
    def init(self):
        node_id_set = { nid for segment in self.segments for nid in segment.node_ids }

        self.n_nodes =  len(node_id_set)
        assert self.n_nodes == max(node_id_set) + 1
        self.n_segments  = len(self.segments)

        for poly in self.polygons:
            self.orient_polygon(poly)

    def orient_polygon(self, poly):
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
        return id_seg + reversed*self.n_segments


    def orient_segment(self, id_seg):
        if id_seg >= len(self.segments):
            return id_seg - self.n_segments, True
        else:
            return id_seg, False

class NodeSet(gs.NodeSet):
    pass

#class Interface(gs.Interface):
#    pass

class Interface:
    def __init__(self, surface, nodes, topology):
        self.surface = surface
        self.topology = topology
        if nodes is not None:
            self.nodes = [ (X[0], X[1], self.surface.z_eval(X) ) for X in nodes]
        self.make_shapes()


    def make_shapes(self):
        self.vertices = [ ShapeInfo(bw.Vertex(node)) for node in self.nodes]
        self.edges = []
        for segment in self.topology.segments:
            #nodes_id, surface_id = segment
            na, nb = segment.node_ids
            edge = bw.Edge( [self.vertices[na].shape, self.vertices[nb].shape] )
            self.edges.append( ShapeInfo(edge) )
        self.faces = []
        n_segments = len(self.topology.segments)
        for poly in self.topology.polygons:
            #segment_ids, surface_id = poly      # segment_id > n_segments .. reversed edge
            edges = []
            for id_seg in poly.segment_ids:
                i_seg, reversed = self.topology.orient_segment(id_seg)
                if reversed:
                    edges.append(self.edges[i_seg].shape.m())
                else:
                    edges.append(self.edges[i_seg].shape)
            wire = bw.Wire(edges)
            face = bw.Face([wire])
            self.faces.append( ShapeInfo(face) )


    def interpolate_interface(self, a_surface, a_nodes, b_surface, b_nodes):
        assert len(a_nodes) == len(b_nodes)
        self.nodes=[]
        for (ax, ay), (bx, by) in zip(a_nodes, b_nodes):
            az = a_surface.z_eval( (ax, ay) )
            bz = b_surface.z_eval( (bx, by) )
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
        assert topo_dim == self.topo_dim
        if self.not_used:
            return
        if hasattr(self, 'dim'):
            assert self.dim == topo_dim + extrude, "dim: %d tdim: %d ext: %d"%(self.dim, topo_dim, extrude)
        else:
            self.dim = topo_dim + extrude

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

    def make_shapes(self):
        shapes = []

        vert_edges=[]

        for i, i_reg in enumerate(self.node_region_ids):
            edge = bw.Edge( [self.i_bot.vertices[i].shape, self.i_top.vertices[i].shape] )
            edge_info = ShapeInfo(edge)
            vert_edges.append(edge_info)
            if self.regions[i_reg].is_active(1):
                edge_info.set( i_reg, self.i_top, self.i_bot)
            shapes.append(edge_info)
        assert len(vert_edges) == self.topology.n_nodes, "n_vert_faces: %d n_nodes: %d"%(len(vert_faces), self.topology.n_nodes)
        assert len(vert_edges) == len(self.node_region_ids)

        vert_faces = []
        for i, i_reg in enumerate(self.segment_region_ids):
            segment = self.topology.segments[i]
            # make face oriented to the right side of the segment when looking from top

            edge_start = vert_edges[segment.node_ids[0]].shape
            edge_bot = self.i_bot.edges[i].shape
            edge_end = vert_edges[segment.node_ids[1]].shape
            edge_top = self.i_top.edges[i].shape

            # edges oriented counter clockwise = positively oriented face
            wire = bw.Wire([edge_start.m(), edge_bot, edge_end, edge_top.m()])
            face = bw.Face([wire])
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
        last_interface = None

        # orient polygons
        for topo in self.topologies:
            topo.init()

        # initialize layers, neigboring layers refer to common interface
        for layer in self.layers:
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
        self.brep_file = self.filename_base + ".brep"
        with open(self.brep_file, 'w') as f:
            bw.write_model(f, compound, bw.Location() )

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


    def call_gmsh(self):
        self.geo_file = self.filename_base + ".tmp.geo"
        self.mesh_step = 5
        with open(self.geo_file, "w") as f:
            print('Merge "%s";\n'%(self.brep_file), file=f)
            print('Field[1] = MathEval;\n', file=f)
            print('Field[1].F = "%f";\n'%(self.mesh_step), file=f)
            print('Background Field = 1;\n', file=f)

        from subprocess import call
        call(["gmsh", "-3", self.geo_file])

    def modify_mesh(self):
        self.tmp_msh_file = self.filename_base + ".tmp.msh"
        self.mesh = gmsh_io.GmshIO()
        with open(self.tmp_msh_file, "r") as f:
            self.mesh.read(f)

        # deform mesh, nontrivial evaluation of Z for the interface mesh


        el_type_to_dim = {15:0, 1:1, 2:2, 4:3}
        new_elements = {}
        for k, elm in self.mesh.elements.items():
            el_type, tags, nodes = elm
            if len(tags) < 2:
                raise Exception("Less then 2 tags.")
            dim = el_type_to_dim[el_type]
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
            new_elements[k] = (el_type, tags, nodes)
        self.mesh.elements = new_elements
        self.msh_file = self.filename_base + ".msh"
        with open(self.msh_file, "w") as f:
            self.mesh.write_ascii(f)



    def mesh_export(self, mesh, filename):
        """ export Netgen mesh to neutral format """

        print("export mesh in neutral format to file = ", filename)

        f = open(filename, 'w')

        points = mesh.Points()
        print(len(points), file=f)
        for p in points:
            print(p.p[0], p.p[1], p.p[2], file=f)

        volels = mesh.Elements3D();
        print(len(volels), file=f)
        for el in volels:
            print(el.index, end="   ", file=f)
            for p in el.points:
                print(p.nr, end=" ", file=f)
            print(file=f)

    def mesh_netgen(self):
        """
        Use Netgen python interface to make a mesh.
        :return:
        """

        geo = ngcsg.CSGeometry("shaft.geo")

        param = ngmesh.MeshingParameters()
        param.maxh = 10
        print(param)

        m1 = ngcsg.GenerateMesh(geo, param)
        m1.SecondOrder()

        self.mesh_export(m1, "shaft.mesh")

        ngcsg.Save(m1, "mesh.vol", geo)
        print("Finished")

    def netgen_to_gmsh(self):
        pass



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

    lg.call_gmsh()
    lg.modify_mesh()

