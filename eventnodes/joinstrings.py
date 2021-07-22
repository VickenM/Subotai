from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode, BaseNode
from .params import StringParam, IntParam, PARAM, ListParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class JoinParam(StringParam):
    def __init__(self, first_param, second_param, sep_param, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.first_param = first_param
        self.second_param = second_param
        self.sep_param = sep_param

    @property
    def value(self):
        return self.calculate()

    def __call__(self, *args, **kwargs):
        return self.calculate()

    def calculate(self):
        sep_ = self.sep_param()
        return sep_.join([self.first_param(), self.second_param()])


class JoinStrings(BaseNode):
    categories = ['String']
    description = \
        """The **JoinString node** joins *first* with *second* with *separator* in between.

Parameters:

- *first*: the first string
- *second*: the seconds string
- *separator*: the separator between strings
- *string*: the resulting string from joining the input strings
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'JoinStrings'
        self.color = (150, 150, 150, 255)

        first = StringParam(name='first', value='', pluggable=PARAM | INPUT_PLUG)
        second = StringParam(name='second', value='', pluggable=PARAM | INPUT_PLUG)
        separator = StringParam(name='separator', value='', pluggable=PARAM | INPUT_PLUG)
        self.params.append(separator)
        self.params.append(first)
        self.params.append(second)
        self.params.append(JoinParam(first_param=first, second_param=second, sep_param=separator, name='string',
                                     pluggable=OUTPUT_PLUG))
