from .base import BaseNode, ComputeNode, EventNode
from .params import IntParam, FloatParam, StringParam, ListParam, Param
from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM


class ToStr(StringParam):
    def __init__(self, int_param, zeropad_param, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.int_param = int_param
        self.zeropad_param = zeropad_param

    @property
    def value(self):
        fmt = '{{:0{}d}}'.format(self.zeropad_param.value)
        return fmt.format(self.int_param.value)  # str(self.int_param.value)

    def __call__(self, *args, **kwargs):
        return self.value()


class IntToStr(BaseNode):
    categories = ['Data']
    description = \
        """The **IntToStr node** converts Integer parameter values to Strings.

Parameters:

- *integer*: the input integer
- *string*: the output string representation of the integer
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'IntToStr'
        self.color = (150, 150, 150, 255)
        input_param = IntParam(name='integer', value=0, pluggable=INPUT_PLUG)
        zeropard_param = IntParam(name='zeropad', value=0, pluggable=PARAM)
        self.params.append(input_param)
        self.params.append(zeropard_param)
        self.params.append(
            ToStr(int_param=input_param, zeropad_param=zeropard_param, name='string', pluggable=OUTPUT_PLUG))
