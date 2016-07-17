import json
import codecs
import os
import re

from model_data import Loader, Validator, notification_handler

RE_PARAM = re.compile('<([a-zA-Z][a-zA-Z0-9_]*)>')


class YamlSupport:
    """
    Class for extract regions, params, active processes
    and mesh file from .yaml files.
    """

    def __init__(self):
        self.regions = {}
        self.params = []
        self.active_processes = []
        self.mesh_file = ""

    def parse(self, file):
        """Parse regions, params and active processes from .yaml file."""
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

        node = root.get_node_at_path('/problem/mesh/mesh_file')
        self.mesh_file = node.value

        node = root.get_node_at_path('/problem')
        ap = {"flow_equation", "solute_equation", "heat_equation"}
        self.active_processes = list(set(node.children_keys).intersection(ap))

        self.params = list(set(RE_PARAM.findall(document)))

        mesh_dict = {}
        try:
            with open(os.path.join(dir_name, os.path.normpath(self.mesh_file)), 'r') as file_d:
                line = file_d.readline()
                while (len(line) > 0) and (line.split()[0] != "$PhysicalNames"):
                    line = file_d.readline()
                line = file_d.readline()
                if len(line) > 0:
                    for i in range(int(line)):
                        s = file_d.readline().split()
                        mesh_dict[s[2]] = s[1]
        except (RuntimeError, IOError) as e:
            err.append("Can't open mesh file: {0}".format(e))
            return err
        self.regions = mesh_dict

        return err

    def get_regions(self):
        """Return regions."""
        return self.regions.copy()

    def get_params(self):
        """Return params."""
        return self.params.copy()

    def get_active_processes(self):
        """Return active processes."""
        return self.active_processes.copy()

    def get_mesh_file(self):
        """Return mesh file."""
        return self.mesh_file

    def save(self, file):
        """Save data to file."""
        err = []
        try:
            with open(file, 'w') as fd:
                d = dict(regions=self.regions, params=self.params,
                         active_processes=self.active_processes,
                         mesh_file=self.mesh_file)
                json.dump(d, fd, indent=4, sort_keys=True)
        except Exception as e:
            err.append("YamlSupport saving error: {0}".format(e))
        return err

    def load(self, file):
        """Load data form file."""
        err = []
        try:
            with open(file, 'r') as fd:
                d = json.load(fd)

                self.regions = d["regions"] if "regions" in d else {}
                self.params = d["params"] if "params" in d else []
                self.active_processes = d["active_processes"] if "active_processes" in d else []
                self.mesh_file = d["mesh_file"] if "mesh_file" in d else ""
        except Exception as e:
            err.append("YamlSupport loading error: {0}".format(e))
        return err
