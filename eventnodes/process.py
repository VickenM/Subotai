from persistence import ParameterDefinition
from .base import ComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore


class Process(ComputeNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:process': ParameterDefinition(StringParam, {'name': 'process', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:arguments': ParameterDefinition(StringParam, {'name': 'arguments', 'value': '', 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'Process'
    categories = ['I/O']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('input:process'))
        self.params.append(self.create_parameter('input:arguments'))

    @ComputeNode.Decorators.show_ui_computation
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
