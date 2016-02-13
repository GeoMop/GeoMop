"""Contains storages for project settings.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import copy


class InvalidDeserializationData(Exception):
    pass


class YAMLSerializable:
    """Class that can be represented with native data types in YAML."""

    @staticmethod
    def load(data):
        """Create instance from data."""
        raise NotImplementedError

    def dump(self):
        """Get representation of class with native data structures."""
        raise NotImplementedError


class AbstractCollection(YAMLSerializable):
    """A collection of objects that can be serialized."""
    def __init__(self):
        self._data = None

    def add(self, value):
        raise NotImplementedError

    def get(self, key):
        return NotImplementedError

    def remove(self, key):
        return NotImplementedError


class Parameter(YAMLSerializable):
    """A parameter in a config file."""
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

    @staticmethod
    def load(data):
        kwargs = {}
        if 'name' in data:
            kwargs['name'] = data['name']
        else:
            raise InvalidDeserializationData("Parameter is missing mandatory attribute 'name'")
        if 'type' in data:
            kwargs['type'] = data['type']
        return Parameter(**kwargs)

    def dump(self):
        return dict(name=self.name,
                    type=self.type)


class ParameterCollection(AbstractCollection):
    """Collection of parameters."""
    def __init__(self):
        self._data = {}

    def add(self, param):
        assert isinstance(param, Parameter), "Value is not of type Parameter"
        if param.name not in self._data:
            self._data[param.name] = param
            return True
        return False

    def get(self, name):
        if name not in self._data:
            return None
        return self._data[name]

    def remove(self, name):
        if name in self._data:
            del self._data[name]

    def all(self):
        return [copy.copy(param) for __, param in self._data.items()]

    def merge(self, params):
        """Merge another param collection into this one.
        :rtype: bool
        :return: True if some new parameters were added, False otherwise."""
        assert isinstance(params, ParameterCollection), "Only ParameterCollection can be merged"
        added_new = False
        for param in params.all():
            added_new = self.add(param)
        return added_new

    @staticmethod
    def load(data):
        if not isinstance(data, list):
            raise InvalidDeserializationData("ParameterCollection is not a collection")
        collection = ParameterCollection()
        for entry in data:
            param = Parameter.load(entry)
            collection.add(param)
        return collection

    def dump(self):
        return [param.dump() for name, param in self._data.items()]



