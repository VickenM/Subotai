from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

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
    parameter_definitions = {
        'input:first': ParameterDefinition(StringParam, {'name': 'first', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:second': ParameterDefinition(StringParam, {'name': 'second', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:separator': ParameterDefinition(StringParam, {'name': 'separator', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'output:string': ParameterDefinition(JoinParam, {'name': 'string', 'pluggable': OUTPUT_PLUG}, storage='derived', bind_node=False),
    }

    type = 'JoinStrings'
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
        self.color = (150, 150, 150, 255)

        first = self.create_parameter('input:first')
        second = self.create_parameter('input:second')
        separator = self.create_parameter('input:separator')
        self.params.append(separator)
        self.params.append(first)
        self.params.append(second)
        self.params.append(JoinParam(first_param=first, second_param=second, sep_param=separator, name='string',
                                     pluggable=OUTPUT_PLUG))
