from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class ZipFile(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'ZipFile'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='source', value='D:\\projects\\python\\node2\\tmp\\src', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='zipfile', value='D:\\projects\\python\\node2\\tmp\\wicked.zip', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='zipfile', value='', pluggable=OUTPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        source = self.get_first_param('source', pluggable=INPUT_PLUG)
        zip_file = self.get_first_param('zipfile', pluggable=INPUT_PLUG)

        from zipfile import ZipFile
        import os

        fullpaths = []
        for root, directories, files in os.walk(source()):
            for filename in files:
                fullpath = os.path.join(root, filename)
                fullpaths.append(fullpath)

        with ZipFile(zip_file(), 'w') as z:
            for fullpath in fullpaths:
                z.write(fullpath)

        output = self.get_first_param('zipfile', pluggable=OUTPUT_PLUG)
        output.value = zip_file.value

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.stop_spinner_signal.emit()
        super().compute()


