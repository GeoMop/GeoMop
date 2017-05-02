#import json


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class WrongKeyError(Error):
    """Raised when attempt assign data to key that not exist"""
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "'{}'".format(self.key)


class ClassFactory:
    """
    Helper class for JsonData.
    """
    def __init__(self, class_list):
        """
        Initialize list of possible classes.
        :param class_list:
        """
        self.class_list = class_list

    def make_instance(self, config):
        """
        Make instance from config dict.
        Dict must contain item "__class__" with name of desired class.
        Desired class must be in class_list.
        :param config:
        :return:
        """
        assert "__class__" in config

        for c in self.class_list:
            if c.__name__ == config["__class__"]:
                config = config.copy()
                del config["__class__"]
                return c(config)
        assert False


class JsonData:
    """
    Abstract base class for various data classes.
    These classes are basically just documented dictionaries,
    which are JSON serializable and provide some syntactic sugar
    (see DotDict from Flow123d - Jan Hybs)
    In order to simplify also serialization of non-data classes, we
    should implement serialization of __dict__.

    Why use JSON for serialization? (e.g. instead of pickle)
    We want to use it for both sending the data and storing them in files,
    while some of these files should be human readable/writable.

    Serializable classes will be derived from this one. And data members
    that should not be serialized are prefixed by '_'.

    TODO: Optional parameter in constructor to specify serialized attributes. (For Pavel)
    ?? Anything similar in current JobPanel?
    """
    def __init__(self, config={}):
        """
        Initialize class dict from config serialization.
        :param config:
        """
        for k, v in config.items():
            if k not in self.__dict__:
                raise WrongKeyError(k)
            self.__dict__[k] = JsonData._deserialize(self.__dict__[k], v)

    @staticmethod
    def _deserialize(temp, data):
        """
        Deserialize data.
        :param temp: template for assign data
        :param data: data for deserialization
        :return:
        """
        # JsonData
        if isinstance(temp, JsonData):
            data = data.copy()
            del data["__class__"]
            return temp.__class__(data)

        # ClassFactory
        elif isinstance(temp, ClassFactory):
            return temp.make_instance(data)

        # dict
        elif isinstance(temp, dict):
            assert temp.__class__ is dict
            d = {}
            for k, v in data.items():
                if k not in temp:
                    raise WrongKeyError(k)
                d[k] = JsonData._deserialize(temp[k], v)
            return d

        # list
        elif isinstance(temp, list):
            assert temp.__class__ is list
            l = []
            if len(temp) == 0:
                for v in data:
                    l.append(JsonData._deserialize(v, v))
            elif len(temp) == 1:
                for v in data:
                    l.append(JsonData._deserialize(temp[0], v))
            else:
                assert False
            return l

        # tuple
        elif isinstance(temp, tuple):
            assert data.__class__ is list
            assert len(temp) == len(data)
            l = []
            for k, v in zip(temp, data):
                l.append(JsonData._deserialize(k, v))
            return tuple(l)

        # other
        else:
            assert temp.__class__ is data.__class__
            return data

    def serialize(self):
        """
        Serialize the object.
        :return:
        """
        return self._get_dict()

    def _get_dict(self):
        """Return dict for serialization."""
        d = {"__class__": self.__class__.__name__}
        for k, v in self.__dict__.items():
            if k[0] != "_":
                d[k] = JsonData._serialize_object(v)
        return d

    @staticmethod
    def _serialize_object(obj):
        """Prepare object for serialization."""
        if isinstance(obj, JsonData):
            return obj._get_dict()
        elif isinstance(obj, dict):
            d = {}
            for k, v in obj.items():
                d[k] = JsonData._serialize_object(v)
            return d
        elif isinstance(obj, list) or isinstance(obj, tuple):
            l = []
            for v in obj:
                l.append(JsonData._serialize_object(v))
            return l
        else:
            return obj

    # @staticmethod
    # def make_instance(config):
    #     """
    #     Make instance from config dict.
    #     Dict must contain item "__class__" with name of desired class.
    #     :param config:
    #     :return:
    #     """
    #     if "__class__" not in config:
    #         return None
    #
    #     # find class by name
    #     cn = config["__class__"]
    #     if cn in locals():
    #         c = locals()[cn]
    #     elif cn in globals():
    #         c = globals()[cn]
    #     else:
    #         return None
    #
    #     # instantiate class
    #     d = config.copy()
    #     del d["__class__"]
    #     return c(d)
