from .base import BaseNode, ComputeNode, EventNode
from .params import IntParam, FloatParam, StringParam, ListParam, Param
from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM


class ToStr(StringParam):
    def __init__(self, int_param, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.int_param = int_param

    @property
    def value(self):
        return str(self.int_param.value)

    def __call__(self, *args, **kwargs):
        return str(self.int_param.value)


class IntToStr(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'IntToStr'
        self.color = (150, 150, 150, 255)
        input_param = IntParam(name='integer', value=0, pluggable=INPUT_PLUG)
        self.params.append(input_param)
        self.params.append(ToStr(int_param=input_param, name='string', pluggable=OUTPUT_PLUG))
