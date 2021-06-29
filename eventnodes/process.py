from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


class Process(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Process'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='process', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='arguments', value='', pluggable=PARAM | INPUT_PLUG))

    @QtCore.Slot()
    def compute(self):
        self.start_spinner_signal.emit()
        import os
        import subprocess, time

        process = self.get_first_param('process')
        arguments = self.get_first_param('arguments')
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)

        cmdline = ' '.join([process.value, arguments.value])
        print(cmdline)
        os.system(cmdline)
        # p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True)
        # output, err = p.communicate()
        #
        # p_status = p.wait()

        signal.emit_event()
        self.stop_spinner_signal.emit()
        super().compute()
