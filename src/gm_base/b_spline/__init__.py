import sys
import os

#from pkgutil import extend_path
#__path__ = extend_path(__path__, __name__)

geomop_root = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-4])
intersections_dir = os.path.join(geomop_root, "submodules", "intersections", "src")
#__path__.insert(0, intersections_dir)
sys.path.append(intersections_dir)

# append path valid in installed GeoMop
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../intersections/src"))

#TODO: Aim was to import individal modules of this package as:
# import b_spline.bspline as bs
# import b_spline.bspline_approx as bs_approx
# ...
#
# However it somehow doesn't work so currently
# we just add the intersection sources into sys.path.

"""
Usage of GridSurface

import bspline as bs

# load file and check the grid
gs = bs.GridSurface.load(file_path)

# Get coordinates of the grid center as numpy array.
center = gs.center()

# Depth:
depth = -center[2]

# Bounding polygon. Numpy array 4 x 2, corners x [x,y].
poly = gs.quad

# Axis aligned bounding box as a numpy array 2x3, [ min_corner, max_corner]
box = gs.aabb()

z_range = box[:, 2]

z_min = z_range[0]
z_max = z_range[1]
"""
