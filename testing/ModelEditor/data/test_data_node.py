from data.data_node import Position, DataError
from data.yaml import Loader
from data.yaml.resolver import resolve_scalar_tag
import pytest
from data.meconfig import MEConfig as cfg
import mock_config as mockcfg
import sys
from PyQt5.QtWidgets import QApplication


app = QApplication(sys.argv)
app_not_init = pytest.mark.skipif(not (type(app).__name__ == "QApplication"),
    reason="App not inicialized")


def test_position():
    assert (Position(1, 1) == Position(1, 1)) is True
    assert (Position(1, 1) < Position(1, 1)) is False
    assert (Position(1, 1) <= Position(1, 1)) is True
    assert (Position(1, 1) > Position(1, 2)) is False
    assert (Position(1, 2) >= Position(1, 2)) is True
    assert (Position(2, 1) <= Position(1, 2)) is False
    assert (Position(2, 1) > Position(1, 2)) is True


@app_not_init
def test_parse(request):
    mockcfg.set_empty_config()

    def fin_test_config():
        mockcfg.clean_config()

    request.addfinalizer(fin_test_config)
    loader = Loader()

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

    # test parser error
    document = (
        "format: ascii\n"
        "- file: dual_sorp.vtk"
    )
    with pytest.raises(DataError):
        loader.load(document)

    # test tag parsing
    document = (
        "problem: !SequentialCoupling\n"
        "  test: 1"
    )
    root = loader.load(document)
    assert root.children[0].children[0].value == 'SequentialCoupling'
    assert root.get_node_at_position(Position(1, 11)).value == 'SequentialCoupling'


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
