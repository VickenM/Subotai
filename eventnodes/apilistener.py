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

from eventnodes.params import Param
import queue


class QueueParam(Param):
    def __init__(self, name='', value=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = queue.Queue
        self._value = value

    def to_dict(self):
        return None


class LoopThread(threading.Thread):
    def __init__(self, node):
        self.node = node
        self.loop = asyncio.new_event_loop()
        super().__init__()

    def run(self):
        try:
            self.loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
            if pending:
                self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self.loop.close()


import time


async def request_consumer(queue, on_response_fn):
    with requests.Session() as s:
        while True:
            if queue.empty():  # TODO this is total hacks.
                await asyncio.sleep(0.05)
                continue

            request = queue.get()  # just sending a stirng for GET for now
            if request is False:
                return
            endpoint = request
            response = s.get(endpoint)

            await on_response_fn(response)


class APIListener(ComputeNode):
    legacy_aliases = ('nodes.apilistener.APIListener',)
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:connected': ('connected', OUTPUT_PLUG),
        'output:received': ('received', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'output:session': ParameterDefinition(QueueParam, {'name': 'session', 'pluggable': OUTPUT_PLUG}, storage='transient', bind_node=False),
        'output:response': ParameterDefinition(StringParam, {'name': 'response', 'value': '', 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    categories = ['I/O']
    type = 'APIListener'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue.Queue()

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:connected'))
        self.signals.append(self.create_signal('output:received'))
        self.params.append(QueueParam(name='session', value=self.queue, pluggable=OUTPUT_PLUG))
        self.params.append(self.create_parameter('output:response'))

        self.loop_thread = LoopThread(node=self)
        self.consumer = None
        if not self.restoring:
            self.activate_resources()

    @QtCore.Slot()
    def compute(self):
        super().compute()

    async def received_response(self, response):
        self.start_spinner_signal.emit()

        resp = self.get_first_param('response', pluggable=OUTPUT_PLUG)
        resp.value = response.json()['message']

        signal = self.get_first_signal('received', pluggable=OUTPUT_PLUG)
        signal.emit_event()

        self.stop_spinner_signal.emit()

    def terminate(self):
        self.queue.put(False)
        loop = self.loop_thread.loop
        if self.loop_thread.is_alive():
            if self.consumer:
                self.consumer.cancel()
            loop.call_soon_threadsafe(loop.stop)
            self.loop_thread.join(timeout=5)
        if not self.loop_thread.is_alive() and not loop.is_closed():
            loop.close()

    def activate_resources(self):
        if self.loop_thread.loop.is_closed():
            self.queue = queue.Queue()
            self.get_first_param('session')._value = self.queue
            self.loop_thread = LoopThread(node=self)
        if not self.loop_thread.is_alive():
            self.loop_thread.start()
            self.consumer = asyncio.run_coroutine_threadsafe(
                request_consumer(self.queue, on_response_fn=self.received_response), self.loop_thread.loop)

    def pause_resources(self):
        self.terminate()
