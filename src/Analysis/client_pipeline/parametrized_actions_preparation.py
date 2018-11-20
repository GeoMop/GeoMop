import os
import shutil

from gm_base.geomop_analysis import YamlSupportLocal


def _check_path_inside(path):
    """Check if path is relative and inside dir."""
    if os.path.isabs(path):
        return False
    normpath = os.path.normpath(path)
    if normpath in [".", ".."] or \
            normpath.startswith("../") or \
            (os.sep == "\\" and normpath.startswith("..\\")):
        return False
    return True


class Flow123dActionPreparation():
    @staticmethod
    def prepare(resources, source_dir, output_dir):
        err = []
        input_files = []

        # copy yaml
        yaml_file = resources["YAMLFile"]
        if not _check_path_inside(yaml_file):
            err.append("Flow123d: Path to YAML file must be relative and inside analysis directory. ({})"
                       .format(yaml_file))
            return err, input_files
        if not os.path.isfile(os.path.join(source_dir, yaml_file)):
            err.append("Flow123d: YAML file does not exist. ({})"
                       .format(yaml_file))
            return err, input_files
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
            yaml_dir_file = os.path.join(yaml_dir, file)
            if not _check_path_inside(yaml_dir_file):
                err.append("Flow123d: Path to input file must be relative and inside analysis directory. ({})"
                           .format(yaml_dir_file))
                return err, input_files
            if not os.path.isfile(os.path.join(source_dir, yaml_dir_file)):
                err.append("Flow123d: Input file does not exist. ({})"
                           .format(yaml_dir_file))
                return err, input_files
            dir = os.path.dirname(file)
            os.makedirs(os.path.join(output_dir, yaml_dir, dir), exist_ok=True)
            shutil.copyfile(os.path.join(source_dir, yaml_dir_file), os.path.join(output_dir, yaml_dir_file))
            input_files.append(yaml_dir_file)

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
