"""Tests for autocomplete helper."""

import pytest
from helpers import AutocompleteHelper

__author__ = 'Tomas Krizek'


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

    def test_key_selection(self):
        """Key should end with ': '."""
        self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        text = self.achelper.select_option('regions')
        assert text == 'regions: '

    def test_anchors(self):
        """Test adding and clearing anchors."""
        self.achelper.register_anchor('anchor1')
        self.achelper.register_anchor('anchor2')
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert len(options) == 5
        assert '*anchor1' in options
        assert '*anchor2' in options

    def test_anchor_selection(self):
        """Anchor should begin with '*'."""
        self.achelper.register_anchor('anchor1')
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert self.achelper.select_option(options[3]) == '*anchor1'

    def test_selection_options(self):
        """Test if selection option are correct."""
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_selection)
        assert len(options) == 2
        assert 'PETSc' in options
        assert 'METIS' in options
        assert self.achelper.select_option('PETSc') == 'PETSc'

    def test_abstract_record_options(self):
        """Test if types are listed as AbstractRecord options."""
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_abstract_record)
        assert len(options) == 3
        assert '!Steady_MH' in options
        assert '!Unsteady_MH' in options
        assert '!Unsteady_LMH' in options
        assert self.achelper.select_option('!Steady_MH') == '!Steady_MH'

    def test_scintilla_options(self):
        """Test if QSci options are generated correctly."""
        self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert self.achelper.scintilla_options.decode('utf-8') == 'mesh_file regions sets'
