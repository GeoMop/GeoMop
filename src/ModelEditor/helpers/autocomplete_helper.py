"""Module for handling autocomplete in editor.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from copy import copy


class AutocompleteHelper:
    """Creates autocomplete options and manages the autocomplete state."""

    def __init__(self):
        """Initialize the class."""
        self._options = {}
        self._anchors = []
        self.scintilla_options = ''
        """the QScintilla options string encoded in utf-8"""
        self.possible_options = []
        """a list of possible options for the current context"""
        self.visible = False
        """whether autocompletion list is displayed"""
        self.context = None
        """:py:class:`AutocompleteContext` for the current word"""

        # define sorting alphabet
        self.sorting_alphabet = list(map(chr, range(48, 57)))  # generate number 0-9
        self.sorting_alphabet.extend(list(map(chr, range(97, 123))))  # generate lowercase alphabet
        self.sorting_alphabet.extend(['!', '*', '_', '-'])

    def create_options(self, input_type):
        """Create a list of options based on the input type.

        Each option is identified by a string that should be displayed as QScintilla
        autocomplete option. Set the autocomplete state to hidden.

        :param dict input_type: specification of the input_type
        :return: string of sorted options separated by a space (for QScintilla API)
        :rtype: str
        """
        prev_options = copy(self._options)
        self._options.clear()

        if input_type['base_type'] == 'Record':  # input type Record
            self._options.update({key: 'key' for key in input_type['keys'] if key != 'TYPE'})
            if 'implemented_abstract_record' in input_type:
                self._options.update({'!' + type_: 'type' for type_ in
                                     input_type['implemented_abstract_record']['implementations']})
        elif input_type['base_type'] == 'Selection':  # input type Selection
            self._options.update({value: 'selection' for value in input_type['values']})
        elif input_type['base_type'] == 'AbstractRecord':  # input typeAbstractRecord
            self._options.update({'!' + type_: 'type' for type_ in
                                  input_type['implementations']})
        elif input_type['base_type'] == 'Bool':  # input tye Bool
            self._options.update({'true': 'bool', 'false': 'bool'})

        # add anchors
        self._options.update({'*' + anchor: 'anchor' for anchor in self._anchors})
        self._prepare_options()

        # if options changed, hide autocomplete
        if sorted(prev_options) != sorted(self._options):
            self.visible = False

        return self.possible_options

    def show_autocompletion(self, context=None):
        """Get autocomplete options for the context.

        If there are some options to be displayed, :py:attr:`visible` is set to True.

        :param AutocompleteContext context: current word and position
        :return: string of sorted options separated by a space
        :rtype: str or ``None``
        """
        self.visible = True
        return self.refresh_autocompletion(context)

    def hide_autocompletion(self):
        """Set the autocompletion state to hidden."""
        self.visible = False

    def refresh_autocompletion(self, context):
        """Refresh possible autocomplete option based on context.

        Do not show any options if the autocomplete is hidden. If there are no
        options, set the autocomplete state to hidden.

        :param AutocompleteContext context: current word and position
        """
        if not self.visible:
            return None
        filter = None
        if context is not None:
            filter = context.hint
        self._prepare_options(filter)
        if len(self.scintilla_options) == 0:
            self.visible = False
            return None
        return self.scintilla_options

    def get_autocompletion(self, option):
        """Get autocompletion string for the selected option.

        Set the autocompletion state to hidden if an option is selected.

        :param str option: option string returned by QScintilla
        :return: an autocompletion string that replaces the word in current context
        :rtype: str
        :raises: ValueError - if option is not one of possible options
        """
        if option not in self.possible_options:
            raise ValueError("Selected autocompletion option is not available.")
        self.visible = False
        type_ = self._options[option]
        if type_ == 'key':
            return option + ': '
        else:
            return option

    def register_anchor(self, anchor_name):
        """Registers an anchor by its name."""
        self._anchors.append(anchor_name)

    def clear_anchors(self):
        """Clears the anchor list."""
        self._anchors.clear()

    def _prepare_options(self, filter=None):
        """Sort filtered options and prepare QScintilla string representation.

        :param str filter: only allow options that starts with this string
        """
        if filter is None:
            filter = ''
        options = [option for option in self._options.keys() if option.startswith(filter)]
        self.possible_options = sorted(options, key=self._sorting_key)

        # if there is only one option and it matches the word exactly, do not show options
        if len(self.possible_options) == 1 and self.possible_options[0] == filter:
            self.possible_options.clear()

        self.scintilla_options = (' '.join(self.possible_options)).encode('utf-8')

    def _sorting_key(self, word):
        """A key for sorting the options."""
        numbers = []
        for letter in word.lower():
            numbers.append(self.sorting_alphabet.index(letter))
        return numbers


class AutocompleteContext:
    """Holds the context information about the word being autocompleted."""

    def __init__(self, word=None, index=None):
        """Initialize the class.

        :param str word: the word being autocompleted
        :param int index: the position of cursor from the beginning of the word
        """
        self.word = word
        """the entire word to be replaced if the autocompletion is triggered"""
        self.index = index
        """the position of cursor from the beginning of the word"""

    @property
    def hint(self):
        """the beginning of the word up to the cursor"""
        if self.word is None or self.index is None:
            return None
        end = self.index
        return self.word[:end]
