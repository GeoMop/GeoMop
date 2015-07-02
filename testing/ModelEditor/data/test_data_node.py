from data.data_node import Position
from data.yaml import Loader
from data.yaml.resolver import resolve_scalar_tag


def test_position():
    assert (Position(1, 1) == Position(1, 1)) is True
    assert (Position(1, 1) < Position(1, 1)) is False
    assert (Position(1, 1) <= Position(1, 1)) is True
    assert (Position(1, 1) > Position(1, 2)) is False
    assert (Position(1, 2) >= Position(1, 2)) is True
    assert (Position(2, 1) <= Position(1, 2)) is False
    assert (Position(2, 1) > Position(1, 2)) is True


def test_parse():
    loader = Loader()

    # parse mapping, scalar
    document = (
        "format: ascii\n"
        "file: dual_sorp.vtk"
    )
    root = loader.load(document)
    assert root.children['format'].value == 'ascii'

    # parse sequence, scalar
    document = (
        "- ascii\n"
        "- utf-8"
    )
    root = loader.load(document)
    assert root.children[1].value == 'utf-8'

    # test complex structure
    document = (
        "output_streams:\n"
        "- file: \n"
        "  format: flow_output_stream\n"
        "- file: dual_por_transport.pvd\n"
        "  time_step: 0.5\n"
        "\n"
        "problem:\n"
        "  description: Some, text\n"
        "  primary_equation:\n"
        "    balance: true\n"
        "    input_fields:\n"
        "    - {conductivity: 1.0e-15, r_set: ALL}\n"
        "    - {bc_pressure: 0, bc_type: dirichlet, r_set: BOUNDARY}\n"
    )
    loader = Loader()
    root = loader.load(document)

    # test values - are scalars converted to the correct type?
    assert (root.children['output_streams'].children[0].children['file']
            .value) is None
    assert (root.children['problem'].children['primary_equation']
            .children['balance'].value) is True
    assert (root.children['output_streams'].children[1].children['time_step']
            .value) == 0.5
    assert (root.children['problem'].children['primary_equation']
            .children['input_fields'].children[0].children['r_set'].value) == 'ALL'
    assert (root.children['problem'].children['primary_equation']
            .children['input_fields'].children[1].children['bc_pressure']
            .value) == 0

    # test node spans - try to get node at certain positions
    assert root.get_node_at_position(Position(2, 4)) == (
        root.children['output_streams'].children[0])
    assert root.get_node_at_position(Position(2, 9)) == (
        root.children['output_streams'].children[0].children['file'])
    assert root.get_node_at_position(Position(10, 18)) == (
        root.children['problem'].children['primary_equation']
        .children['balance'])
    assert root.get_node_at_position(Position(12, 22)) == (
        root.children['problem'].children['primary_equation']
        .children['input_fields'].children[0].children['conductivity'])
    assert root.get_node_at_position(Position(12, 32)) == (
        root.children['problem'].children['primary_equation']
        .children['input_fields'].children[0])


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
