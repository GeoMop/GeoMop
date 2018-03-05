import codecs
import os
import re

from gm_base.flow_util import YamlSupportRemote, ObservedQuantitiesValueType
from model_data import Loader, Validator, notification_handler, get_root_input_type_from_json, autoconvert

RE_PARAM = re.compile('<([a-zA-Z][a-zA-Z0-9_]*)>')


class YamlSupportLocal(YamlSupportRemote):
    """
    Class for extract regions, params, active processes
    and mesh file from .yaml files.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def _get_root_input_type():
        """Returns root input type."""
        curr_format_file = "2.1.0"
        err = []
        #file_name = os.path.join("resources", "ist", curr_format_file + ".json")
        #file_name = r"d:\geomop\analysis\GeoMop\src\common\resources\ist\2.0.0.json"
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "resources", "ist", curr_format_file + ".json")
        try:
            with open(file_name, 'r') as file_d:
                text = file_d.read()
        except (RuntimeError, IOError) as err:
            err.append("Can't open format file '" + curr_format_file + "' (" + str(err) + ")")
        try:
            root_input_type = get_root_input_type_from_json(text)
        except Exception as e:
            err.append("Can't open format file (" + str(e) + ")")
        return root_input_type, err

    @staticmethod
    def _get_value_type(input_type, value):
        """Returns observed quantities value type."""
        fvs = input_type["values"][value]["attributes"]["field_value_shape"]

        # value type
        vt = None
        if fvs["type"] == "Integer" and fvs["shape"] == [1, 1]:
            vt = ObservedQuantitiesValueType.integer
        elif fvs["type"] == "Double" and fvs["shape"] == [1, 1]:
            vt = ObservedQuantitiesValueType.scalar
        elif fvs["type"] == "Double" and fvs["shape"] == [3, 1]:
            vt = ObservedQuantitiesValueType.vector
        elif fvs["type"] == "Double" and fvs["shape"] == [3, 3]:
            vt = ObservedQuantitiesValueType.tensor

        # multifield
        mf = "subfields" in fvs and fvs["subfields"]

        return vt, mf

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
        
        root_input_type, new_err = self._get_root_input_type()
        err.extend(new_err)

        # autoconvert
        root = autoconvert(root, root_input_type)

        # validate
        if not validator.validate(root, root_input_type):
            err.append(".yaml file have not valid format")
            #return err

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
            oq = {}
            oq.update(self._get_observed_quantities(problem_node, 'flow_equation/output/observe_fields'))
            if len(oq) > 0:
                data["observed_quantities"] = oq

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
            oq.update(self._get_observed_quantities(problem_node, 'solute_equation/transport/output/observe_fields'))
            oq.update(self._get_observed_quantities(problem_node, 'solute_equation/reaction/output/observe_fields'))
            oq.update(self._get_observed_quantities(problem_node, 'solute_equation/reaction/reaction_mobile/output/observe_fields'))
            oq.update(self._get_observed_quantities(problem_node, 'solute_equation/reaction/reaction_immobile/output/observe_fields'))
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
            oq = {}
            oq.update(self._get_observed_quantities(problem_node, 'heat_equation/output/observe_fields'))
            if len(oq) > 0:
                data["observed_quantities"] = oq

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

    @classmethod
    def _get_observed_quantities(cls, base_node, path):
        """Returns observed quantities at given path"""
        try:
            node = base_node.get_node_at_path(path)
        except LookupError:
            return {}
        oq = {}
        for child in node.children:
            vt, mf = cls._get_value_type(child.input_type, child.value)
            subfields = []
            if mf:
                n = node
                while n is not None:
                    if n.input_type['base_type'] == 'Record' and "subfields_address" in n.input_type["attributes"]:
                        subfields_address = n.input_type["attributes"]["subfields_address"]
                        subfields = cls._get_subfields_at_path(n, subfields_address)
                        break
                    n = n.parent
            if len(subfields) > 0:
                oq.update({s+"_"+child.value: vt for s in subfields})
            else:
                oq[child.value] = vt
        return oq

    @staticmethod
    def _get_subfields_at_path(base_node, path):
        """Returns subfields"""
        prefix_path, suffix_path = path.split("/*/", 1)
        try:
            prefix_node = base_node.get_node_at_path(prefix_path)
        except LookupError:
            return []
        subfields = []
        for child in prefix_node.children:
            try:
                suffix_node = child.get_node_at_path(suffix_path)
                subfields.append(suffix_node.value)
            except LookupError:
                pass
        return subfields
