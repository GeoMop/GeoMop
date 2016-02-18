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


class File(YAMLSerializable):
    """Represents a file entry in a config file."""
    def __init__(self, file_path, params=None):
        self.file_path = file_path
        if params is None:
            self.params = set()
        else:
            self.params = set(params)

    @staticmethod
    def load(data):
        kwargs = {}
        if 'file_path' in data:
            kwargs['file_path'] = data['file_path']
        else:
            raise InvalidDeserializationData("File is missing mandatory attribute 'file_path'")
        if 'params' in data:
            kwargs['params'] = data['params']
        return File(**kwargs)

    def dump(self):
        return dict(file_path=self.file_path,
                    params=list(self.params))


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

    def keys(self):
        return [key for key in self._data]

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

    def add(self, file_path, params=None):
        file_path = self.make_relative_path(file_path)
        file = self.get(file_path)
        if file is not None and params is not None:
            # file already exists, change set of parameters (if provided, keep old otherwise)
            file.params.clear()
            file.params.update(params)
            return
        file = File(file_path, params)
        self._data.append(file)
        return

    def get(self, file_path):
        file_path = self.make_relative_path(file_path)
        for file in self._data:
            if file.file_path == file_path:
                return file
        return None

    def remove(self, file_path):
        file = self.get(file_path)
        if file is not None:
            self._data.remove(file)

    def all(self):
        return copy.deepcopy(self._data)

    def path_is_in_project_dir(self, file_path):
        """Whether file exists in the project directory or subdirectories."""
        if not file_path or not self.project_dir:
            return False
        return file_path.startswith(self.project_dir)

    def make_relative_path(self, file_path):
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
        for file_data in data:
            file = File.load(file_data)
            collection.add(file.file_path, file.params)
        return collection

    def dump(self):
        return [file.dump() for file in self.all()]


