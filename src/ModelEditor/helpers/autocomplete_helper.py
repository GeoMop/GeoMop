"""Module for handling autocomplete in editor."""

__author__ = 'Tomas Krizek'


class AutocompleteHelper:
    """Helper class for creating and managing autocomplete options in editor."""

    SPECIAL_CHARS = ['&']

    def __init__(self):
        """Initializes the class."""
        self._options = {}
        self._anchors = []
        self.scintilla_options = ''
        """the QScintilla options string encoded in utf-8"""

    def create_options(self, input_type, prev_char=''):
        """
        Creates a list of options based on the input type and previous character in editor.
        Each option is identified by a string.

        Returns a list of string (option identifiers) that should be displayed as QScintilla
        autocomplete options.
        """
        self._options.clear()

        # TODO: prev_char vs first_char ... &an -> &anchor ?
        if prev_char not in AutocompleteHelper.SPECIAL_CHARS:
            if input_type['base_type'] == 'Record':  # input type Record
                self._options.update({key: 'key' for key in input_type['keys'] if key != 'TYPE'})
            elif input_type['base_type'] == 'Selection':  # input type Selection
                self._options.update({value: 'selection' for value in input_type['values']})
            elif input_type['base_type'] == 'AbstractRecord':  # input typeAbstractRecord
                self._options.update({'!' + type_: 'type' for type_ in
                                      input_type['implementations']})

        elif prev_char == '&':  # add anchors
            self._options.update({'&' + anchor: 'anchor' for anchor in self._anchors})

        self.scintilla_options = (' '.join(sorted(list(self._options.keys())))).encode('utf-8')
        return list(self._options.keys())

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
        self._anchors.append(anchor_name)

    def clear_anchors(self):
        """Clears the anchor list."""
        self._anchors.clear()
