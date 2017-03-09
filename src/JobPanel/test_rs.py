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

class G(JsonData):
    def __init__(self, config):
        self.a = 1
        self.b = (1, 2.0, [A({"a": 2})])
        self.c = {"a": 2, "b": {"c": ClassFactory([A, A2])}}

        super().__init__(config)




g = G({"a": 2, "b": [2, 3.0, [{"__class__": "A", "a": 3}, {"__class__": "A", "a": 5}]],
       "c": {"a": 3, "b": {"c": {"__class__": "A", "a": 7}}}})

print(json.dumps(g.serialize(),
                  sort_keys=True))

