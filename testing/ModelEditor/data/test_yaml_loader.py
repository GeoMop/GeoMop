from data.yaml_loader import YamlLoader
from data.yaml.resolver import resolve


def test_parse():
    loader = YamlLoader()
    
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
        "- file: dual_por.pvd\n"
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
    loader = YamlLoader()
    root = loader.load(document)
    # TODO convert values to appropriate type
    assert root.children['output_streams'].children[1].children['time_step'].value == '0.5'
    assert (root.children['problem'].children['primary_equation']
            .children['input_fields'].children[0].children['r_set'].value) == 'ALL'


def test_resolver():
    value = '13'
    assert resolve(value) == 'tag:yaml.org,2002:int'
    value = '-13'
    assert resolve(value) == 'tag:yaml.org,2002:int'
    value = '13.2'
    assert resolve(value) == 'tag:yaml.org,2002:float'
    value = '-13.1e-13'
    assert resolve(value) == 'tag:yaml.org,2002:float'
    value = 'true'
    assert resolve(value) == 'tag:yaml.org,2002:bool'
    value = ''
    assert resolve(value) == 'tag:yaml.org,2002:null'


if __name__ == '__main__':
    test_parse()
