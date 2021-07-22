from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode, BaseNode
from .params import StringParam, IntParam, PARAM, ListParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class JoinParam(StringParam):
    def __init__(self, params, sep_param, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.params = params
        self.sep_param = sep_param

    @property
    def value(self):
        return self.calculate()

    def __call__(self, *args, **kwargs):
        return self.calculate()

    def calculate(self):
        sep_ = self.sep_param()
        values = [p() for p in self.params]
        return sep_.join(values)


class JoinStringsMulti(BaseNode):
    description = \
        """The **JoinStringMulti node** joins multiple *string#* inputs together with  *separator* in between.
Additional stirng inputs are dynamically added as input connections are made

Parameters:

- *input#*: the nth string
- *separator*: the separator between strings
- *string*: the resulting string from joining the input strings
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'JoinStringsMulti'
        self.color = (150, 150, 150, 255)

        self.string_params = []

        string0 = StringParam(name='string1', value='', pluggable=PARAM | INPUT_PLUG, node=self)
        separator = StringParam(name='separator', value='', pluggable=PARAM | INPUT_PLUG)
        self.params.append(separator)
        self.string_params.append(string0)
        self.params.append(string0)
        self.params.append(JoinParam(params=self.string_params, sep_param=separator, name='string',
                                     pluggable=OUTPUT_PLUG))

    def connected_params(self, connected_param, this_param):
        if not self.string_params[-1].is_connected():
            return

        import appnode

        extra_params_count = len(self.string_params) + 1
        param = StringParam(name='string' + str(extra_params_count), value='', pluggable=PARAM | INPUT_PLUG, node=self)
        self.params.append(param)
        self.string_params.append(param)

        self.ui_node.add_input(appnode.Plug.from_param(param_obj=param))
        self.ui_node.adjust()

    def disconnected_params(self, this_param):
        while (len(self.string_params) > 1) and (not self.string_params[-2].is_connected()):
            param_to_remove = self.params.pop()
            self.string_params.remove(param_to_remove)

            for plug in self.ui_node.inputs:
                if plug.plug_obj == param_to_remove:
                    self.ui_node.remove_input(plug)
                    break
