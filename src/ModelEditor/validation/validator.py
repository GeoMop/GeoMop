"""Validator for Flow123D data structure"""

from validation import errors, checks
import data.data_node as dn


class Validator:
    SCALAR = ['Integer', 'Double', 'Bool', 'String', 'Selection', 'FileName']

    @property
    def errors(self):
        return tuple(self._errors)

    @property
    def console_log(self):
        out = ('VALID' if self.valid else 'INVALID')
        for path, error in sorted(self._errors, key=(lambda item: item[0])):
            out = out + '\n' + path + ': ' + str(error)
        return out

    # TODO decouple node and input_type!
    def validate(self, node, input_type):
        """
        Performs data validation of node with the specified input_type.

        Validation is performed recursively on all children nodes as well.

        Returns True when all data was correctly validated, False otherwise.
        Attribute errors contains a list of occurred errors.
        """
        self._errors = []
        self.valid = True
        self._validate_node(node, input_type)
        self._errors = self._errors
        return self.valid

    def _validate_node(self, node, input_type):
        """
        Determines if node contains correct value.

        Method verifies node recursively. All descendant nodes are checked.
        """
        if node.ref is not None:
            # TODO implement validation of references
            raise NotImplementedError

        if input_type['base_type'] in Validator.SCALAR:
            self._validate_scalar(node, input_type)
        elif input_type['base_type'] == 'Record':
            self._validate_record(node, input_type)
        elif input_type['base_type'] == 'AbstractRecord':
            self._validate_abstract(node, input_type)
        elif input_type['base_type'] == 'Array':
            self._validate_array(node, input_type)
        else:
            self._report_error(
                node,
                errors.ValidationError(
                    ("Format error: Unknown input_type {input_type})"
                        .format(input_type=input_type['base_type']))))

    def _validate_scalar(self, node, input_type):
        try:
            checks.check_scalar(node, input_type)
        except errors.ValidationError as error:
            self._report_error(node, error)

    def _validate_record(self, node, input_type):
        if not isinstance(node, dn.CompositeNode) or not node.explicit_keys:
            self._report_error(node, errors.ValidationError("Expecting type Record"))
            return
        keys = node.children_keys
        keys.extend(input_type['keys'].keys())
        for key in set(keys):
            child = node.get_child(key)
            try:
                checks.check_record_key(node.children_keys, key, input_type)
            except errors.ValidationError as error:
                self._report_error(node, error)
                if isinstance(error, errors.UnknownKey):
                    continue
            else:
                if child is not None:
                    child_input_type = input_type['keys'][key]['type']
                    self._validate_node(child, child_input_type)

    def _validate_abstract(self, node, input_type):
        raise NotImplementedError
        # node = self.root_node.get(path)
        # try:
        #     record_its = checks.get_abstractrecord_type(node.value, its)
        # except errors.ValidationError as error:
        #     self._report_error(path, error)
        # else:
        #     self._validate_record(path, record_its)

    def _validate_array(self, node, input_type):
        if not isinstance(node, dn.CompositeNode) or node.explicit_keys:
            self._report_error(node, errors.ValidationError("Expecting type Array"))
            return
        try:
            checks.check_array(node.children, input_type)
        except errors.ValidationError as error:
            self._report_error(node, error)
        for child in node.children:
            self._validate_node(child, input_type['subtype'])

    def __init__(self):
        self.valid = True
        self._errors = []

    def _report_error(self, node, error):
        """
        Report an error.
        """
        self.valid = False
        self._errors.append((node, error))


