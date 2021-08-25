from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, BoolParam, IntParam, ListParam, PARAM, SUBTYPE_DIRPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class CurrentDir(ComputeNode):
    type = 'CurrentDir'
    categories = ['FileSystem']
    description = \
        """The **CurrentDir node** outputs the current directory to *directory*.

Parameters:

- *directory*: the current directory

"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='directory', value='', pluggable=OUTPUT_PLUG))

    @ComputeNode.Decorators.show_ui_computation
    @Slot()
    def compute(self):
        import os
        directory = self.get_first_param('directory')
        directory.value = os.getcwd()

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
