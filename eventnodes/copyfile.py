from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class CopyFile(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:source': ParameterDefinition(StringParam, {'name': 'source', 'value': 'd:\\temp\\source.txt', 'pluggable': PARAM | INPUT_PLUG, 'subtype': SUBTYPE_FILEPATH}, storage='stored', bind_node=False),
        'input:destination': ParameterDefinition(StringParam, {'name': 'destination', 'value': 'd:\\temp\\target.txt', 'pluggable': PARAM | INPUT_PLUG, 'subtype': SUBTYPE_FILEPATH}, storage='stored', bind_node=False),
        'output:destination': ParameterDefinition(StringParam, {'name': 'destination', 'value': 'd:\\temp\\target.txt', 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'CopyFile'
    categories = ['FileSystem']
    description = \
        """The **CopyFile node** copies the file in the *source* path to the *destination* path.

Parameters:

- *source*: Path of the file to copy
- *destination*: Path of where to copy the source file to
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('input:source'))
        self.params.append(self.create_parameter('input:destination'))
        self.params.append(self.create_parameter('output:destination'))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        import shutil
        source = self.get_first_param('source')
        dest = self.get_first_param('destination')
        try:
            shutil.copy2(source(), dest())

            output = self.get_first_param('destination', pluggable=OUTPUT_PLUG)
            output.value = dest.value
        finally:
            self.stop_spinner_signal.emit()
            signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
            signal.emit_event()
        super().compute()
