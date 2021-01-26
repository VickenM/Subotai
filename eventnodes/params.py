from abc import abstractmethod

NONE = 0
INPUT_PLUG = 1
OUTPUT_PLUG = 2
PARAM = 4

SUBTYPE_PASSWORD = 1


class Param(object):
    def __init__(self, name, value=None, pluggable=NONE):
        self.name = name
        self._type = None  # int or float or str or list or dict or tuple
        self._subtype = None
        self._value = value
        self.pluggable = pluggable  # NONE means its just a param on the node. otherwise, INPUT_PLUG or OUTPUT_PLUG to make it connectible
        self.connection = None

    @abstractmethod
    def valid_value(self, value):
        return True

    @property
    def type(self):
        return self._type

    @property
    def subtype(self):
        return self._subtype

    @property
    def value(self):
        if self.connection:
            return self.connection.value
        return self._value

    @value.setter
    def value(self, new_value):
        if self.valid_value(new_value):
            self._value = new_value

    def get_pluggable(self):
        return self.pluggable

    def set_pluggable(self, plug_type):
        self.pluggable = plug_type

    def connect(self, param):
        assert (isinstance(param, Param))
        self.connection = param

    def disconnect(self):
        self.connection = None

    def __call__(self, *args, **kwargs):
        return self.value


class IntParam(Param):
    def __init__(self, name='', value=0, minimum=-9999, maximum=9999, pluggable=None, subtype=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = int
        self._value = value
        self._minimum = minimum
        self._maximum = maximum

    def valid_value(self, value):
        return self.minimum < self.value < self.maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum


class FloatParam(Param):
    def __init__(self, name='', value=0, minimum=None, maximum=None, pluggable=None, subtype=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = int
        self._value = value
        self._minimum = minimum
        self._maximum = maximum

    def valid_value(self, value):
        return self.minimum < self.value < self.maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum


class StringParam(Param):
    def __init__(self, name='', value='', pluggable=None, subtype=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = str
        self._subtype = subtype
        self._value = value


class BoolParam(Param):
    def __init__(self, name='', value=True, pluggable=None, subtype=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = bool
        self._value = value


class ListParam(Param):
    def __init__(self, name='', value=[], pluggable=None, subtype=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = list
        self._value = value


from enum import Enum

class EnumParam(Param):
    def __init__(self, name='', value=Enum, pluggable=None, subtype=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = Enum
        self._value = value
