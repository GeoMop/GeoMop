from .action_types import ParametrizedActionType, Runner, QueueType,  ActionStateType
from .data_types_tree import Struct, String

from flow_util import YamlSupportRemote, analysis
from .flow_data_types import *

import os
import shutil
import codecs
from math import *

class Flow123dAction(ParametrizedActionType):
    
    name = "Flow123d"
    """Display name of action"""
    description = "Flow123d"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
        :param string YAMLFile: path to Yaml file
        :param action or DTT Input: action DTT variable
        """
        super(Flow123dAction, self).__init__(**kwargs)
        self._logical_queue = QueueType.external
        #self._file_output = self.__file_output()
        self._yaml_support = YamlSupportRemote()

    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._output = self.__file_output()
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()

        # check if YAML file exist
        yaml_file = self._variables['YAMLFile']
        if not os.path.isfile(yaml_file):
            self._add_error(self._load_errs, "YAML file don't exist.")
            return

        # check if support file exist
        dir, name = os.path.split(yaml_file)
        s = name.rsplit(sep=".", maxsplit=1)
        new_name = s[0] + ".sprt"
        sprt_file = os.path.join(dir, new_name)
        if not os.path.isfile(sprt_file):
            self._add_error(self._load_errs, "Support file don't exist.")
            return

        # load support file
        err = self._yaml_support.load(sprt_file)
        if len(err) > 0:
            self._extend_error(self._load_errs, err)
            return

        # check if mesh file exist
        mesh_file = self._yaml_support.get_mesh_file()
        mesh_file_path = os.path.join(dir, os.path.normpath(mesh_file))
        if not os.path.isfile(mesh_file_path):
            self._add_error(self._load_errs, "Mesh file don't exist.")
            return

        # check hash consistency
        err, yaml_file_hash_real = YamlSupportRemote.file_hash(yaml_file)
        if len(err) > 0:
            self._extend_error(self._load_errs, err)
            return
        if self._yaml_support.get_yaml_file_hash() != yaml_file_hash_real:
            self._add_error(self._load_errs, "YAML file hash is inconsistent.")

        err, mesh_file_hash_real = YamlSupportRemote.file_hash(mesh_file_path)
        if len(err) > 0:
            self._extend_error(self._load_errs, err)
            return
        if self._yaml_support.get_mesh_file_hash() != mesh_file_hash_real:
            self._add_error(self._load_errs, "Mesh file hash is inconsistent.")

        # process file hashes
        self._hash.update(bytes(self._yaml_support.get_yaml_file_hash(), "utf-8"))
        self._hash.update(bytes(self._yaml_support.get_mesh_file_hash(), "utf-8"))

        self._output = self.__file_output()

    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(Flow123dAction, self)._get_variables_script()
        var.append(["YAMLFile='{0}'".format(self._variables["YAMLFile"])])
        return var

    def _get_runner(self, params):    
        """
        return Runner class with process description
        """
        runner = Runner(self)
        runner.name = self._get_instance_name()
        yaml_file = params[0]
        output_dir = os.path.join("output", self._store_id)
        runner.command = ["flow123d", "-s", yaml_file, "-o", output_dir]
        runner.input_files = [yaml_file, self._yaml_support.get_mesh_file()]
        runner.output_files = [output_dir]
        return runner
        
    def _update(self):    
        """
        Process action on client site and return None or prepare process 
        environment and return Runner class with  process description if 
        action is set for externall processing.        
        """
        # todo: remove output files
        shutil.rmtree(os.path.join("output", self._store_id), ignore_errors=True)
        file = self.__parametrise_file()
        return self._get_runner([file])
        
    def _after_update(self, store_dir):    
        """
        Set real output variable and set finished state.
        """

        self._output = self.__file_result()
        self._store_results(store_dir)
        self._state = ActionStateType.finished

    def _check_params(self):    
        """check if all require params is set"""
        err = super(Flow123dAction, self)._check_params()
        if 'YAMLFile' not in self._variables:
            self._add_error(err, "Flow123d action require YAMLFile parameter")
        if self._output is None:
            self._add_error(err, "Can't determine output from YAML file")
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(Flow123dAction, self).validate()
        input_type = self.get_input_val(0)
        if input_type is None:
            self._add_error(err, "Can't validate input (Output slot of input action is empty)")
        else:
            if not isinstance(input_type, Struct):
                self._add_error(err, "Flow123d input parameter must return Struct")
            params =  self.__get_require_params()
            for param in params:
                if not hasattr(input_type, param):
                    self._add_error(err, "Yaml parameter {0} is not set in input".format(param))
        return err
        
    def __get_require_params(self):
        """Return list of params needed for completation of Yaml file"""
        return self._yaml_support.get_params()
        
    def __file_output(self):
        """Return DTT output structure from Yaml file"""
        return FlowOutputType.create_type(self._yaml_support)

    def __file_result(self):
        """Add to DTT output real values from returned file"""
        # TODO: exception if fail
        ret = FlowOutputType.create_data(self._yaml_support, os.path.join("output", self._store_id))
        #shutil.rmtree(os.path.join("output", self._store_id), ignore_errors=True)
        return ret

    def __parametrise_file(self):
        """Rename and make completation of Yaml file and return new file path"""

        # new name
        file = self._variables['YAMLFile']
        dir, name = os.path.split(file)
        s = name.rsplit(sep=".", maxsplit=1)
        new_name = s[0] + "_" + self._store_id
        if len(s) == 2:
            new_name += "." + s[1]
        new_file = os.path.join(dir, new_name)

        # completion
        input = self.get_input_val(0)
        params_dict = {}
        for param in self.__get_require_params():
            params_dict[param] = getattr(input, param)._to_string()
        analysis.replace_params_in_file(file, new_file, params_dict)

        return new_file

    def _store(self, path):
        """
        make all needed serialization processess and
        return text data for storing
        """
        res = ""

        return res

    def _restore(self, text, path):
        """
        make all needed deserialization processess and
        return text data for storing
        
        if result file  in not pressented, throw exception
        """

        self._output = self.__file_result()

    def get_resources(self):
        """Return list of resource files"""
        d = {"name": self.name,
             "YAMLFile": self._variables['YAMLFile']}
        return [d]


class FunctionAction(ParametrizedActionType):

    name = "Function"
    """Display name of action"""
    description = "Function"
    """Display description of action"""

    def __init__(self, **kwargs):
        """
        :param list of str Params: input parameters
            example:
            ["x1", "x2", "x3"]
        :param list of srt Expressions: function prescription
            example:
            ["y1 = 1 * x1 + 2 * x2", "y2 = 3 * x1 + 4 * x2", "y3 = sin(x3)"]
        :param action or DTT Input: action DTT variable
        """
        super().__init__(**kwargs)

    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()

        # add params and Expression to hash
        if 'Params' in self._variables and \
                isinstance(self._variables['Params'], list):
            for par in self._variables['Params']:
                self._hash.update(bytes(par, "utf-8"))
        if 'Expressions' in self._variables and \
                isinstance(self._variables['Expressions'], list):
            for ex in self._variables['Expressions']:
                self._hash.update(bytes(ex, "utf-8"))

        self._output = self.__func_output()

    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super()._get_variables_script()
        lines = self._format_array("Params", self._variables["Params"], 0, "Unknown type")
        lines[-1] = lines[-1][:-1]
        var.append(lines)
        lines = self._format_array("Expressions", self._variables["Expressions"], 0, "Unknown type")
        lines[-1] = lines[-1][:-1]
        var.append(lines)
        return var

    def _update(self):
        """
        Process action on client site and return None or prepare process
        environment and return Runner class with  process description if
        action is set for externall processing.
        """
        self._output = self.__func_result()
        return None

    def _check_params(self):
        """check if all require params is set"""
        err = super()._check_params()
        if 'Params' in self._variables:
            if isinstance(self._variables['Params'], list):
                for par in self._variables['Params']:
                    if not isinstance(par, str):
                        self._add_error(err, "Parameter Params must be list of str")
            else:
                self._add_error(err, "Parameter Params must be list")
        else:
            self._add_error(err, "Function action require Params parameter")
        if 'Expressions' in self._variables:
            if isinstance(self._variables['Expressions'], list):
                for par in self._variables['Expressions']:
                    if not isinstance(par, str):
                        self._add_error(err, "Parameter Expressions must be list of str")
            else:
                self._add_error(err, "Parameter Expressions must be list")
        else:
            self._add_error(err, "Function action require Expressions parameter")
        if self._output is None:
            self._add_error(err, "Can't determine output from function prescription")
        return err

    def validate(self):
        """validate variables, input and output"""
        err = super().validate()
        input_type = self.get_input_val(0)
        if input_type is None:
            self._add_error(err, "Can't validate input (Output slot of input action is empty)")
        else:
            if not isinstance(input_type, Struct):
                self._add_error(err, "Function input parameter must return Struct")
            params = self.__get_require_params()
            for param in params:
                if hasattr(input_type, param):
                    if not isinstance(getattr(input_type, param), Float):
                        self._add_error(err, "Function parameter {0} is not Float".format(param))
                else:
                    self._add_error(err, "Function parameter {0} is not set in input".format(param))
        return err

    def __get_require_params(self):
        """Return list of params needed for function evaluation"""
        params = []
        if 'Params' in self._variables and \
                isinstance(self._variables['Params'], list):
            for par in self._variables['Params']:
                if isinstance(par, str):
                    params.append(par)
        return params

    def __parse_expressions(self):
        """Split expression to output variables and right side of expression"""
        ret = []
        if 'Expressions' in self._variables and \
                isinstance(self._variables['Expressions'], list):
            for expression in self._variables['Expressions']:
                if isinstance(expression, str):
                    s = expression.split("=", maxsplit=1)
                    if len(s) < 2:
                        continue
                    var = s[0].strip()
                    ex = s[1].strip()
                    if len(var) > 0 and len(ex) > 0:
                        ret.append((var, ex))
        return ret

    def __func_output(self):
        """Return DTT output structure from function prescription"""
        output = Struct()
        for v, e in self.__parse_expressions():
            setattr(output, v, Float())
        return output

    def __func_result(self):
        """Add to DTT output real values from function evaluation"""
        input = self.get_input_val(0)
        loc = {}
        for par in self.__get_require_params():
            loc[par] = getattr(input, par).value
        output = Struct()
        for v, e in self.__parse_expressions():
            res = eval(e, globals(), loc)
            setattr(output, v, Float(float(res)))
        return output
