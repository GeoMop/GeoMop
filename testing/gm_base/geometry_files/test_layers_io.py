import pytest

import gm_base.json_data as js
import gm_base.geometry_files.format_last as gs
import filecmp
import os
import json
import gm_base.geometry_files.layers_io as layers_io

script_dir = os.path.os.path.dirname(os.path.realpath(__file__))

def get_path(f):
    return os.path.join(script_dir, "test_data", f)

class TestGeometryStructures:
    # Test Read/Write of Geometry structures and its interaction with JSONData

    def check(self, f_ref, f_out):
        """
        File cmp.
        :return:
        """
        # normalize reference file
        with open(f_ref) as f:
            data = json.loads(f.read(), encoding="utf-8")
        with open(f_ref, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

        return filecmp.cmp(f_ref, f_out)



    def reload(self, layers_file):
        gs_lg = layers_io.read_geometry(layers_file)
        out_file = layers_file + ".out"
        gs = self.write_geometry(out_file, gs_lg)
        return out_file

    def write_geometry(self, file_name, lg):
        """Write LayerGeometry data to file"""
        with open(file_name, 'w') as f:
            json.dump(lg.serialize(), f, indent=4, sort_keys=True)



    def test_reload_simple(self, paths_to_remove):
        layers_file = get_path("layers_simple.json")
        out_file = self.reload(layers_file)
        paths_to_remove.append(out_file)
        assert self.check(layers_file + ".ref", out_file)

    def test_reload_flat(self, paths_to_remove):
        layers_file = get_path("layers_flat_0.json")
        out_file = self.reload(layers_file)
        paths_to_remove.append(out_file)
        assert self.check(layers_file + ".ref", out_file)
