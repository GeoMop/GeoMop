import common.analysis as analysis
import os
import pytest


class A:
    pass
class B(A):
    pass
class C(A):
    pass
class D(B):
    pass
class E(B):
    pass


def test_closest_common_ancestor():
    cca = analysis.action_base.closest_common_ancestor
    assert cca(D, E) is B
    assert cca(C, D) is A
    assert cca(A, B) is A
    assert cca(A, int) is object




@pytest.mark.parametrize("src_file", ["analysis.in.py"])
def test_representation(src_file):
    module = analysis.base._Module.create_from_file(src_file)
    code = module.code()
    round_module_name = "round."+module.name
    with open(round_module_name +".py", "w") as f:
        f.write(code)

    round_module = analysis.base._Module.create_from_source(round_module_name, code)
    round_code = round_module.code()
    assert code == round_code

    with open(round_module_name +".py", "w") as f:
        f.write(round_code)
    base, ext = os.path.splitext(src_file)
    assert ext == ".py"
    base, _in = os.path.splitext(base)
    assert _in == ".in"
    ref_out = "{}.ref.py".format(base)
    with open(ref_out, "r") as f:
        ref_code = f.read()
    assert code == ref_code


