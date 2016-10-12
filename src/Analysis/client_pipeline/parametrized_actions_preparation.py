import os
import shutil

from geomop_analysis import YamlSupportLocal


class Flow123dActionPreparation():
    @staticmethod
    def prepare(resources, output_dir):
        # copy yaml
        yaml_file_new = shutil.copy(resources["YAMLFile"], output_dir)

        # create support file
        ys = YamlSupportLocal()
        err = ys.parse(yaml_file_new)
        dir, name = os.path.split(yaml_file_new)
        s = name.rsplit(sep=".", maxsplit=1)
        new_name = s[0] + ".sprt"
        sprt_file = os.path.join(dir, new_name)
        ys.save(sprt_file)

        # copy mesh file
        dir, name = os.path.split(resources["YAMLFile"])
        shutil.copy(os.path.join(dir, ys.get_mesh_file()), output_dir)
