"""
This file contains algorithms for
1. constructing a 3D geometry in the BREP format
   (see https://docs.google.com/document/d/1qWq1XKfHTD-xz8vpINxpfQh4k6l1upeqJNjTJxeeOwU/edit#)
   from the Layer File format (see geometry_structures.py).
2. meshing the 3D geometry (e.g. using GMSH)
3. setting regions to the elements of the resulting mesh and other mesh postprocessing


TODO:
- check how GMSH number surfaces standing alone,
  seems that it number object per dimension by the IN time in DFS from solids down to Vtx,
  just ignoring main compound, not sure how numbering works for free standing surfaces.

- finish usage of polygon decomposition (without split)
- implement intersection in interface_finish_init
- tests

Heterogeneous mesh step:

- storing mesh step from regions into shape info objects
- ( brep created )
-
- add include


"""


import os
import sys
import subprocess



#geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "gm_base")
#intersections_src = os.path.join(os.path.dirname(os.path.realpath(__file__)), "intersections","src")
#sys.path.append(geomop_src)
#sys.path.append(intersections_src)

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import gm_base.json_data as js
import gm_base.geometry_files.format_last as gs
import gm_base.geometry_files.layers_io as layers_io
import bgem.polygons.polygons as polygons
import bgem.polygons.merge as merge
import gm_base.polygons.polygons_io as polygons_io
import gm_base.geometry_files.bspline_io as bspline_io
import bgem.gmsh.gmsh_io as gmsh_io
import numpy as np
import numpy.linalg as la
import math

import bgem.bspline.bspline as bs
import bgem.bspline.bspline_approx as bs_approx
import bgem.bspline.brep_writer as bw

from bgem.geometry import geometry

# def import_plotting():
# global plt
# global bs_plot

#import gm_base.geometry_files.plot_polygons as plot_polygons

#import matplotlib
#import matplotlib.pyplot as plt

#import bspline_plot as bs_plot


###
#netgen_install_prefix="/home/jb/local/"
#netgen_path = "opt/netgen/lib/python3/dist-packages"
#sys.path.append( netgen_install_prefix + netgen_path )

#import netgen.csg as ngcsg
#import netgen.meshing as ngmesh

class ExcGMSHCall(Exception):
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "Error in GMSH call.\n\nSTDOUT:\n{}\n\nSTDERR:\n{}".format(self.stdout, self.stderr)


def _conv_surface(gs_surface):
    surf = geometry.Surface()

    surf.grid_file = gs_surface.grid_file
    surf.file_skip_lines = gs_surface.file_skip_lines
    surf.file_delimiter = gs_surface.file_delimiter
    surf.name = gs_surface.name
    surf.approximation = gs_surface.approximation
    surf.regularization = gs_surface.regularization
    surf.approx_error = gs_surface.approx_error

    return surf


def _make_decomp(raw_geometry, gs_layer, iface_nodeset, reg_map):
    # handle InterpolatedNodeSet
    if isinstance(iface_nodeset, gs.InterpolatedNodeSet):
        a, b = iface_nodeset.surf_nodesets
        if (a.nodeset_id != b.nodeset_id) or (
            raw_geometry.node_sets[a.nodeset_id].topology_id != raw_geometry.node_sets[b.nodeset_id].topology_id):
            assert False, "Interpolation of different nodesets not supported yet."
        iface_nodeset = a

    # make decomposition
    decomp = polygons_io.deserialize(raw_geometry.node_sets[iface_nodeset.nodeset_id].nodes,
                                     raw_geometry.topologies[raw_geometry.node_sets[iface_nodeset.nodeset_id].topology_id])

    # set regions
    for pt in decomp.points.values():
        reg = reg_map[gs_layer.node_region_ids[pt.id]]
        decomp.set_attr(pt, reg)
    for seg in decomp.segments.values():
        reg = reg_map[gs_layer.segment_region_ids[seg.id]]
        decomp.set_attr(seg, reg)
    for poly in decomp.polygons.values():
        reg = reg_map[gs_layer.polygon_region_ids[poly.id]]
        decomp.set_attr(poly, reg)

    return decomp


