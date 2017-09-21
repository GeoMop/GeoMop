import pytest

import json_data as js
import geometry_files.geometry_structures as gs
import filecmp
import json
from geometry_files.geometry import GeometrySer


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
        geom_serializer = GeometrySer(layers_file)
        gs_lg = geom_serializer.read()
        out_file = layers_file + ".out"
        gs = GeometrySer(out_file)
        gs.write(gs_lg)
        return out_file


    def test_reload_simple(self):
        layers_file = "./layers_simple.json"
        self.check(layers_file, self.reload(layers_file))

    def test_reload_flat(self):
        layers_file = "./layers_flat_0.json"
        assert self.check(layers_file, self.reload(layers_file))