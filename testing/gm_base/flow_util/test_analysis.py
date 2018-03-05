"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import pytest

from flow_util import analysis


@pytest.mark.parametrize('text, params, expected', [
    ('<test>', dict(test=1), '1'),
    ('value: <test>', dict(test='abc'), 'value: abc'),
    ('- <first>\n- <second>', dict(first='a', second='b'), '- a\n- b'),
])
def test_replace_params_in_text(text, params, expected):
    assert analysis.replace_params_in_text(text, params) == expected
