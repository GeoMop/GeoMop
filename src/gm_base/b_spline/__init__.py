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


