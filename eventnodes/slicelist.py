from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode, BaseNode
from .params import StringParam, IntParam, PARAM, ListParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class SliceParam(ListParam):
    def __init__(self, start, end, list_param, name=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.start = start
        self.end = end
        self.list_param = list_param

    @property
    def value(self):
        return self.calculate()

    def __call__(self, *args, **kwargs):
        return self.calculate()

    def calculate(self):
        return self.list_param.value[self.start.value:self.end.value]


class SliceList(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (150, 150, 150, 255)
        self.type = 'SliceList'

        start_param = IntParam(name='start', value=0, pluggable=PARAM | INPUT_PLUG)
        end_param = IntParam(name='end', value=-1, pluggable=PARAM | INPUT_PLUG)
        list_param = ListParam(name='list', value=[], pluggable=INPUT_PLUG)

        self.params.append(start_param)
        self.params.append(end_param)
        self.params.append(list_param)
        self.params.append(
            SliceParam(name='list', start=start_param, end=end_param, list_param=list_param, pluggable=OUTPUT_PLUG))

        # def compute(self):
        #     start = self.get_first_param('start')
        #     end = self.get_first_param('end')
        #     in_list = self.get_first_param('list', pluggable=INPUT_PLUG)
        #     out_list = self.get_first_param('list', pluggable=OUTPUT_PLUG)
        #
        #     _parts = source().split(pattern())
        #
        #     parts.value.clear()
        #     for p in _parts:
        #         parts.value.append(StringParam(name='', value=p))
        #
        #     signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        #     signal.emit_event()
        #     super().compute()
