import pytest
from analysis.analysis import *

def test_generic_representation():


    def test_workflow(a, b):
        c = Tuple(a).name("c")
        d = Tuple(a, b)
        e = Tuple(c, d)
        return e

    w = make_workflow(test_workflow)
    print(w.code())