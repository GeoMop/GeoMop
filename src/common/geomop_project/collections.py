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


class FileCollection(AbstractCollection):
    """Collection of files."""
    def __init__(self, project_dir=None):
        self._data = []
        self.project_dir = project_dir
        """this part of the path is stripped from the saved paths to make them relative"""

    def add(self, file_path):
        file_path = self.make_relative(file_path)
        if file_path not in self._data:
            self._data.append(file_path)
            return True
        return False

    def get(self, file_path):
        file_path = self.make_relative(file_path)
        try:
            return self._data[self._data.index(file_path)]
        except ValueError:
            return None

    def remove(self, file_path):
        try:
            self._data.remove(file_path)
        except ValueError:
            pass

    def all(self):
        return copy.copy(self._data)

    def exists_in_project_dir(self, file_path):
        """Whether file exists in the project directory or subdirectories."""
        if not file_path or not self.project_dir:
            return False
        return file_path.startswith(self.project_dir)

    def make_relative(self, file_path):
        """Makes the path relative to project_dir."""
        if not self.project_dir:
            return file_path
        if not file_path.startswith(self.project_dir):
            # assume file_path is already relative to project
            return file_path
        return file_path[len(self.project_dir):]

    @staticmethod
    def load(data):
        if not isinstance(data, list):
            raise InvalidDeserializationData("FileCollection is not a collection")
        collection = FileCollection()
        for file_path in data:
            collection.add(file_path)
        return collection

    def dump(self):
        return self.all()


