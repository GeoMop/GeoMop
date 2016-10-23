from .action_types import OutputActionType, ActionStateType
from .data_types_tree import DTT


class PrintDTTAction(OutputActionType):
    name = "PrintDTT"
    """Display name of action"""
    description = "PrintDTT"
    """Display description of action"""

    def __init__(self, **kwargs):
        """
        :param string OutputFile: path to output file
        :param action or DTT Input: action DTT variable
        """
        super().__init__(**kwargs)

    def _inicialize(self):
        """inicialize action run variables"""
        if self._get_state().value > ActionStateType.created.value:
            return
        self._set_state(ActionStateType.initialized)
        self._process_base_hash()

        # add output file name to hash
        if 'OutputFile' in self._variables and \
                isinstance(self._variables['OutputFile'], str):
            self._hash.update(bytes(self._variables['OutputFile'], "utf-8"))

    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super()._get_variables_script()
        var.append(["OutputFile='{0}'".format(self._variables["OutputFile"])])
        return var

    def _update(self):
        """
        Process action on client site and return None or prepare process
        environment and return Runner class with  process description if
        action is set for externall processing.
        """
        err = []
        try:
            with open(self._variables['OutputFile'], 'w') as fd:
                input = self.get_input_val(0)
                fd.write("\n".join(input._get_settings_script()))
        except Exception as e:
            err.append("Output file saving error: {0}".format(e))
        # ToDo: process errors
        return None

    def _check_params(self):
        """check if all require params is set"""
        err = super()._check_params()
        if 'OutputFile' not in self._variables:
            self._add_error(err, "PrintDTT action require OutputFile parameter")
        return err

    def validate(self):
        """validate variables, input and output"""
        err = super().validate()
        input_type = self.get_input_val(0)
        if input_type is None:
            self._add_error(err, "Can't validate input (Output slot of input action is empty)")
        else:
            if not isinstance(input_type, DTT):
                self._add_error(err, "PrintDTT input parameter must return DTT")
        return err
