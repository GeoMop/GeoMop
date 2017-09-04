"""
TODO:
- debug why we have empty Compound, seems that nothing is created since  region.is%active is not called.
"""
import sys
import os

geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

import json_data as js
import geometry_files.geometry_structures as gs
from geometry_files.geometry import GeometrySer
import brep_writer as bw

###
netgen_install_prefix="/home/jb/local/"
netgen_path = "opt/netgen/lib/python3/dist-packages"
sys.path.append( netgen_install_prefix + netgen_path )

import netgen.csg as ngcsg
import netgen.meshing as ngmesh


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
        self.vertices = [bw.Vertex(node) for node in self.nodes]
        self.edges = []
        for segment in self.topology.segments:
            #nodes_id, surface_id = segment
            na, nb = segment.node_ids
            edge = bw.Edge( [self.vertices[na], self.vertices[nb]] )
            self.edges.append( edge)
        self.faces = []
        n_segments = len(self.topology.segments)
        for poly in self.topology.polygons:
            #segment_ids, surface_id = poly      # segment_id > n_segments .. reversed edge
            edges = []
            for id_seg in poly.segment_ids:
                i_seg, reversed = self.topology.orient_segment(id_seg)
                if reversed:
                    edges.append(self.edges[i_seg].m())
                else:
                    edges.append(self.edges[i_seg])
            wire = bw.Wire(edges)
            face = bw.Face([wire])
            self.faces.append(face)


    def interpolate_interface(self, a_surface, a_nodes, b_surface, b_nodes):
        assert len(a_nodes) == len(b_nodes)
        self.nodes=[]
        for (ax, ay), (bx, by) in zip(a_nodes, b_nodes):
            az = a_surface.z_eval( (ax, ay) )
            bz = b_surface.z_eval( (bx, by) )
            line = ( (ax, ay, az), (bx,by,bz) )
            x,y,z = self.surface.line_intersect( *line )
            self.nodes.append( (x,y,z) )



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

    def make_shapes(self):
        shapes=[]

        # no point regions
        #for i, i_reg in enumerate(self.node_region_ids):
        #    if self.regions[i_reg].is_active(0):
        #        shapes.append( (self.i_top.vertices[i], i_reg) )

        for i, i_reg in enumerate(self.segment_region_ids):
            if self.regions[i_reg].is_active(1):
                shapes.append( (self.i_top.edges[i], i_reg) )

        for i, i_reg in enumerate(self.polygon_region_ids):
            if self.regions[i_reg].is_active(2):
                shapes.append( (self.i_top.faces[i], i_reg) )
        return shapes

class StratumLayer(gs.StratumLayer):
    def init(self, lg):
        self.i_top = self.top.make_interface(lg)
        self.i_bot = self.bottom.make_interface(lg)
        assert self.i_top.topology.id == self.i_bot.topology.id
        self.topology = self.i_top.topology
        self.regions = lg.regions

    def make_shapes(self):
        shapes = []

        vert_edges=[]

        for i, i_reg in enumerate(self.node_region_ids):
            edge = bw.Edge( [self.i_bot.vertices[i], self.i_top.vertices[i]] )
            vert_edges.append(edge)
            if self.regions[i_reg].is_active(1):
                shapes.append( (edge, i_reg) )
        assert len(vert_edges) == self.topology.n_nodes, "n_vert_faces: %d n_nodes: %d"%(len(vert_faces), self.topology.n_nodes)
        assert len(vert_edges) == len(self.node_region_ids)

        vert_faces = []
        for i, i_reg in enumerate(self.segment_region_ids):
            segment = self.topology.segments[i]
            # make face oriented to the right side of the segment when looking from top

            edge_start = vert_edges[segment.node_ids[0]]
            edge_bot = self.i_bot.edges[i]
            edge_end = vert_edges[segment.node_ids[1]]
            edge_top = self.i_top.edges[i]

            # edges oriented counter clockwise = positively oriented face
            wire = bw.Wire([edge_start.m(), edge_bot, edge_end, edge_top.m()])
            face = bw.Face([wire])
            vert_faces.append(face)
            if self.regions[i_reg].is_active(2):
                shapes.append((face, i_reg))
        assert len(vert_faces) == len(self.topology.segments)
        assert len(vert_faces) == len(self.segment_region_ids)

        for i, i_reg in enumerate(self.polygon_region_ids):
            if self.regions[i_reg].is_active(3):
                polygon = self.topology.polygons[i]
                segment_ids = polygon.segment_ids  # segment_id > n_segments .. reversed edge

                # we orient all faces inwards (assuming normal oriented up for counter clockwise edges, right hand rule)
                # assume polygons oriented upwards
                faces = []
                for id_seg in segment_ids:
                    i_seg, reversed = self.topology.orient_segment(id_seg)
                    if reversed:
                        faces.append( vert_faces[i_seg].m() )
                    else:
                        faces.append( vert_faces[i_seg] )
                faces.append( self.i_top.faces[i] )
                faces.append( self.i_bot.faces[i].m() )
                shell = bw.Shell( faces )
                solid = bw.Solid([shell])

                shapes.append((solid, i_reg))

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

        self.vertices={}            # (interface_id, interface_node_id) : bw.Vertex
        self.extruded_edges = {}    # (layer_id, node_id) : bw.Edge, orented upward, Loacl to Layer
        for block in self.blocks:
            for layer in block:
                self.brep_shapes += layer.make_shapes()

        shapes, shape_regions = zip(*self.brep_shapes)

        compound = bw.Compound(shapes)
        with open("layer_model.brep", 'w') as f:
            bw.write_model(f, compound, bw.Location() )

        shape_to_reg = [ (i, shape.id, i_reg, self.regions[i_reg].dim) for i, (shape, i_reg) in enumerate(self.brep_shapes) ]
        for line in shape_to_reg:
            print(line)

        #print(compound)


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

    lg.init()   # initialize the tree with ids and references where necessary

    lg.construct_brep_geometry()
    #geom.mesh_netgen()
    #geom.netgen_to_gmsh()



