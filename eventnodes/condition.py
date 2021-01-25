from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class Condition(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Condition'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='true', pluggable=OUTPUT_PLUG))
        self.signals.append(Signal(node=self, name='false', pluggable=OUTPUT_PLUG))

        self.params.append(IntParam(name='value1', value=0, pluggable=INPUT_PLUG|PARAM))
        self.params.append(IntParam(name='value2', value=0, pluggable=INPUT_PLUG|PARAM))

    def compute(self):
        t = self.get_first_signal('true')
        f = self.get_first_signal('false')

        value1 = self.get_first_param('value1')
        value2 = self.get_first_param('value2')

        if value1.value > value2.value:
            t.emit_event()
        else:
            f.emit_event()
