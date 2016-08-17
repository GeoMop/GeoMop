from .action_types import ParametrizedActionType, Runner, QueueType,  ActionStateType
from .data_types_tree import Struct, String

from flow_util import YamlSupportRemote, analysis
import os
import codecs

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
        self._file_output = self.__file_output()
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
        runner.command = ["flow123d", "-s", params[0]]
        return runner
        
    def _update(self):    
        """
        Process action on client site and return None or prepare process 
        environment and return Runner class with  process description if 
        action is set for externall processing.        
        """
        file = self.__parametrise_file()
        return  self._get_runner([file])
        
    def _after_update(self, store_dir):    
        """
        Set real output variable and set finished state.
        """
        # TODO read output from files
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
        #ys = YamlSupport()
        #ys.parse(self._variables['YAMLFile'])

        # TODO logic
        return String("Test")

    def __file_result(self,  file):
        """Add to DTT output real values from returned file"""
        # TODO logic
        return String("Test")
        
    def __parametrise_file(self):
        """Rename and make completation of Yaml file and return new file path"""

        # new name
        file = self._variables['YAMLFile']
        dir, name = os.path.split(file)
        s = name.rsplit(sep=".", maxsplit=1)
        new_name = s[0] + "_param"
        if len(s) == 2:
            new_name += "." + s[1]
        new_file = os.path.join(dir, new_name)

        # completion
        input = self.get_input_val(0)
        params_dict = {}
        for param in self.__get_require_params():
            params_dict[param] = getattr(input, param).value
        analysis.replace_params_in_file(file, new_file, params_dict)

        return new_file

    def _store(self, path):
        """
        make all needed serialization processess and
        return text data for storing
        """
        res = ""
        # TODO copy result files to store path and store only files names
        return res

    def _restore(self, text, path):
        """
        make all needed deserialization processess and
        return text data for storing
        
        if result file  in not pressented, throw exception
        """
        # TODO instead next commented line restore files names and make output from it
        # self._output = eval(res)
