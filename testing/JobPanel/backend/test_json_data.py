from backend.json_data import *

import json


def test_json_data():
    # create, serialize
    class A(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = "test"
            self.c = 2.0
            self._u = 5

            super().__init__(config)

    a = A({"a": 2})

    assert a.a == 2
    assert a.b == "test"
    assert a.c == 2.0
    assert a._u == 5

    assert json.dumps(a.serialize(), sort_keys=True) == '{"__class__": "A", "a": 2, "b": "test", "c": 2.0}'

    # JsonData object
    class B(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = A()

            super().__init__(config)

    b = B({"a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa"}})

    assert b.a == 2
    assert b.b.__class__ is A
    assert b.b.a == 3
    assert b.b.b == "aaa"

    assert json.dumps(b.serialize(), sort_keys=True) ==\
        '{"__class__": "B", "a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa", "c": 2.0}}'

    # ClassFactory
    class A2(JsonData):
        def __init__(self, config={}):
            self.x = 2
            self.y = "test2"

            super().__init__(config)

    class C(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = ClassFactory([A, A2])

            super().__init__(config)

    c = C({"a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa"}})

    assert c.a == 2
    assert c.b.__class__ is A
    assert c.b.a == 3
    assert c.b.b == "aaa"

    assert json.dumps(c.serialize(), sort_keys=True) ==\
        '{"__class__": "C", "a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa", "c": 2.0}}'

    # dict
    class D(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = {"a": 1, "b": 2.0, "c": A({"a": 2})}

            super().__init__(config)

    d = D({"a": 2, "b": {"a": 3, "b": 3.0, "c": {"__class__": "A", "a": 3}}})

    assert d.a == 2
    assert isinstance(d.b, dict)
    assert d.b["a"] == 3
    assert d.b["b"] == 3.0
    assert d.b["c"].__class__ is A
    assert d.b["c"].a == 3

    assert json.dumps(d.serialize(), sort_keys=True) ==\
        '{"__class__": "D", "a": 2, "b": {"a": 3, "b": 3.0, "c": {"__class__": "A", "a": 3, "b": "test", "c": 2.0}}}'

    # list in list in dict
    class D2(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = {"a": 1, "b": 2.0, "c": [[1]]}

            super().__init__(config)

    d2 = D2({"a": 2, "b": {"a": 3, "b": 3.0, "c": [[2, 3], [4, 5]]}})

    assert d2.b["a"] == 3
    assert d2.b["c"][0][0] == 2
    assert d2.b["c"][1][1] == 5

    assert json.dumps(d2.serialize(), sort_keys=True) ==\
        '{"__class__": "D2", "a": 2, "b": {"a": 3, "b": 3.0, "c": [[2, 3], [4, 5]]}}'

    # empty list
    class E(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = []

            super().__init__(config)

    e = E({"a": 2, "b": [1, 2.0, "aaa"]})

    assert e.b[0] == 1
    assert e.b[1] == 2.0
    assert e.b[2] == "aaa"

    assert json.dumps(e.serialize(), sort_keys=True) == '{"__class__": "E", "a": 2, "b": [1, 2.0, "aaa"]}'

    # list with one item
    class E2(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = [A({"a": 2})]

            super().__init__(config)

    e2 = E2({"a": 2, "b": [{"__class__": "A", "a": 3}, {"__class__": "A", "a": 5}]})

    assert e2.b[0].__class__ == A
    assert e2.b[0].a == 3
    assert e2.b[1].a == 5

    assert json.dumps(e2.serialize(), sort_keys=True) ==\
        '{"__class__": "E2", "a": 2, "b": [{"__class__": "A", "a": 3, "b": "test", "c": 2.0}, ' \
        '{"__class__": "A", "a": 5, "b": "test", "c": 2.0}]}'

    # tuple
    class F(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = (1, 2.0, A({"a": 2}))

            super().__init__(config)

    f = F({"a": 2, "b": [2, 3.0, {"__class__": "A", "a": 3}]})

    assert isinstance(f.b, tuple)
    assert f.b[0] == 2
    assert f.b[2].__class__ is A
    assert f.b[2].a == 3

    assert json.dumps(f.serialize(), sort_keys=True) ==\
        '{"__class__": "F", "a": 2, "b": [2, 3.0, {"__class__": "A", "a": 3, "b": "test", "c": 2.0}]}'

    # WrongKeyError
    try:
        a = A({"a": 2, "d": 3})
        assert False
    except WrongKeyError:
        pass

    # recursion
    class G(JsonData):
        def __init__(self, config={}):
            self.a = 1
            self.b = (1, 2.0, [A({"a": 2})])
            self.c = {"a": 2, "b": {"c": ClassFactory([A, A2])}}

            super().__init__(config)

    g = G({"a": 2, "b": [2, 3.0, [{"__class__": "A", "a": 3}, {"__class__": "A", "a": 5}]],
           "c": {"a": 3, "b": {"c": {"__class__": "A", "a": 7}}}})

    assert isinstance(g.b, tuple)
    assert g.b[1] == 3.0
    assert g.b[2].__class__ is list
    assert g.b[2][1].__class__ is A
    assert g.b[2][1].a == 5
    assert isinstance(g.c, dict)
    assert g.c["a"] == 3
    assert isinstance(g.c["b"], dict)
    assert g.c["b"]["c"].__class__ is A
    assert g.c["b"]["c"].a == 7

    assert json.dumps(g.serialize(), sort_keys=True) ==\
        '{"__class__": "G", "a": 2, "b": [2, 3.0, [{"__class__": "A", "a": 3, "b": "test", "c": 2.0}, ' \
        '{"__class__": "A", "a": 5, "b": "test", "c": 2.0}]], ' \
        '"c": {"a": 3, "b": {"c": {"__class__": "A", "a": 7, "b": "test", "c": 2.0}}}}'
