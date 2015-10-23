"""Tests for autocomplete helper."""

import pytest
from helpers import AutocompleteHelper

__author__ = 'Tomas Krizek'


class TestAutocompleteHelper:
    """Tests the AutocompleteHelper class."""

    input_type_record = {
        'base_type': 'Record',
        'keys': [
            {'key': 'regions'},
            {'key': 'mesh_file'},
            {'key': 'sets'},
        ]
    }

    @pytest.fixture(autouse=True)
    def setup_achelper(self):
        """Set up a fresh AutocompleteHelper for each test."""
        self.achelper = AutocompleteHelper()

    def test_record_options(self):
        """Test if record keys are added to options."""
        options = self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        assert 'regions' in options
        assert 'mesh_file' in options
        assert 'sets' in options

    def test_key_selection(self):
        """Key should end with ': '."""
        self.achelper.create_options(TestAutocompleteHelper.input_type_record)
        text = self.achelper.select_option('regions')
        assert text == 'regions: '
