from persistence import ParameterDefinition
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, PARAM
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore

import requests
import asyncio
import threading

from .apilistener import QueueParam


class APIRequest(ComputeNode):
    legacy_aliases = ('nodes.apirequest.APIRequest',)
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:session': ParameterDefinition(QueueParam, {'name': 'session', 'pluggable': INPUT_PLUG}, storage='transient', bind_node=False),
        'input:request': ParameterDefinition(StringParam, {'name': 'request', 'value': 'n', 'pluggable': INPUT_PLUG | PARAM}, storage='stored', bind_node=False),
    }

    categories = ['I/O']
    type = 'APIRequest'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(QueueParam(name='session', value=None, pluggable=INPUT_PLUG))
        self.params.append(
            self.create_parameter('input:request'))

    @QtCore.Slot()
    def compute(self):
        self.start_spinner_signal.emit()
        session = self.get_first_param('session')
        request = self.get_first_param('request')

        if session.value and request.value:
            session.value.put(request.value)

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()

        self.stop_spinner_signal.emit()
        super().compute()
