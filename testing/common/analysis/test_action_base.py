
from typing import List
import src.common.analysis.action_base as base
import src.common.analysis.code.decorators as wf
import src.common.analysis.code.wrap as wrap
import src.common.analysis.action_instance as ai


@wf.Class
class Point:
    x: float = 0.0
    y: float = 0.0

@wf.Class
class Element:
    region: int
    node_ids: List[int] = []


@wf.Class
class Mesh:
    nodes: List[Point] = []
    elements: List[Element] = []



def test_dataclass_modification():
    #
    point_wrap = Point
    point_action = point_wrap.action
    params = list(point_action.parameters)
    param_z = base.ActionParameter(2, "z", float, 0.0)
    params.append(param_z)
    point_xyz = wrap.public_action( base.ClassActionBase.construct_from_params("PointXYZ", params) )
    xyz_instance = point_xyz(x=1, y=2, z=3)._action
    assert len(xyz_instance.arguments) == 3
    assert xyz_instance.arguments[0].value.action.value == 1.0
    assert xyz_instance.arguments[1].value.action.value == 2.0
    assert xyz_instance.arguments[2].value.action.value == 3.0




# def test_classtypes():
#     mesh = Mesh()
#     point = data.Class(x:float = 0, y:float = 0)
#
# def test_subtypes():
#
#     data.Sequence[]
