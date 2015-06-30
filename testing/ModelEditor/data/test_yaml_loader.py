from data.yaml_loader import YamlLoader


def test_parse():
    document = "format: ascii\nfile: dual_sorp.vtk"
    loader = YamlLoader()
    root = loader.load(document)
    assert root.children['format'].value == 'ascii'


if __name__ == '__main__':
    test_parse()
