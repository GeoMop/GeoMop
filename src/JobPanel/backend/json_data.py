import json


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
        if "__class__" not in config:
            return None

        for c in self.class_list:
            if c.__name__ == config["__class__"]:
                return c(config)
        return None

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

    ?? Anything similar in current JobPanel?
    """
    def __init__(self, config):
        """
        Initialize class dict from config serialization.
        :param config:
        """
        for k, v in config.items():
            if k in self.__dict__:
                # dict
                if isinstance(self.__dict__[k], dict):
                    if isinstance(v, dict):
                        for k2, v2 in v.items():
                            if k2 in self.__dict__[k]:
                                obj = self._simple(self.__dict__[k][k2], v2)
                                if obj is not None:
                                    self.__dict__[k][k2] = obj
                # list
                elif isinstance(self.__dict__[k], list):
                    if len(self.__dict__[k]) == 0:
                        if isinstance(v, list):
                            self.__dict__[k] = v
                    elif len(self.__dict__[k]) == 1:
                        if isinstance(v, list):
                            l = []
                            for vi in v:
                                obj = self._simple(self.__dict__[k][0], vi)
                                if obj is not None:
                                    l.append(obj)
                            self.__dict__[k] = l
                # tuple
                elif isinstance(self.__dict__[k], tuple):
                    if isinstance(v, list) and len(self.__dict__[k]) == len(v):
                        l = []
                        for ki, vi in zip(self.__dict__[k], v):
                            obj = self._simple(ki, vi)
                            if obj is not None:
                                l.append(obj)
                        self.__dict__[k] = tuple(l)
                else:
                    obj = self._simple(self.__dict__[k], v)
                    if obj is not None:
                        self.__dict__[k] = obj

    def _simple(self, temp, data):
        # JsonData
        if isinstance(temp, JsonData):
            return temp.__class__(data)
        # ClassFactory
        elif isinstance(temp, ClassFactory):
            return temp.make_instance(data)
        # str
        elif isinstance(temp, str):
            if isinstance(data, str):
                return data
        # int
        elif isinstance(temp, int):
            if isinstance(data, int):
                return data
        # float
        elif isinstance(temp, float):
            if isinstance(data, float) or isinstance(data, int):
                return float(data)
        # bool
        elif isinstance(temp, bool):
            if isinstance(data, bool):
                return data
        # other
        else:
            return data
        return None

    def serialize(self):
        """
        Serialize the object into JSON.
        :return:
        """
        return json.dumps(self._get_dict(), sort_keys=True)

    def _get_dict(self):
        """Return dict for serialization."""
        d = {"__class__": self.__class__.__name__}
        for k, v in self.__dict__.items():
            if k[0] != "_":
                if isinstance(v, JsonData):
                    d[k] = v._get_dict()
                elif isinstance(v, dict):
                    d2 = {}
                    for k2, v2 in v.items():
                        if isinstance(v2, JsonData):
                            d2[k2] = v2._get_dict()
                        else:
                            d2[k2] = v2
                    d[k] = d2
                elif isinstance(v, list) or isinstance(v, tuple):
                    l = []
                    for vi in v:
                        if isinstance(vi, JsonData):
                            l.append(vi._get_dict())
                        else:
                            l.append(vi)
                    d[k] = l
                else:
                    d[k] = v
        return d

    @staticmethod
    def make_instance(config):
        """
        Make instance from config dict.
        Dict must contain item "__class__" with name of desired class.
        :param config:
        :return:
        """
        if "__class__" not in config:
            return None

        # find class by name
        cn = config["__class__"]
        if cn in locals():
            c = locals()[cn]
        elif cn in globals():
            c = globals()[cn]
        else:
            return None

        # instantiate class
        d = config.copy()
        del d["__class__"]
        return c(d)
