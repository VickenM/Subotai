from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode, BaseNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from enum import Enum, auto


class MathOpParam(EnumParam):
    class Operations(Enum):
        add = auto()
        subtract = auto()
        multiply = auto()
        divide = auto()
        modulo = auto()


class MathParam(IntParam):
    def __init__(self, first_param, second_param, op_param, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.first_param = first_param
        self.second_param = second_param
        self.op_param = op_param

    @property
    def value(self):
        return self.calculate()

    def __call__(self, *args, **kwargs):
        return self.calculate()

    def calculate(self):
        op = self.op_param
        first = self.first_param
        second = self.second_param

        if op.value == op.Operations.add:
            return first.value + second.value
        elif op.value == op.Operations.subtract:
            return first.value - second.value
        elif op.value == op.Operations.multiply:
            return first.value * second.value
        elif op.value == op.Operations.divide:
            return first.value / second.value
        elif op.value == op.Operations.modulo:
            return first.value % second.value

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()


class Math(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Math'
        self.color = (150, 150, 150, 255)

        op = MathOpParam(name='operation', value=MathOpParam.Operations.add, pluggable=PARAM)
        first = IntParam(name='value1', value=0, pluggable=INPUT_PLUG | PARAM)
        second = IntParam(name='value2', value=0, pluggable=INPUT_PLUG | PARAM)
        self.params.append(op)
        self.params.append(first)
        self.params.append(second)
        self.params.append(
            MathParam(first_param=first, second_param=second, op_param=op, name='result', pluggable=OUTPUT_PLUG))

# class Math(ComputeNode):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.type = 'Math'
#
#         self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
#         self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
#
#         self.params.append(MathOpParam(name='operation', value=MathOpParam.Operations.add, pluggable=PARAM))
#         self.params.append(IntParam(name='value1', value=0, pluggable=INPUT_PLUG | PARAM))
#         self.params.append(IntParam(name='value2', value=0, pluggable=INPUT_PLUG | PARAM))
#         self.params.append(IntParam(name='result', value=0, pluggable=OUTPUT_PLUG))
#
#     def compute(self):
#         first = self.get_first_param('value1')
#         second = self.get_first_param('value2')
#         op = self.get_first_param('operation')
#
#         result = self.get_first_param('result')
#         if op.value == op.Operations.add:
#             result.value = first.value + second.value
#         elif op.value == op.Operations.subtract:
#             result.value = first.value - second.value
#         elif op.value == op.Operations.multiply:
#             result.value = first.value * second.value
#         elif op.value == op.Operations.divide:
#             result.value = first.value / second.value
#
#         signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
#         signal.emit_event()
