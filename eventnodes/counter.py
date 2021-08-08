from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class Counter(ComputeNode):
    categories = ['Flow Control']
    description = \
        """The **Counter node** emits the *event* signal each time it increments the *value* parameter by *increment*.

Parameters:

- *initial*: the starting value to count from
- *increment*: the value to increment by
- *value*: the current count

Signals:

- *reset*: When this signal is triggered, *value* gets reset to *inital* value
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Counter'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='reset', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))

        self.params.append(IntParam(name='initial', value=0, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='increment', value=1, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='value', value=0, pluggable=OUTPUT_PLUG))

    def map_signal(self, signal):
        if signal == 'reset':
            return self.reset
        elif signal == 'event':
            return self.trigger

    @Slot()
    def trigger(self):
        self.compute()

    @Slot()
    def reset(self):
        item = self.get_first_param('value')
        initial = self.get_first_param('initial')
        item.value = initial.value

    @ComputeNode.Decorators.show_ui_computation
    @Slot()
    def compute(self):
        QtCore.QCoreApplication.processEvents()
        self.start_spinner_signal.emit()
        event = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        item = self.get_first_param('value')
        increment = self.get_first_param('increment')
        self.stop_spinner_signal.emit()
        event.emit_event()
        item.value += increment.value
