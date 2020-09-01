from enum import IntEnum
from copy import deepcopy
from collections import OrderedDict
#from .history import RegionHistory
from gm_base.geometry_files.format_last import RegionDim
#
# class TopologyOperations(IntEnum):
#     """Type of topology operation"""
#     none = 0
#     """Added diagrams have topology index copy_top_id"""
#     insert = 1
#     """Added diagrams have topology index
#     copy_top_id+1 and next is move about 1"""
#     insert_next = 2
#     """First added diagram have topology index
#     copy_top_id, next added diagrams have topology
#     index copy_top_id+1 and next is move about 1"""
#
# class ShapeDim(IntEnum):
#     """Type of shape"""
#     point = 0
#     """Point"""
#     line = 1
#     """Line"""
#     poly = 2
#     """Polygon"""
#
