"""Tests for autocomplete helper.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import pytest
from helpers import AutocompleteHelper, AutocompleteContext


class TestAutocompleteHelper:
    """Tests the AutocompleteHelper class."""

    input_type_record = {
        'base_type': 'Record',
        'keys': {
            'regions': None,
            'mesh_file': None,
            'sets': None
        }
    }

    input_type_selection = {
        'base_type': 'Selection',
        'values': {
            'PETSc': None,
            'METIS': None
        }
    }

    input_type_abstract_record = {
        'base_type': 'AbstractRecord',
        'implementations': {
            'Steady_MH': None,
            'Unsteady_MH': None,
            'Unsteady_LMH': None
        }
    }

    @pytest.fixture(autouse=True)
    def setup_achelper(self):
        """Set up a fresh AutocompleteHelper for each test."""
        self.achelper = AutocompleteHelper()

    def test_record_options(self):
        """Test if record keys are added to options."""
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert len(options) == 3
        assert 'regions' in options
        assert 'mesh_file' in options
        assert 'sets' in options

    def test_get_autocompletion_key(self):
        """Key should end with ': '."""
        self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        text = self.achelper.get_autocompletion('regions')
        assert text == 'regions: '

    def test_anchors(self):
        """Test adding and clearing anchors."""
        self.achelper.register_anchor('anchor1')
        self.achelper.register_anchor('anchor2')
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert len(options) == 5
        assert '*anchor1' in options
        assert '*anchor2' in options

    def test_get_autocompletion_anchor(self):
        """Anchor should begin with '*'."""
        self.achelper.register_anchor('anchor1')
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert self.achelper.get_autocompletion(options[3]) == '*anchor1'

    def test_get_autocompletion_selection(self):
        """Test if selection option are correct."""
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_selection)
        assert len(options) == 2
        assert 'PETSc' in options
        assert 'METIS' in options
        assert self.achelper.get_autocompletion('PETSc') == 'PETSc'

    def test_get_autocompletion_abstract_record(self):
        """Test if types are listed as AbstractRecord options."""
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_abstract_record)
        assert len(options) == 3
        assert '!Steady_MH' in options
        assert '!Unsteady_MH' in options
        assert '!Unsteady_LMH' in options
        assert self.achelper.get_autocompletion('!Steady_MH') == '!Steady_MH'

    def test_scintilla_options(self):
        """Test if QSci options are generated correctly."""
        self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert self.achelper.scintilla_options.decode('utf-8') == 'mesh_file regions sets'

    def test_show_autocompletion(self):
        self.achelper.create_options(TestAutocompleteHelper.input_type_abstract_record)
        context = AutocompleteContext('!Uns', 2)
        options = self.achelper.show_autocompletion(context)
        assert self.achelper.visible is True
        assert options.decode('utf-8') == '!Unsteady_LMH !Unsteady_MH'
        self.achelper.visible = False
        context = AutocompleteContext('!X', 2)
        assert self.achelper.show_autocompletion(context) is None
        assert self.achelper.visible is False

    def test_hide_autocompletion(self):
        self.achelper.create_options(TestAutocompleteHelper.input_type_abstract_record)
        context = AutocompleteContext('!Uns', 2)
        self.achelper.show_autocompletion(context)
        self.achelper.hide_autocompletion()
        assert self.achelper.visible is False

    def test_refresh_autocompletion(self):
        self.achelper.create_options(TestAutocompleteHelper.input_type_abstract_record)
        context = AutocompleteContext('!Uns', 2)
        assert self.achelper.visible is False
        assert self.achelper.refresh_autocompletion(context) is None
        options = self.achelper.show_autocompletion(context)
        assert self.achelper.visible is True
        assert options.decode('utf-8') == '!Unsteady_LMH !Unsteady_MH'
        context = AutocompleteContext('!Unsteady_L', 11)
        options = self.achelper.refresh_autocompletion(context)
        assert options.decode('utf-8') == '!Unsteady_LMH'
        assert self.achelper.visible is True
        context = AutocompleteContext('!Unsteady_X', 11)
        options = self.achelper.refresh_autocompletion(context)
        assert options is None
        assert self.achelper.visible is False


def test_autocomplete_context():
    assert AutocompleteContext('value', 3).hint == 'val'
    assert AutocompleteContext('key: ', 0).hint == ''
    assert AutocompleteContext('key: ', 2).hint == 'ke'
    assert AutocompleteContext('*anchor', 7).hint == '*anchor'
    assert AutocompleteContext('!tag', 1).hint == '!'
