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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'JoinStrings'
        self.color = (150, 150, 150, 255)

        # self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        # self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))

        first = StringParam(name='first', value='', pluggable=PARAM | INPUT_PLUG)
        second = StringParam(name='second', value='', pluggable=PARAM | INPUT_PLUG)
        separator = StringParam(name='separator', value='', pluggable=PARAM | INPUT_PLUG)
        self.params.append(first)
        self.params.append(second)
        self.params.append(separator)
        self.params.append(JoinParam(first_param=first, second_param=second, sep_param=separator, name='string',
                                     pluggable=OUTPUT_PLUG))

        # def compute(self):
        #     first = self.get_first_param('first')
        #     second = self.get_first_param('second')
        #     sep = self.get_first_param('separator')
        #
        #     string = self.get_first_param('string')
        #
        #     sep_ = sep()
        #     string.value = sep_.join([first(), second()])
        #
        #     signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        #     signal.emit_event()
        #     super().compute()
