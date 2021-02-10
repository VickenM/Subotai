from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

class For(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'For'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.signals.append(Signal(node=self, name='finished', pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='start', value=0, pluggable=INPUT_PLUG|PARAM))
        self.params.append(IntParam(name='end', value=0, pluggable=INPUT_PLUG | PARAM))
        self.params.append(IntParam(name='step', value=0, pluggable=INPUT_PLUG | PARAM))

        self.params.append(IntParam(name='current', value=0, pluggable=OUTPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        finished = self.get_first_signal('finished', pluggable=OUTPUT_PLUG)

        start = self.get_first_param('start')
        end = self.get_first_param('end')
        step = self.get_first_param('step')

        current = self.get_first_param('current')

        for i in range(start.value, end.value, step.value):
            current.value = i
            signal.emit_event()
        finished.emit_event()
        self.stop_spinner_signal.emit()