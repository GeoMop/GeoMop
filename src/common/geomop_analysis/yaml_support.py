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
        try:
            node = root.get_node_at_path('/problem/mesh/mesh_file')
            self._mesh_file = node.value
        except LookupError:
            err.append("Can't find node '/problem/mesh/mesh_file'")
            return err

        # active processes
        self._active_processes = {}
        try:
            problem_node = root.get_node_at_path('/problem')
        except LookupError:
            err.append("Can't find node '/problem'")
            return err

        # flow equation
        if "flow_equation" in problem_node.children_keys:
            data = {}

            # output stream file
            try:
                node = problem_node.get_node_at_path('flow_equation/output_stream/file')
                data["output_stream_file"] = node.value
            except LookupError:
                pass

            # observed quantities
            try:
                oq = {}
                node = problem_node.get_node_at_path('flow_equation/output/observe_fields')
                for child in node.children:
                    oq[child.value] = ObservedQuantitiesValueType.scalar
                data["observed_quantities"] = oq
            except LookupError:
                pass

            # balance file
            try:
                node = problem_node.get_node_at_path('flow_equation/balance/file')
                data["balance_file"] = node.value
            except LookupError:
                data["balance_file"] = "water_balance.txt"
            self._active_processes["flow_equation"] = data

        # solute equation
        if "solute_equation" in problem_node.children_keys:
            data = {}

            # output stream file
            try:
                node = problem_node.get_node_at_path('solute_equation/output_stream/file')
                data["output_stream_file"] = node.value
            except LookupError:
                pass

            # observed quantities
            oq = {}
            try:
                node = problem_node.get_node_at_path('solute_equation/transport/output/observe_fields')
                for child in node.children:
                    oq[child.value] = ObservedQuantitiesValueType.scalar
            except LookupError:
                pass
            try:
                node = problem_node.get_node_at_path('solute_equation/reaction/output/observe_fields')
                for child in node.children:
                    oq[child.value] = ObservedQuantitiesValueType.scalar
            except LookupError:
                pass
            try:
                node = problem_node.get_node_at_path('solute_equation/reaction/reaction_mobile/output/observe_fields')
                for child in node.children:
                    oq[child.value] = ObservedQuantitiesValueType.scalar
            except LookupError:
                pass
            try:
                node = problem_node.get_node_at_path('solute_equation/reaction/reaction_immobile/output/observe_fields')
                for child in node.children:
                    oq[child.value] = ObservedQuantitiesValueType.scalar
            except LookupError:
                pass
            if len(oq) > 0:
                data["observed_quantities"] = oq

            # balance file
            try:
                node = problem_node.get_node_at_path('solute_equation/balance/file')
                data["balance_file"] = node.value
            except LookupError:
                data["balance_file"] = "mass_balance.txt"

            # substances
            sub = []
            try:
                node = problem_node.get_node_at_path('solute_equation/substances')
                for child in node.children:
                    name = child.get_child("name")
                    if name is not None:
                        sub.append(name.value)
            except LookupError:
                pass
            data["substances"] = sub

            self._active_processes["solute_equation"] = data

        # heat equation
        if "heat_equation" in problem_node.children_keys:
            data = {}

            # output stream file
            try:
                node = problem_node.get_node_at_path('heat_equation/output_stream/file')
                data["output_stream_file"] = node.value
            except LookupError:
                pass

            # observed quantities
            try:
                oq = {}
                node = problem_node.get_node_at_path('heat_equation/output/observe_fields')
                for child in node.children:
                    oq[child.value] = ObservedQuantitiesValueType.scalar
                data["observed_quantities"] = oq
            except LookupError:
                pass

            # balance file
            try:
                node = problem_node.get_node_at_path('heat_equation/balance/file')
                data["balance_file"] = node.value
            except LookupError:
                data["balance_file"] = "energy_balance.txt"

            self._active_processes["heat_equation"] = data

        # params
        self._params = sorted(list(set(RE_PARAM.findall(document))))

        # regions
        mesh_dict = {}
        mesh_file_path = os.path.join(dir_name, os.path.normpath(self._mesh_file))
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

        self._regions = list(mesh_dict.keys())
        self._regions.append(".IMPLICIT_BOUNDARY")
        self._regions.append("ALL")
        self._regions.sort()

        # .yaml file hash
        e, self._yaml_file_hash = self.file_hash(file)
        err.extend(e)

        # mesh file hash
        e, self._mesh_file_hash = self.file_hash(mesh_file_path)
        err.extend(e)

        return err
