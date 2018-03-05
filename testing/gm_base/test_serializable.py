"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from gm_base.geomop_util.serializable import Serializable
from enum import IntEnum


class MyEnum(IntEnum):
    a = 1
    b = 2


class RegularData:

    def __init__(self, a=1, b=2):
        self.a = a
        self.b = b


class DataList:

    __serializable__ = Serializable(composite={'data': RegularData})

    def __init__(self, data=None):
        self.data = data if data is not None else []


class MyData:

    def __init__(self, **kwargs):
        self.a = kwargs['a']
        self.b = kwargs['b'] if 'b' in kwargs else 0
        self.c = kwargs['c'] if 'c' in kwargs else None
        self.d = kwargs['d'] if 'd' in kwargs else None
        self.o = 4
        self.e = kwargs['e'] if 'e' in kwargs else MyEnum.a


MyData.__serializable__ = Serializable(
    excluded=['o'],
    default={'a': 1},
    composite={'c': MyData, 'e': MyEnum}
)


class UuidDict(dict):

    __serializable__ = Serializable(
        composite={'__all__': MyData,
                   'special': int}
    )

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value


def test_load_serializable():
    data = {'b': 2, 'c': {'a': 2, 'o': 5}, 'e': 2}
    mydata = Serializable.load(data, MyData)
    assert mydata.a == 1
    assert mydata.b == 2
    assert isinstance(mydata.c, MyData) is True
    assert mydata.o == 4
    assert mydata.c.a == 2
    assert mydata.c.b == 0
    assert mydata.c.c is None
    assert mydata.c.o == 4
    assert mydata.e == MyEnum.b


def test_dump_serializable():
    mydata = MyData(a=1, b=2, c=MyData(a=2), e=MyEnum.b)
    data = Serializable.dump(mydata)
    assert isinstance(data, dict) is True
    assert data['a'] == 1
    assert data['b'] == 2
    assert isinstance(data['c'], dict) is True
    assert data['c']['a'] == 2
    assert data['c']['b'] == 0
    assert data['e'] == 2


def test_load_serializable_regular():
    data = {'a': 3, 'b': 4}
    regdata = Serializable.load(data, RegularData)
    assert isinstance(regdata, RegularData) is True
    assert regdata.a == 3
    assert regdata.b == 4


def test_dump_serializable_regular():
    regdata = RegularData(a=1, b=2)
    data = Serializable.dump(regdata)
    assert isinstance(data, dict) is True
    assert data['a'] == 1
    assert data['b'] == 2


def test_load_serializable_list():
    data = {'data': [{'a': 2, 'b': 4},
                     {'a': 6, 'b': 2}]}
    datalist = Serializable.load(data, DataList)
    assert isinstance(datalist, DataList) is True
    assert len(datalist.data) == 2
    assert datalist.data[0].a == 2
    assert datalist.data[0].b == 4
    assert datalist.data[1].a == 6
    assert datalist.data[1].b == 2


def test_dump_serializable_list():
    datalist = DataList(data=[RegularData(a=2, b=4),
                              RegularData(a=6, b=2)])
    data = Serializable.dump(datalist)
    assert isinstance(data['data'], list)
    assert len(data['data']) == 2
    assert data['data'][0]['a'] == 2
    assert data['data'][0]['b'] == 4
    assert data['data'][1]['a'] == 6
    assert data['data'][1]['b'] == 2


def test_load_serializable_uuiddict():
    data = {'a1': {'a': 2, 'b': 4},
            'b3': {'a': 6, 'b': 2},
            'special': 2}
    uuiddict = Serializable.load(data, UuidDict)
    assert isinstance(uuiddict, UuidDict) is True
    assert len(uuiddict) == 3
    assert uuiddict['a1'].a == 2
    assert uuiddict['a1'].b == 4
    assert uuiddict['b3'].a == 6
    assert uuiddict['b3'].b == 2
    assert uuiddict['special'] == 2


def test_dump_serializable_uuiddict():
    uuiddict = UuidDict(
        special=2,
        a1=MyData(a=2, b=4),
        b3=MyData(a=6, b=2)
    )
    data = Serializable.dump(uuiddict)
    assert isinstance(data, dict) is True
    assert len(data) == 3
    assert data['a1']['a'] == 2
    assert data['a1']['b'] == 4
    assert data['b3']['a'] == 6
    assert data['b3']['b'] == 2
    assert data['special'] == 2
