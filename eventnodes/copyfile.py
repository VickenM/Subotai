from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class CopyFile(ComputeNode):
    categories = ['FileSystem']
    description = \
        """The **CopyFile node** copies the file in the *source* path to the *destination* path.

Parameters:

- *source*: Path of the file to copy
- *destination*: Path of where to copy the source file to
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'CopyFile'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='source', value='d:\\temp\\source.txt', pluggable=PARAM | INPUT_PLUG,
                                       subtype=SUBTYPE_FILEPATH))
        self.params.append(StringParam(name='destination', value='d:\\temp\\target.txt', pluggable=PARAM | INPUT_PLUG,
                                       subtype=SUBTYPE_FILEPATH))
        self.params.append(StringParam(name='destination', value='d:\\temp\\target.txt', pluggable=OUTPUT_PLUG))

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
