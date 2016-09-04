import codecs
import os
import re

from flow_util import YamlSupportRemote, ObservedQuantitiesValueType
from model_data import Loader, Validator, notification_handler

RE_PARAM = re.compile('<([a-zA-Z][a-zA-Z0-9_]*)>')


class YamlSupportLocal(YamlSupportRemote):
    """
    Class for extract regions, params, active processes
    and mesh file from .yaml files.
    """

    def __init__(self):
        super().__init__()

    def parse(self, file):
        """
        Parse regions, params and active processes from .yaml file.
        Also computes hashes from .yaml and mesh files.
        """
        err = []

        dir_name = os.path.dirname(file)

        document = ""
        try:
            try:
                with codecs.open(file, 'r', 'utf-8') as file_d:
                    document = file_d.read().expandtabs(tabsize=2)
            except UnicodeDecodeError:
                with open(file, 'r') as file_d:
                    document = file_d.read().expandtabs(tabsize=2)
        except (RuntimeError, IOError) as e:
            err.append("Can't open .yaml file: {0}".format(e))
            return err

        loader = Loader(notification_handler)
        validator = Validator(notification_handler)
        notification_handler.clear()
        root = loader.load(document)
        # assert validator.validate(root, cls.root_input_type)

        # mesh file
        node = root.get_node_at_path('/problem/mesh/mesh_file')
        self.mesh_file = node.value

        # active processes
        self.active_processes = {}
        problem_node = root.get_node_at_path('/problem')
        if "flow_equation" in problem_node.children_keys:
            data = {}
            try:
                node = problem_node.get_node_at_path('flow_equation/output_stream/file')
                data["output_stream_file"] = node.value
            except LookupError:
                pass
            try:
                oq = {}
                node = problem_node.get_node_at_path('flow_equation/output/fields')
                vectors = ["velocity_p0"]
                tensors = []
                for child in node.children:
                    if child.value in vectors:
                        oq[child.value] = ObservedQuantitiesValueType.vector
                    elif child.value in tensors:
                        oq[child.value] = ObservedQuantitiesValueType.tensor
                    else:
                        oq[child.value] = ObservedQuantitiesValueType.scalar
                data["observed_quantities"] = oq
            except LookupError:
                pass
            self.active_processes["flow_equation"] = data
        if "solute_equation" in problem_node.children_keys:
            try:
                node = problem_node.get_node_at_path('solute_equation/output_stream/file')
                data["output_stream_file"] = node.value
            except LookupError:
                pass
            try:
                oq = {}
                node = problem_node.get_node_at_path('solute_equation/substances')
                for child in node.children:
                    oq[child.value + "_conc"] = ObservedQuantitiesValueType.scalar
                data["observed_quantities"] = oq
            except LookupError:
                pass
            self.active_processes["solute_equation"] = data
        if "heat_equation" in problem_node.children_keys:
            try:
                node = problem_node.get_node_at_path('heat_equation/output_stream/file')
                data["output_stream_file"] = node.value
            except LookupError:
                pass
            try:
                oq = {}
                oq["temperature"] = ObservedQuantitiesValueType.scalar
                data["observed_quantities"] = oq
            except LookupError:
                pass
            self.active_processes["heat_equation"] = data

        # params
        self.params = sorted(list(set(RE_PARAM.findall(document))))

        # regions
        mesh_dict = {}
        mesh_file_path = os.path.join(dir_name, os.path.normpath(self.mesh_file))
        try:
            with open(mesh_file_path, 'r') as file_d:
                line = file_d.readline()
                while (len(line) > 0) and (line.split()[0] != "$PhysicalNames"):
                    line = file_d.readline()
                line = file_d.readline()
                if len(line) > 0:
                    for i in range(int(line)):
                        s = file_d.readline().split()
                        mesh_dict[s[2][1:-1]] = s[1]
        except (RuntimeError, IOError) as e:
            err.append("Can't open mesh file: {0}".format(e))
            return err
        self.regions = sorted(list(mesh_dict.keys()))

        # .yaml file hash
        e, self.yaml_file_hash = self.file_hash(file)
        err.extend(e)

        # mesh file hash
        e, self.mesh_file_hash = self.file_hash(mesh_file_path)
        err.extend(e)

        return err
