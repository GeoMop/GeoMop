from data.meconfig import MEConfig as cfg
from data.meconfig import _Config as Config
from data.yaml import Loader


def set_empty_config():
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.init(None)
    cfg.config = Config()


def clean_config():
    import config
    config.delete_config_file("ModelEditorData_test")


def load_complex_structure_to_config():
    with open('../../sample/ModelEditor/YamlFiles/config_complex_structure.yaml') as file:
        cfg.document = file.read()
    loader = Loader()
    cfg.root = loader.load(cfg.document)


def load_valid_structure_to_config():
    with open('../../sample/ModelEditor/YamlFiles/config_valid.yaml') as file:
        cfg.document = file.read()
    loader = Loader()
    cfg.root = loader.load(cfg.document)


def load_invalid_structure_to_config():
    with open('../../sample/ModelEditor/YamlFiles/config_invalid.yaml') as file:
        cfg.document = file.read()
    loader = Loader()
    cfg.root = loader.load(cfg.document)
