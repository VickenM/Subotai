from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class CopyFile(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'CopyFile'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='source', value='d:\\temp\\source.txt', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='destination', value='d:\\temp\\target.txt', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='destination', value='d:\\temp\\target.txt', pluggable=OUTPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        import shutil
        source = self.get_first_param('source')
        dest = self.get_first_param('destination')
        try:
            shutil.copy2(source(), dest())

            output = self.get_first_param('destination', pluggable=OUTPUT_PLUG)
            output.value = dest.value

            signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
            signal.emit_event()
        finally:
            self.stop_spinner_signal.emit()
        super().compute()
