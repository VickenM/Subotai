from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM, ListParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


# TODO: implement this the same as splitstring.SplitStringNode, ie without signals

# class SplitParam(ListParam):
#     def __init__(self, first_param, second_param, pattern_param, name=None, pluggable=None):
#         super().__init__(name=name, pluggable=pluggable)
#         self.first_param = first_param
#         self.second_param = second_param
#         self.pattern_param = pattern_param
#
#     @property
#     def value(self):
#         return self.calculate()
#
#     def __call__(self, *args, **kwargs):
#         return self.calculate()
#
#     def calculate(self):
#         pattern = self.pattern_param()
#         parts = self.first_param{}.split(pattern)



class SplitString(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:source': ParameterDefinition(StringParam, {'name': 'source', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:pattern': ParameterDefinition(StringParam, {'name': 'pattern', 'value': '\\', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'output:parts': ParameterDefinition(ListParam, {'name': 'parts', 'value': [], 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'SplitString'
    categories = ['String']
    description = \
        """The **SplitString node** uses *pattern* to split the *source* string into a list of *parts*

Parameters:

- *source*: the input string
- *pattern*: pattern to split the source string by
- *parts*: the resulting list of string parts
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('input:source'))
        self.params.append(self.create_parameter('input:pattern'))
        self.params.append(self.create_parameter('output:parts'))

    def compute(self):
        source = self.get_first_param('source')
        pattern = self.get_first_param('pattern')
        parts = self.get_first_param('parts')

        _parts = source().split(pattern())

        parts.value.clear()
        for p in _parts:
            parts.value.append(StringParam(name='', value=p))

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        super().compute()
