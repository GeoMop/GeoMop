import sys
import os

geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

import geometry_files.geometry_structures
from geometry_files.geometry import GeometrySer
import brep_writer as bw

###
netgen_install_prefix="/home/jb/local/"
netgen_path = "opt/netgen/lib/python3/dist-packages"
sys.path.append( netgen_install_prefix + netgen_path )

import netgen.csg as ngcsg
import netgen.meshing as ngmesh





class Geometry:
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
    def __init__(self):
        self.lg = None
        # Layers geometry. Initializaed by load method.
        self.brep = None
        # Finally bw.Compound of whole geometry.
        self.filename_base = None
        # base dir and file_name for auxiliary files: .brep, ..., .msh

    def load(self, layers_file):
        from geometry_files.geometry import GeometrySer
        self.filename_base = os.path.splitext(layers_file)[0]
        geom_serializer = GeometrySer(layers_file)
        self.lg = geom_serializer.read()

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

        return self.brep

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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('layers_file', help="Input Layers file (JSON).")
    args = parser.parse_args()

    geom = Geometry()
    geom.load(args.layers_file)
    geom.construct_brep_geometry()
    #geom.mesh_netgen()
    #geom.netgen_to_gmsh()



