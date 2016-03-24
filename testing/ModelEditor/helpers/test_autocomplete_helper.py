"""Tests for autocomplete helper.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import pytest

from helpers import AutocompleteHelper, AutocompleteContext


@pytest.fixture
def achelper():
    return AutocompleteHelper()


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
    'base_type': 'Abstract',
    'implementations': {
        'Steady_MH': None,
        'Unsteady_MH': None,
        'Unsteady_LMH': None
    }
}


def test_record_options(achelper):
    """Test if record keys are added to options."""
    options = achelper.create_options(input_type_record)
    assert len(options) == 3
    assert 'regions' in options
    assert 'mesh_file' in options
    assert 'sets' in options


def test_get_autocompletion_key(achelper):
    """Key should end with ': '."""
    achelper.create_options(input_type_record)
    text = achelper.get_autocompletion('regions')
    assert text == 'regions: '


def test_anchors(achelper):
    """Test adding and clearing anchors."""
    achelper.register_anchor('anchor1')
    achelper.register_anchor('anchor2')
    options = achelper.create_options(input_type_record)
    assert len(options) == 5
    assert '*anchor1' in options
    assert '*anchor2' in options


def test_get_autocompletion_anchor(achelper):
    """Anchor should begin with '*'."""
    achelper.register_anchor('anchor1')
    options = achelper.create_options(input_type_record)
    assert achelper.get_autocompletion(options[3]) == '*anchor1'


def test_get_autocompletion_selection(achelper):
    """Test if selection option are correct."""
    options = achelper.create_options(input_type_selection)
    assert len(options) == 2
    assert 'PETSc' in options
    assert 'METIS' in options
    assert achelper.get_autocompletion('PETSc') == 'PETSc'


def test_get_autocompletion_abstract_record(achelper):
    """Test if types are listed as Abstract options."""
    options = achelper.create_options(input_type_abstract_record)
    assert len(options) == 3
    assert '!Steady_MH' in options
    assert '!Unsteady_MH' in options
    assert '!Unsteady_LMH' in options
    assert achelper.get_autocompletion('!Steady_MH') == '!Steady_MH'


def test_scintilla_options(achelper):
    """Test if QSci options are generated correctly."""
    achelper.create_options(input_type_record)
    assert achelper.scintilla_options.decode('utf-8') == 'mesh_file regions sets'


def test_show_autocompletion(achelper):
    achelper.create_options(input_type_abstract_record)
    context = AutocompleteContext('!Uns', 2)
    achelper.show_autocompletion(context)
    assert achelper.visible is True
    assert achelper.scintilla_options.decode('utf-8') == '!Unsteady_LMH !Unsteady_MH'
    achelper.visible = False
    context = AutocompleteContext('!X', 2)
    achelper.show_autocompletion(context)
    assert achelper.scintilla_options.decode('utf-8') == ''
    assert achelper.visible is False
    # do not show if the option and word+cursor is identical
    context = AutocompleteContext('!Unsteady_MH', 12)
    achelper.show_autocompletion(context)
    assert achelper.scintilla_options.decode('utf-8') == ''


def test_hide_autocompletion(achelper):
    achelper.create_options(input_type_abstract_record)
    context = AutocompleteContext('!Uns', 2)
    achelper.show_autocompletion(context)
    achelper.hide_autocompletion()
    assert achelper.visible is False
    achelper.visible = True
    achelper.get_autocompletion('!Unsteady_MH')
    assert achelper.visible is False


def test_refresh_autocompletion(achelper):
    achelper.create_options(input_type_abstract_record)
    context = AutocompleteContext('!Uns', 2)
    assert achelper.visible is False
    achelper.show_autocompletion(context)
    assert achelper.visible is True
    assert achelper.scintilla_options.decode('utf-8') == '!Unsteady_LMH !Unsteady_MH'
    context = AutocompleteContext('!Unsteady_L', 11)
    achelper.refresh_autocompletion(context)
    assert achelper.scintilla_options.decode('utf-8') == '!Unsteady_LMH'
    assert achelper.visible is True
    context = AutocompleteContext('!Unsteady_X', 11)
    achelper.refresh_autocompletion(context)
    assert achelper.scintilla_options.decode('utf-8') == ''
    assert achelper.visible is False


@pytest.mark.parametrize('line, index, expected', [
    ('value', 3, 'val'),
    ('key: ', 0, ''),
    ('key: ', 2, 'ke'),
    ('*anchor', 7, '*anchor'),
    ('!tag', 1, '!')
])
def test_autocomplete_context(line, index, expected):
    assert AutocompleteContext(line, index).hint == expected
