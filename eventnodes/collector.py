from persistence import ParameterDefinition
from persistence import StateField
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class Collector(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'input:emit': ('emit', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    state_fields = {'pending_items': StateField('_items', [])}
    parameter_definitions = {
        'input:item': ParameterDefinition(StringParam, {'name': 'item', 'value': '', 'pluggable': INPUT_PLUG}, storage='stored', bind_node=False),
        'output:items': ParameterDefinition(ListParam, {'name': 'items', 'value': [], 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'Collector'
    categories = ['Flow Control']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('input:emit'))
        self.signals.append(self.create_signal('output:event'))

        self.params.append(self.create_parameter('input:item'))
        self.params.append(self.create_parameter('output:items'))
        self._items = []

    @Slot()
    def trigger(self):
        super().trigger()

    @Slot()
    def collect(self):
        item = self.get_first_param('item')
        self._items.append(item.value)

    def map_signal(self, signal):
        if signal == 'event':
            return self.collect
        elif signal == 'emit':
            return self.trigger

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()

        output_items = self.get_first_param('items', pluggable=OUTPUT_PLUG)

        output_items.value.clear()
        for i in self._items:
            output_items.value.append(StringParam(name='', value=i))

        self._items = []

        event = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        event.emit_event()
