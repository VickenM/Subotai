from .base import BaseNode, ComputeNode, EventNode
from .params import IntParam, FloatParam, StringParam, ListParam
from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM


class Parameter(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Parameter'
        self.color = (150, 150, 150, 255)
        # self.params.append(ListParam(name='type', value=[
        #     IntParam(value='Integer'),
        #     FloatParam(value='Float'),
        #     StringParam(value='String'),
        # ], pluggable=PARAM))
        self.params.append(StringParam(name='param', value='', pluggable=OUTPUT_PLUG | PARAM))

    def set_param_type(self, param_type):
        if param_type == 'Integer':
            self.param = IntParam(name='param', value=0, pluggable=OUTPUT_PLUG)
        elif param_type == 'Float':
            self.param = FloatParam(name='param', value=0.0, pluggable=OUTPUT_PLUG)
        elif param_type == 'String':
            self.param = StringParam(name='param', value='', pluggable=OUTPUT_PLUG)
        elif param_type == 'List':
            self.param = ListParam(name='param', value=[], pluggable=OUTPUT_PLUG)
