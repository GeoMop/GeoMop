import os
import shutil

from gm_base.geomop_analysis import YamlSupportLocal


class Flow123dActionPreparation():
    @staticmethod
    def prepare(resources, source_dir, output_dir):
        err = []
        input_files = []

        # copy yaml
        yaml_file = resources["YAMLFile"]
        yaml_dir, yaml_name = os.path.split(yaml_file)
        os.makedirs(os.path.join(output_dir, yaml_dir), exist_ok=True)
        shutil.copyfile(os.path.join(source_dir, yaml_file), os.path.join(output_dir, yaml_file))
        input_files.append(yaml_file)

        # copy input files
        ys = YamlSupportLocal()
        e = ys.parse(yaml_file)
        if len(e) > 0:
            err.extend(e)
            return err, input_files
        for file in ys.get_input_files():
            dir = os.path.dirname(file)
            os.makedirs(os.path.join(output_dir, yaml_dir, dir), exist_ok=True)
            shutil.copyfile(os.path.join(source_dir, yaml_dir, file), os.path.join(output_dir, yaml_dir, file))
            input_files.append(file)

        # create support file
        ys = YamlSupportLocal()
        e = ys.parse(os.path.join(output_dir, yaml_file))
        if len(e) > 0:
            err.extend(e)
            return err, input_files
        s = yaml_name.rsplit(sep=".", maxsplit=1)
        new_name = s[0] + ".sprt"
        sprt_file = os.path.join(output_dir, yaml_dir, new_name)
        ys.save(sprt_file)
        input_files.append(os.path.join(yaml_dir, new_name))

        return err, input_files
