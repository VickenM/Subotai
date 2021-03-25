from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class Counter(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Counter'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='reset', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))

        self.params.append(IntParam(name='initial', value=0, pluggable=INPUT_PLUG | PARAM))
        self.params.append(IntParam(name='value', value=0, pluggable=OUTPUT_PLUG))

    @Slot(str)
    def trigger(self, event):
        super().trigger(event)

    @Slot(str)
    def reset(self, event):
        item = self.get_first_param('value')
        initial = self.get_first_param('initial')
        item.value = initial.value

    def map_signal(self, signal):
        if signal == 'reset':
            return self.reset
        elif signal == 'event':
            return self.trigger

    def compute(self):
        self.start_spinner_signal.emit()
        event = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        item = self.get_first_param('value')
        self.stop_spinner_signal.emit()
        event.emit_event()
        item.value = item.value + 1
