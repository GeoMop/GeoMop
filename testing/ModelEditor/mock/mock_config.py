from meconfig import cfg
from meconfig.meconfig import _Config as Config
from model_data import Loader, NotificationHandler
import os

__sample_dir__ = os.path.join(os.path.split(os.path.split(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0])[0])[0], "sample","ModelEditor", "YamlFiles" )

def set_empty_config():
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.config = Config()
    cfg.init(None)


def clean_config():
    import config
    config.delete_config_file("ModelEditorData_test")


def load_complex_structure_to_config():
    with open(os.path.join(__sample_dir__, 'config_complex_structure.yaml')) as file:
        cfg.document = file.read()
    loader = Loader(NotificationHandler())
    cfg.root = loader.load(cfg.document)


def load_valid_structure_to_config():
    with open(os.path.join(__sample_dir__, 'config_valid.yaml')) as file:
        cfg.document = file.read()
    loader = Loader(NotificationHandler())
    cfg.root = loader.load(cfg.document)


def load_invalid_structure_to_config():
    with open(os.path.join(__sample_dir__, 'config_invalid.yaml')) as file:
        cfg.document = file.read()
    loader = Loader(NotificationHandler())
    cfg.root = loader.load(cfg.document)
