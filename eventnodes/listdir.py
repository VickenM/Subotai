from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, BoolParam, IntParam, ListParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class ListDir(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'ListDir'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='directory', value='d:\\temp', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='pattern', value='*.*', pluggable=PARAM))
        self.params.append(BoolParam(name='recursive', value=False, pluggable=PARAM))
        self.params.append(BoolParam(name='fullpaths', value=False, pluggable=PARAM))
        self.params.append(ListParam(name='files', value=[], pluggable=OUTPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        directory = self.get_first_param('directory').value
        recursive = self.get_first_param('recursive').value
        pattern = self.get_first_param('pattern').value
        fullpaths = self.get_first_param('fullpaths').value

        import os
        import glob
        import time
        time.sleep(1)
        files = []
        if recursive:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    if glob.fnmatch.fnmatch(filename, pattern):
                        if fullpaths:
                            files.append(os.path.join(dirpath, filename))
                        else:
                            files.append(filename)
        else:
            for filename in os.listdir(directory):
                if glob.fnmatch.fnmatch(filename, pattern):
                    if fullpaths:
                        files.append(os.path.join(directory, filename))
                    else:
                        files.append(filename)

        output_files = self.get_first_param('files')
        output_files.value.clear()
        for file in files:
            output_files.value.append(StringParam(name='', value=file))

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()

