"""Module for handling autocomplete in editor."""

__author__ = 'Tomas Krizek'


class AutocompleteHelper:
    """Helper class for creating and managing autocomplete options in editor."""

    def __init__(self):
        """Initializes the class."""
        self._options = {}

    def create_options(self, input_type, prev_char=''):
        """
        Creates a list of options based on the input type and previous character in editor.
        Each option is identified by a string.

        Returns a list of string (option identifiers) that should be displayed as QScintilla
        autocomplete options.
        """
        self._options.clear()
        if input_type['base_type'] == 'Record':
            # create options from keys
            self._options.update({key['key']: 'key' for key in input_type['keys']})
        return self.options

    def select_option(self, option_string):
        """
        Selects an option based on the option_string returned from QScintilla API.

        Returns a string that should be inserted into the editor. This string can differ from
        `option_string` for a better user experience.(For example, a record key would be identified
        by its name, but the returned string would also contain ': ' at the end.
        """
        if option_string not in self._options:
            return ''
        type_ = self._options[option_string]
        if type_ == 'key':
            return option_string + ': '
        else:
            return option_string

    def register_anchor(self, anchor_name):
        """Registers an anchor by its name."""
        pass

    def clear_anchors(self):
        """Clears the anchor list."""
        pass

    @property
    def options(self):
        """Returns the QScintilla options."""
        return self._options.keys()
