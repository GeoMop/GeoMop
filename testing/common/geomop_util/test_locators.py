"""Tests for locators.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from geomop_util import Position


def test_position():
    assert (Position(1, 1) == Position(1, 1)) is True
    assert (Position(1, 1) < Position(1, 1)) is False
    assert (Position(1, 1) <= Position(1, 1)) is True
    assert (Position(1, 1) > Position(1, 2)) is False
    assert (Position(1, 2) >= Position(1, 2)) is True
    assert (Position(2, 1) <= Position(1, 2)) is False
    assert (Position(2, 1) > Position(1, 2)) is True


def test_position_from_document_end():
    """Tests position initialization from document end."""
    document = (
        "format: ascii\n"
        "file: dual_sorp.vtk"
    )
    pos = Position.from_document_end(document)
    assert pos.line == 2
    assert pos.column == 20

