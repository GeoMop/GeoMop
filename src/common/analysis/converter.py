
import indexed
from typing import *

from common.analysis import action_base as base







class GetAttribute(base._ActionBase):


    def _code(self):
        data_class = self.arguments[0].value
        assert isinstance(data_class, base._ActionBase)
        attr_name = self.arguments[1].value
        assert isinstance(attr_name, base.Value)
        attr_name = attr_name.evaluate([])
        return "{} = {}.{}".format(self.get_code_instance_name(), data_class.get_code_instance_name(), attr_name)

    @classmethod
    def _evaluate(cls, data_class: Any, attr_name: str) -> Any:
        return data_class.get_attribute(attr_name)




class GetItem(base._ActionBase):

    @classmethod
    def _evaluate(cls, data_list: List[Any], idx: str) -> Any:
        return data_list[idx]



