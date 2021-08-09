from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode, BaseNode
from .params import StringParam, IntParam, PARAM, ListParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class JoinParam(StringParam):
    def __init__(self, params, format_, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.params = params
        self.format_ = format_

    @property
    def value(self):
        return self.calculate()

    def __call__(self, *args, **kwargs):
        return self.calculate()

    def calculate(self):
        format_ = self.format_()
        # values = {p.name: p() for p in self.params}
        # try:
        #     return format_.format(**values)
        # except:
        #     return ''
        values = [p() for p in self.params]
        try:
            return format_.format(*values)
        except Exception as e:
            print(e)
            return ''


class FormatString(BaseNode):
    categories = ['String']
    description = \
        """
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'FormatString'
        self.color = (150, 150, 150, 255)

        self.string_params = []

        format_ = StringParam(name='format', value='', pluggable=PARAM)
        string0 = StringParam(name='string1', value='', pluggable=PARAM | INPUT_PLUG, node=self)
        self.params.append(format_)
        self.string_params.append(string0)
        self.params.append(string0)
        self.params.append(JoinParam(params=self.string_params, format_=format_, name='string',
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
