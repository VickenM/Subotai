from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, BoolParam, IntParam, ListParam, PARAM, SUBTYPE_DIRPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class CurrentDir(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'output:directory': ParameterDefinition(StringParam, {'name': 'directory', 'value': '', 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'CurrentDir'
    categories = ['FileSystem']
    description = \
        """The **CurrentDir node** outputs the current directory to *directory*.

Parameters:

- *directory*: the current directory

"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('output:directory'))

    @ComputeNode.Decorators.show_ui_computation
    @Slot()
    def compute(self):
        import os
        directory = self.get_first_param('directory')
        directory.value = os.getcwd()

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
