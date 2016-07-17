from .action_types import ParametrizedActionType, Runner, QueueType,  ActionStateType
from .data_types_tree import Struct, String

from geomop_analysis import YamlSupport
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
            
    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._output = self.__file_output()
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()

        # TODO: update testing and remove next two lines
        self._hash.update(bytes(self._variables['YAMLFile'], "utf-8"))
        return

        # add .yaml file to hash
        err = []
        yaml_file = self._variables['YAMLFile']
        document = ""
        try:
            try:
                with codecs.open(yaml_file, 'r', 'utf-8') as file_d:
                    document = file_d.read().expandtabs(tabsize=2)
            except UnicodeDecodeError:
                with open(yaml_file, 'r') as file_d:
                    document = file_d.read().expandtabs(tabsize=2)
        except (RuntimeError, IOError) as e:
            err.append("Can't open .yaml file: {0}".format(e))
            return
        self._hash.update(bytes(document, "utf-8"))

        # add mesh file to hash
        ys = YamlSupport()
        err.extend(ys.parse(yaml_file))
        mesh_file = os.path.join(os.path.dirname(yaml_file),
                                 os.path.normpath(ys.get_mesh_file()))
        try:
            with open(self.mesh_file, 'r') as file_d:
                for line in file_d:
                    self._hash.update(bytes(line, "utf-8"))
        except (RuntimeError, IOError) as e:
            err.append("Can't open mesh file: {0}".format(e))
            return
        # TODO: handle errors

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
        runner.command = ["flow123d", params[0]]
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
                if not hasattr(self._inputs[0],  param) :
                    self._add_error(err, "Yaml parameter {0} is not set in input".format(param))
        return err
        
    def __get_require_params(self):
        """Return list of params needed for completation of Yaml file"""
        #ys = YamlSupport()
        #ys.parse(self._variables['YAMLFile'])
        return []#ys.get_params()
        
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
        #replace_params_in_file(file, new_file, params)

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
