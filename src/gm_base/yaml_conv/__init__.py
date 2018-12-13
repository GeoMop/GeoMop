import sys
import os

geomop_root = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-4])
yaml_converter_dir = os.path.join(geomop_root, "submodules", "yaml_converter")
sys.path.append(yaml_converter_dir)

# append path valid in installed GeoMop
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "yaml_converter"))
