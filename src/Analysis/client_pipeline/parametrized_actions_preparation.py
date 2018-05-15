import os
import shutil

from gm_base.geomop_analysis import YamlSupportLocal


class Flow123dActionPreparation():
    @staticmethod
    def prepare(resources, source_dir, output_dir):
        err = []
        input_files = []

        # copy yaml
        yaml_file = os.path.join(source_dir, resources["YAMLFile"])
        yaml_file_new = shutil.copy(yaml_file, output_dir)
        input_files.append(resources["YAMLFile"])

        # copy mesh file
        ys = YamlSupportLocal()
        e = ys.parse(yaml_file)
        if len(e) > 0:
            err.extend(e)
            return err, input_files
        shutil.copy(os.path.join(source_dir, ys.get_mesh_file()), output_dir)
        input_files.append(ys.get_mesh_file())

        # create support file
        ys = YamlSupportLocal()
        e = ys.parse(yaml_file_new)
        if len(e) > 0:
            err.extend(e)
            return err, input_files
        dir, name = os.path.split(yaml_file_new)
        s = name.rsplit(sep=".", maxsplit=1)
        new_name = s[0] + ".sprt"
        sprt_file = os.path.join(dir, new_name)
        ys.save(sprt_file)
        input_files.append(new_name)

        return err, input_files
