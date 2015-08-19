from data.data_node import Position
import data.data_node as dn
from data.yaml import Loader
from data.yaml.resolver import resolve_scalar_tag
import pytest
from data.meconfig import MEConfig as cfg
import mock_config as mockcfg
import sys
from PyQt5.QtWidgets import QApplication
from data.error_handler import ErrorHandler


APP = QApplication(sys.argv)
APP_NOT_INIT = pytest.mark.skipif(not (type(APP).__name__ == "QApplication"),
                                  reason="App not inicialized")


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
    pos = dn.Position.from_document_end(document)
    assert pos.line == 2
    assert pos.column == 20


@APP_NOT_INIT
def test_parse(request=None):
    error_handler = ErrorHandler()
    mockcfg.set_empty_config()

    if request is not None:
        def fin_test_config():
            mockcfg.clean_config()
        request.addfinalizer(fin_test_config)
    loader = Loader(error_handler)

    # parse mapping, scalar
    document = (
        "format: ascii\n"
        "file: dual_sorp.vtk"
    )
    root = loader.load(document)
    assert root.children[0].value == 'ascii'

    # parse sequence, scalar
    document = (
        "- ascii\n"
        "- utf-8"
    )
    root = loader.load(document)
    assert root.children[1].value == 'utf-8'

    # test complex structure
    mockcfg.load_complex_structure_to_config()

    # test values - are scalars converted to the correct type?
    assert cfg.root.children[0].children[0].children[0].value is None
    assert cfg.root.children[1].children[1].children[0].value is True
    assert cfg.root.children[0].children[1].children[1].value == 0.5
    assert (cfg.root.children[1].children[1].children[1].children[0].children[1]
            .value) == 'ALL'
    assert (cfg.root.children[1].children[1].children[1].children[1].children[0]
            .value) == 0

    # test node spans - try to get node at certain positions
    assert cfg.root.get_node_at_position(Position(5, 5)) == (
        cfg.root.children[0].children[0].children[0])
    assert cfg.root.get_node_at_position(Position(5, 9)) == (
        cfg.root.children[0].children[0].children[0])
    assert cfg.root.get_node_at_position(Position(13, 18)) == (
        cfg.root.children[1].children[1]
        .children[0])
    assert cfg.root.get_node_at_position(Position(15, 22)) == (
        cfg.root.children[1].children[1]
        .children[1].children[0].children[0])
    assert cfg.root.get_node_at_position(Position(15, 33)) == (
        cfg.root.children[1].children[1]
        .children[1].children[0].children[1])

    # test absolute_path, get_node_at_path
    assert cfg.root.get_node_at_path('/') == cfg.root
    input_fields_node = cfg.root.get_node_at_path('/problem/primary_equation/input_fields')
    assert input_fields_node == cfg.root.children[1].children[1].children[1]
    assert input_fields_node.get_node_at_path('.') == input_fields_node
    assert (input_fields_node.get_node_at_path('./0/r_set') ==
            input_fields_node.children[0].children[1])
    assert (input_fields_node.get_node_at_path('/problem/primary_equation/input_fields/0/r_set') ==
            input_fields_node.children[0].children[1])
    assert input_fields_node.get_node_at_path('../../..') == cfg.root

    with pytest.raises(LookupError):
        cfg.root.get_node_at_path('/invalid/path')

    # test parser error
    document = (
        "format: ascii\n"
        "- file: dual_sorp.vtk"
    )
    loader.load(document)
    assert len(loader.error_handler.errors) == 1

    # test tag parsing
    document = (
        "problem: !SequentialCoupling\n"
        "  test: 1"
    )
    root = loader.load(document)
    assert root.children[0].type.value == 'SequentialCoupling'
    assert root.get_node_at_position(Position(1, 11)).type.value == 'SequentialCoupling'

    mockcfg.load_valid_structure_to_config()

    # test get_node_at_path
    assert cfg.root.get_node_at_path('/') == cfg.root
    assert (cfg.root.get_node_at_path('/problem/mesh/mesh_file').value ==
            'input/dual_por.msh')
    assert (cfg.root.children[0].children[0].get_node_at_path(
        '../primary_equation/balance').value is True)

    # test tag
    assert cfg.root.children[0].type.value == 'SequentialCoupling'
    assert cfg.root.children[0].type.span.start.line == 6
    assert cfg.root.children[0].type.span.start.column == 11
    assert cfg.root.children[0].type.span.end.line == 6
    assert cfg.root.children[0].type.span.end.column == 29

    # test ref
    input_fields = cfg.root.children[0].children[1].children[1]
    assert input_fields.children[0].children[0].value == 0
    assert input_fields.children[2].children[0].value == 0

    # test empty abstract record
    node = cfg.root.get_node_at_path('/problem/primary_equation/solver')
    assert isinstance(node, dn.CompositeNode)
    assert node.explicit_keys is True
    assert node.type.value == 'Petsc'

    # test ref errors
    document = (
        "- &r text\n"
        "- *x\n"
        "- *r\n"
        "- *y"
    )
    loader.error_handler.clear()
    root = loader.load(document)
    assert len(loader.error_handler.errors) == 2


def test_resolver():
    value = '13'
    assert resolve_scalar_tag(value) == 'tag:yaml.org,2002:int'
    value = '-13'
    assert resolve_scalar_tag(value) == 'tag:yaml.org,2002:int'
    value = '13.2'
    assert resolve_scalar_tag(value) == 'tag:yaml.org,2002:float'
    value = '-13.1e-13'
    assert resolve_scalar_tag(value) == 'tag:yaml.org,2002:float'
    value = 'true'
    assert resolve_scalar_tag(value) == 'tag:yaml.org,2002:bool'
    value = ''
    assert resolve_scalar_tag(value) == 'tag:yaml.org,2002:null'


def profile_parsing():
    import timeit

    setup = (
        "from data.yaml import Loader\n"
        "with open('data/examples/config_simple.yaml') as file:\n"
        "    document = file.read()\n"
        "loader = Loader()\n"
    )
    number = 100
    total_time = timeit.timeit('root = loader.load(document)',
                               setup=setup,
                               number=number)
    print("loading document takes ~{0:.3f}ms".format(total_time * 1000 / number))

    setup += (
        "root = loader.load(document)\n"
        "from data.data_node import Position\n"
        "position = Position(40, 35)\n"
    )
    number = 10000
    total_time = timeit.timeit('root.get_node_at_position(position)',
                               setup=setup,
                               number=number)

    print("finding node takes ~{0:.3f}ms".format(total_time * 1000 / number))


if __name__ == '__main__':
    test_parse()
