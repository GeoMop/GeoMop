"""Tests for autocomplete helper."""

import pytest
from helpers import AutocompleteHelper

__author__ = 'Tomas Krizek'


class TestAutocompleteHelper:
    """Tests the AutocompleteHelper class."""

    @pytest.fixture(autouse=True)
    def setup_achelper(self):
        """Set up a fresh AutocompleteHelper for each test."""
        self.achelper = AutocompleteHelper()

    def test_record_options(self):
        """Test if record keys are added to options."""
        input_type = {
            'base_type': 'Record',
            'keys': [
                {'key': 'regions'},
                {'key': 'mesh_file'},
                {'key': 'sets'},
            ]
        }
        options = self.achelper.create_options(input_type)
        assert 'regions' in options
        assert 'mesh_file' in options
        assert 'sets' in options
