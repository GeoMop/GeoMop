import codecs
import os
import re

from flow_util import YamlSupportRemote, ObservedQuantitiesValueType
from model_data import Loader, Validator, notification_handler, get_root_input_type_from_json

RE_PARAM = re.compile('<([a-zA-Z][a-zA-Z0-9_]*)>')


class YamlSupportLocal(YamlSupportRemote):
    """
    Class for extract regions, params, active processes
    and mesh file from .yaml files.
    """

    def __init__(self):
        super().__init__()

    def _get_root_input_type(self):
        """Returns root input type."""
        curr_format_file = "2.0.0"
        #file_name = os.path.join("resources", "ist", curr_format_file + ".json")
        #file_name = r"d:\geomop\analysis\GeoMop\src\common\resources\ist\2.0.0.json"
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "resources", "ist", curr_format_file + ".json")
        try:
            with open(file_name, 'r') as file_d:
                text = file_d.read()
        except (RuntimeError, IOError) as err:
                cls._report_error("Can't open format file '" + cls.curr_format_file + "'", err)
        try:
            root_input_type = get_root_input_type_from_json(text)
        except Exception as e:
            cls._report_error("Can't open format file", e)
        return root_input_type

    def _get_value_type(self, input_type, value):
        """Returns observed quantities value type."""
        ret = None
        fvs = input_type["values"][value]["attributes"]["field_value_shape"]
        if fvs["type"] == "Integer" and fvs["shape"] == [1, 1]:
            ret = ObservedQuantitiesValueType.integer
        elif fvs["type"] == "Double" and fvs["shape"] == [1, 1]:
            ret = ObservedQuantitiesValueType.scalar
        elif fvs["type"] == "Double" and fvs["shape"] == [3, 1]:
            ret = ObservedQuantitiesValueType.vector
        elif fvs["type"] == "Double" and fvs["shape"] == [3, 3]:
            ret = ObservedQuantitiesValueType.tensor
        return ret

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
        nh = notification_handler # smazat
        loader = Loader(notification_handler)
        validator = Validator(notification_handler)
        notification_handler.clear()
        root = loader.load(document)
        root_input_type = self._get_root_input_type()
        validator.validate(root, root_input_type)

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
                    vt = self._get_value_type(child.input_type, child.value)
                    oq[child.value] = vt
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
                    vt = self._get_value_type(child.input_type, child.value)
                    oq[child.value] = vt
            except LookupError:
                pass
            try:
                node = problem_node.get_node_at_path('solute_equation/reaction/output/observe_fields')
                for child in node.children:
                    vt = self._get_value_type(child.input_type, child.value)
                    oq[child.value] = vt
            except LookupError:
                pass
            try:
                node = problem_node.get_node_at_path('solute_equation/reaction/reaction_mobile/output/observe_fields')
                for child in node.children:
                    vt = self._get_value_type(child.input_type, child.value)
                    oq[child.value] = vt
            except LookupError:
                pass
            try:
                node = problem_node.get_node_at_path('solute_equation/reaction/reaction_immobile/output/observe_fields')
                for child in node.children:
                    vt = self._get_value_type(child.input_type, child.value)
                    oq[child.value] = vt
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
                    vt = self._get_value_type(child.input_type, child.value)
                    oq[child.value] = vt
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
