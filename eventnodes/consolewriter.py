from persistence import ParameterDefinition
from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide6.QtCore import Slot


class ConsoleWriter(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'property:prefix': ParameterDefinition(StringParam, {'name': 'prefix', 'value': '%m/%d/%Y, %H:%M:%S', 'pluggable': PARAM}, storage='stored', bind_node=False),
        'input:message': ParameterDefinition(StringParam, {'name': 'message', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'ConsoleWriter'
    categories = ['I/O']
    description = \
        """The **ConsoleWriter node** outputs the text in *message* to the system console.
The *prefix* parameter can be used to add prefix text to the message line and accepts date time directives by Python's strftime function.
[See the link for a complete list of strftime directives](https://strftime.org/)


Parameters:

- *prefix*: Prefix text to message line
- *message*: text line to output to the system console
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('property:prefix'))
        self.params.append(self.create_parameter('input:message'))

    @ComputeNode.Decorators.show_ui_computation
    @Slot()
    def compute(self):
        self.start_spinner_signal.emit()
        prefix = self.get_first_param('prefix')

        from datetime import datetime

        now = datetime.now()
        date_time = now.strftime(prefix.value)

        message = self.get_first_param('message').value

        output = '{} {}'.format(date_time, message)
        print(output)

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