def _construct_geometry(raw_geometry):
    # create geometry object
    lg = geometry.LayerGeometry()

    # add surfaces
    for gs_surface in raw_geometry.surfaces:
        lg.surfaces.append(_conv_surface(gs_surface))

    # add interfaces
    iface_map = {}
    for i, gs_iface in enumerate(raw_geometry.interfaces):
        iface = lg.add_interface(
            surface_id=gs_iface.surface_id,
            transform_z=gs_iface.transform_z,
            elevation=gs_iface.elevation
        )
        iface_map[i] = iface

    # add regions
    reg_map = {}
    for i, gs_region in enumerate(raw_geometry.regions):
        reg = lg.add_region(
            color=gs_region.color,
            name=gs_region.name,
            dim=geometry.RegionDim[gs_region.dim.name],
            topo_dim=geometry.TopologyDim[gs_region.topo_dim.name],
            boundary=gs_region.boundary,
            not_used=gs_region.not_used,
            mesh_step=gs_region.mesh_step
        )
        reg.brep_shape_ids = gs_region.brep_shape_ids
        reg_map[i] = reg

    # add layers
    for gs_layer in raw_geometry.layers:
        if isinstance(gs_layer, gs.StratumLayer):
            top_decomp = _make_decomp(raw_geometry, gs_layer, gs_layer.top, reg_map)
            bottom_decomp = _make_decomp(raw_geometry, gs_layer, gs_layer.bottom, reg_map)
            lg.add_stratum_layer(top_decomp, iface_map[gs_layer.top.interface_id],
                                 bottom_decomp, iface_map[gs_layer.bottom.interface_id])
        elif isinstance(gs_layer, gs.FractureLayer):
            top_decomp = _make_decomp(raw_geometry, gs_layer, gs_layer.top, reg_map)
            lg.add_fracture_layer(top_decomp, iface_map[gs_layer.top.interface_id])
        else:
            assert False, "Not supported layer type."

    return lg


def make_geometry(**kwargs):
    """
    TODO: Have LayerGeometry as a class for building geometry, manipulating geometry and meshing.
    then this function is understood as a top level script to us LayerGemoetry API to perform
    basic workflow:
    Read geometry from file or use provided gs.LayerGeometry object.
    Construct the BREP geometry, call gmsh, postprocess mesh.
    Write: geo file, brep file, tmp.msh file, msh file
    """
    raw_geometry = kwargs.get("geometry", None)
    layers_file = kwargs.get("layers_file", None)
    filename_base = kwargs.get("filename_base", "")
    mesh_step = kwargs.get("mesh_step", 0.0)

    if raw_geometry is None:
        if layers_file is None:
            raw_geometry = layers_io.read_geometry(filename_base, sys.stdin)
        else:
            raw_geometry = layers_io.read_geometry(layers_file)
            filename_base = os.path.splitext(layers_file)[0]
    lg = _construct_geometry(raw_geometry)
    lg.filename_base = filename_base

    lg.init()   # initialize the tree with ids and references where necessary

    lg.construct_brep_geometry()
    lg.make_gmsh_shape_dict()
    lg.distribute_mesh_step()

    lg.call_gmsh(mesh_step)
    lg.modify_mesh()
    return lg



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('layers_file', nargs='?', help="Input Layers file (JSON).")
    parser.add_argument("--mesh-step", type=float, default=0.0, help="Maximal global mesh step.")
    parser.add_argument("--filename_base", type=str, default="", help="Base name for output files.")
    args = parser.parse_args()

    try:
        make_geometry(layers_file=args.layers_file, mesh_step=args.mesh_step)
    except ExcGMSHCall as e:
        print(str(e))
