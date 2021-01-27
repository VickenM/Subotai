from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM, ListParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class SplitString(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'SplitString'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='source', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='pattern', value='\\', pluggable=PARAM | INPUT_PLUG))
        self.params.append(ListParam(name='parts', value=[], pluggable=OUTPUT_PLUG))

    def compute(self):
        source = self.get_first_param('source')
        pattern = self.get_first_param('pattern')
        parts = self.get_first_param('parts')

        _parts = source().split(pattern())

        parts.value.clear()
        for p in _parts:
            parts.value.append(StringParam(name='', value=p))

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        super().compute()
