import gm_base.config as config
import os

from gm_base.geomop_util import Serializable


class DataForTestInner:
    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        self.a = kw_or_def('a', 0)
        self.b = kw_or_def('a', 1)


class DataForTest:

    __serializable__ = Serializable(
        composite={'inner': DataForTestInner}
    )

    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        self.inner = kw_or_def('inner', DataForTestInner())
        self.name = kw_or_def('name', "ooo")


def test_config_save_and_load():
    #config dir exist
    #assert os.path.isdir(config.__config_dir__)
    data = DataForTest()
    data.inner.a = 6
    data.name="test1"
    config.save_config_file("test_data", data)
    data.inner.a = 7
    data.name="test2"
    data = config.get_config_file("test_data", cls=DataForTest)
    assert data.inner.a ==6
    assert data.name == "test1"
    data.inner.a = 7
    data.name="test2"
    config.save_config_file("test_data", data)
    data = config.get_config_file("test_data", cls=DataForTest)
    assert data.inner.a ==7
    assert data.name == "test2"
    config.delete_config_file("test_data")
    data = config.get_config_file("test_data")
    assert data == None
    config.delete_config_file("test_data")
    
    
