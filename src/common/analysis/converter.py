
import indexed
from typing import *

from common.analysis import action_base as base







class GetAttribute(base._ActionBase):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def format(self, n_args):
        assert n_args == self.parameters.size()
        return "{{0}}.{key}".format(key=self.key)

    def _evaluate(self, data_class: Any) -> Any:
        return data_class.get_attribute(self.key)




class GetItem(base._ActionBase):

    def format(self, n_args):
        assert n_args == self.parameters.size()
        return "{0}[{1}]"

    def _evaluate(self, data_list: List[Any], idx: str) -> Any:
        return data_list[idx]



