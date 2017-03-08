from backend.json_data import *

class A(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = "test"
        self.c = 2.0
        self._u = 5

        super().__init__(config)

class A2(JsonData):
    def __init__(self, config):
        self.x = 2
        self.y = "test2"

        super().__init__(config)

class B(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = A({"a": 2})

        super().__init__(config)

class C(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = ClassFactory([A, A2])

        super().__init__(config)

class D(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = {"a": 1, "b": 2.0, "c": A({"a": 2})}

        super().__init__(config)

class D2(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = {"a": 1, "b": 2.0, "c": [1, [1, 2]]}

        super().__init__(config)

class E(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = []

        super().__init__(config)

class E2(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = [A({"a": 2})]

        super().__init__(config)

class F(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = (1, 2.0, A({"a": 2}))

        super().__init__(config)





a = A({"a": 2})
print(a.serialize())

b = B({"a": 2, "b": {"a": 3, "b": "aaa"}})
print(b.serialize())

c = C({"a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa"}})
print(c.serialize())

d = D({"a": 2, "b": {"a": 3, "b": 3.0, "c": {"__class__": "A", "a": 3}}})
print(d.serialize())

d2 = D2({"a": 2, "b": {"a": 3, "b": 3.0, "c": [2, [3, 4]]}})
print(d2.serialize())

e = E({"a": 2, "b": [1, 2.0, "aaa"]})
print(e.serialize())

e2 = E2({"a": 2, "b": [{"__class__": "A", "a": 3}, {"__class__": "A", "a": 5}]})
print(e2.serialize())

f = F({"a": 2, "b": [2, 3.0, {"__class__": "A", "a": 3}]})
print(f.serialize())


a = A({"a": 2, "d": 3, "q": 8})
