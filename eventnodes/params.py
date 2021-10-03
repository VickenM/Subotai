from abc import abstractmethod

NONE = 0
INPUT_PLUG = 1
OUTPUT_PLUG = 2
PARAM = 4

SUBTYPE_PASSWORD = 1
SUBTYPE_FILEPATH = 2
SUBTYPE_DIRPATH = 4


class Param(object):
    def __init__(self, name, value=None, pluggable=NONE, node=None):
        super().__init__()
        self.color = (200, 200, 200, 255)
        self.name = name
        self._type = None  # int or float or str or list or dict or tuple
        self._subtype = None
        self._value = value
        self.pluggable = pluggable  # NONE means its just a param on the node. otherwise, INPUT_PLUG or OUTPUT_PLUG to make it connectible
        self.connection = None
        self.node = node

        self._old_value = None

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
            self._old_value = self._value
            self._value = new_value
        # print(self._old_value, self._value)

    # Casts the given argument to this Param's type. Default implementation is to use the 'type'
    # ie, if type is int, cast(...) will return int(arg)
    def cast(self, arg):
        return self.type(arg)

    def get_pluggable(self):
        return self.pluggable

    def set_pluggable(self, plug_type):
        self.pluggable = plug_type

    def connect_(self, param):
        assert (isinstance(param, Param))
        self.connection = param
        if self.node:
            self.node.connected_params(connected_param=param, this_param=self)

    def disconnect_(self):
        self.connection = None
        if self.node:
            self.node.disconnected_params(this_param=self)

    def is_connected(self):
        return self.connection is not None

    def to_dict(self):
        return self._value

    def __call__(self, *args, **kwargs):
        return self.value


class IntParam(Param):
    def __init__(self, name='', value=0, minimum=-9999, maximum=9999, pluggable=None, subtype=None, node=None):
        super().__init__(name=name, pluggable=pluggable, node=node)
        self.color = (80, 80, 255, 255)
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
    def __init__(self, name='', value=0.0, minimum=-9999, maximum=9999, pluggable=None, subtype=None, node=None):
        super().__init__(name=name, pluggable=pluggable, node=node)
        self.color = (200, 120, 255, 255)
        self.name = name
        self._type = float
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
    def __init__(self, name='', value='', pluggable=None, subtype=None, node=None):
        super().__init__(name=name, pluggable=pluggable, node=node)
        self.color = (255, 120, 150, 255)
        self.name = name
        self._type = str
        self._subtype = subtype
        self._value = value


class BoolParam(Param):
    def __init__(self, name='', value=True, pluggable=None, subtype=None, node=None):
        super().__init__(name=name, pluggable=pluggable, node=node)
        self.name = name
        self._type = bool
        self._value = value

    def cast(self, arg):
        if type(arg) == int:
            return bool(arg)
        import distutils.util
        return bool(distutils.util.strtobool(arg))


class ListParam(Param):
    def __init__(self, name='', value=[], pluggable=None, subtype=None, node=None):
        super().__init__(name=name, pluggable=pluggable, node=node)
        self.color = (255, 255, 120, 255)
        self.name = name
        self._type = list
        self._value = value

    def to_dict(self):
        return [v._value for v in self._value]


from enum import Enum


class EnumParam(Param):
    def __init__(self, name='', value=Enum, pluggable=None, subtype=None, node=None):
        super().__init__(name=name, pluggable=pluggable, node=node)
        self.color = (255, 160, 0, 255)
        self.name = name
        self._type = Enum
        self._value = value
