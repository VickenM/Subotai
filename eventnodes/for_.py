from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class For(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
        'output:finished': ('finished', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:start': ParameterDefinition(IntParam, {'name': 'start', 'value': 0, 'pluggable': INPUT_PLUG | PARAM}, storage='stored', bind_node=False),
        'input:end': ParameterDefinition(IntParam, {'name': 'end', 'value': 0, 'pluggable': INPUT_PLUG | PARAM}, storage='stored', bind_node=False),
        'input:step': ParameterDefinition(IntParam, {'name': 'step', 'value': 1, 'pluggable': INPUT_PLUG | PARAM}, storage='stored', bind_node=False),
        'output:current': ParameterDefinition(IntParam, {'name': 'current', 'value': 0, 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'For'
    categories = ['Flow Control']
    description = \
        """The **For node** loops from *start* to *end* and emit an event for each value. *step* controls each step increment.

Parameters:

- *start*: the start value
- *end*: the end value to stop emitting events
- *step*: the step increment
- *current*: the value currently being outputted by the node

Events:

- *finished*: emitted event when reached the end
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.signals.append(self.create_signal('output:finished'))
        self.params.append(self.create_parameter('input:start'))
        self.params.append(self.create_parameter('input:end'))
        self.params.append(self.create_parameter('input:step'))

        self.params.append(self.create_parameter('output:current'))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        finished = self.get_first_signal('finished', pluggable=OUTPUT_PLUG)

        start = self.get_first_param('start')
        end = self.get_first_param('end')
        step = self.get_first_param('step')

        current = self.get_first_param('current')

        for i in range(start.value, end.value+1, step.value):
            QtCore.QCoreApplication.processEvents()

            self.start_spinner_signal.emit()
            current.value = i
            signal.emit_event()
            self.stop_spinner_signal.emit()

        finished.emit_event()
