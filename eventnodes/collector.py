from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class Collector(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Collector'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='emit', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))

        self.params.append(StringParam(name='item', value='', pluggable=INPUT_PLUG))
        self.params.append(ListParam(name='items', value=[], pluggable=OUTPUT_PLUG))
        self._items = []

    @Slot(str)
    def trigger(self, event):
        super().trigger(event)

    @Slot(str)
    def collect(self, event):
        item = self.get_first_param('item')
        self._items.append(item.value)

    def map_signal(self, signal):
        if signal == 'event':
            return self.collect
        elif signal == 'emit':
            return self.trigger

    def compute(self):
        output_items = self.get_first_param('items', pluggable=OUTPUT_PLUG)

        output_items.value.clear()
        for i in self._items:
            output_items.value.append(StringParam(name='', value=i))

        self._items = []

        event = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        event.emit_event()
