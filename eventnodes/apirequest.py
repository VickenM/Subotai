from .base import ComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import requests
import asyncio
import threading

from eventnodes.apilistener import QueueParam


class APIRequest(ComputeNode):
    categories = ['I/O']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'APIRequest'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(QueueParam(name='session', value=None, pluggable=INPUT_PLUG))
        self.params.append(
            StringParam(name='request', value='https://dog.ceo/api/breeds/image/random', pluggable=INPUT_PLUG | PARAM))

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
