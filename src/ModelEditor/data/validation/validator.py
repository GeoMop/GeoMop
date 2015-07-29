"""Validator for Flow123D data structure"""

from data.validation import errors, checks
import data.data_node as dn
from data.data_node import DataError


class Validator:
    """Handles data structure validation."""
    SCALAR = ['Integer', 'Double', 'Bool', 'String', 'Selection', 'FileName']

    def __init__(self, error_handler):
        """Initializes the validator with an ErrorHandler."""
        self.error_handler = error_handler
        self.valid = True

    def validate(self, node, input_type):
        """
        Performs data validation of node with the specified input_type.

        Validation is performed recursively on all children nodes as well.
        Options are added to nodes where applicable (record keys, selection, ...).

        Returns True when all data was correctly validated, False otherwise.
        Attribute errors contains a list of occurred errors.
        """
        self.valid = True
        self._validate_node(node, input_type)
        return self.valid

    def _validate_node(self, node, input_type):
        """
        Determines if node contains correct value.

        Method verifies node recursively. All descendant nodes are checked.
        """
        if node is None:
            raise errors.ValidationError("Invalid node (None)")

        if input_type['base_type'] in Validator.SCALAR:
            self._validate_scalar(node, input_type)
        elif input_type['base_type'] == 'Record':
            self._validate_record(node, input_type)
        elif input_type['base_type'] == 'AbstractRecord':
            self._validate_abstract(node, input_type)
        elif input_type['base_type'] == 'Array':
            self._validate_array(node, input_type)
        else:
            message = "Format error: Unknown input_type {input_type})"
            message = message.format(input_type=input_type['base_type'])
            error = errors.ValidationError(message)
            self._report_error(message, error)

    def _validate_scalar(self, node, input_type):
        if input_type['base_type'] == 'Selection':
            node.options = input_type['values']
        try:
            checks.check_scalar(node, input_type)
        except errors.ValidationError as error:
            self._report_error(node, error)

    def _validate_record(self, node, input_type):
        if not isinstance(node, dn.CompositeNode) or not node.explicit_keys:
            self._report_error(node, errors.ValidationTypeError("Expecting type Record"))
            return
        keys = node.children_keys
        node.options = input_type['keys'].keys()
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
        try:
            concrete_type = checks.get_abstractrecord_type(node, input_type)
        except errors.ValidationError as error:
            self._report_error(node, error)
        else:
            self._validate_record(node, concrete_type)

    def _validate_array(self, node, input_type):
        if not isinstance(node, dn.CompositeNode) or node.explicit_keys:
            self._report_error(node, errors.ValidationTypeError("Expecting type Array"))
            return
        try:
            checks.check_array(node.children, input_type)
        except errors.ValidationError as error:
            self._report_error(node, error)
        for child in node.children:
            self._validate_node(child, input_type['subtype'])

    def _report_error(self, node, error):
        """Reports an error."""
        invalidate = self.error_handler.report_validation_error(node, error)
        if invalidate:
            self.valid = False
