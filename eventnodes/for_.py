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
        self.params.append(IntParam(name='step', value=1, pluggable=INPUT_PLUG | PARAM))

        self.params.append(IntParam(name='current', value=0, pluggable=OUTPUT_PLUG))

        self.description = \
            """The **For node** loops from *start* to *end* and emit an event for each value. *step* controls each step increment.

Parameters:

- *start*: the start value
- *end*: the end value to stop emitting events
- *step*: the step increment
- *current*: the value currently being outputted by the node

Events:

- *finished*: emitted event when reached the end
"""

    def compute(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        finished = self.get_first_signal('finished', pluggable=OUTPUT_PLUG)

        start = self.get_first_param('start')
        end = self.get_first_param('end')
        step = self.get_first_param('step')

        current = self.get_first_param('current')

        for i in range(start.value, end.value, step.value):
            self.start_spinner_signal.emit()
            current.value = i
            self.stop_spinner_signal.emit()
            signal.emit_event()

        finished.emit_event()
