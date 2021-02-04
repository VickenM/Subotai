from .base import BaseNode, ComputeNode, EventNode
from .params import IntParam, FloatParam, StringParam, ListParam, BoolParam
from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM


class StringParameter(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'StringParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(StringParam(name='param', value='', pluggable=OUTPUT_PLUG | PARAM))


class IntegerParameter(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'IntegerParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(IntParam(name='param', value=0, pluggable=OUTPUT_PLUG | PARAM))


class FloatParameter(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'FloatParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(FloatParam(name='param', value=0.0, pluggable=OUTPUT_PLUG | PARAM))


class BooleanParameter(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'BooleanParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(BoolParam(name='param', value=True, pluggable=OUTPUT_PLUG | PARAM))

