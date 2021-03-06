from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from enum import Enum, auto


class CompareParam(EnumParam):
    class Operations(int, Enum):
        less_than = auto()
        greater_than = auto()
        equal = auto()

    enum = Operations


class Condition(ComputeNode):
    type = 'Condition'
    categories = ['Flow Control']
    description = \
        """The **Condition node** compares the values of *value1* and *value2* inputs with the *operation* parameter
and outputs either the *true* or *false* signal, based on the comparison.


Parameters:

- *operation*: The comparison operation to perform on the inputs
- *value1*: The first value to compare
- *value2*: The second value to compare
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='true', pluggable=OUTPUT_PLUG))
        self.signals.append(Signal(node=self, name='false', pluggable=OUTPUT_PLUG))

        self.params.append(CompareParam(name='operation', value=CompareParam.Operations.equal, pluggable=PARAM))
        self.params.append(IntParam(name='value1', value=0, pluggable=INPUT_PLUG | PARAM))
        self.params.append(IntParam(name='value2', value=0, pluggable=INPUT_PLUG | PARAM))

    @ComputeNode.Decorators.show_ui_computation
    @Slot()
    def compute(self):
        self.start_spinner_signal.emit()

        t = self.get_first_signal('true')
        f = self.get_first_signal('false')

        op = self.get_first_param('operation')
        value1 = self.get_first_param('value1')
        value2 = self.get_first_param('value2')

        self.stop_spinner_signal.emit()
        if op.value == op.Operations.greater_than:
            if value1.value > value2.value:
                t.emit_event()
            else:
                f.emit_event()
        elif op.value == op.Operations.less_than:
            if value1.value < value2.value:
                t.emit_event()
            else:
                f.emit_event()
        elif op.value == op.Operations.equal:
            if value1.value == value2.value:
                t.emit_event()
            else:
                f.emit_event()
