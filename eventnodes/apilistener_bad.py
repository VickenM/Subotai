from .base import ComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

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


class LoopThread(threading.Thread):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.loop = asyncio.new_event_loop()

    def run(self):
        print('running')
        self.loop.run_forever()


import time


async def request_consumer(queue, on_response_fn):
    print('entering')
    with requests.Session() as s:
        while True:
            request = queue.get()  # just sending a stirng for GET for now
            print(request)
            # endpoint = request
            response = s.get(request)

            await on_response_fn(response)
            # await asyncio.sleep(1)
            print('response!!!')


class APIListener(ComputeNode):
    categories = ['Events']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'APIListener'

        self.queue = queue.Queue()

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='connected', pluggable=OUTPUT_PLUG))
        self.signals.append(Signal(node=self, name='response', pluggable=OUTPUT_PLUG))
        self.params.append(QueueParam(name='session', value=self.queue, pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='response', value='', pluggable=OUTPUT_PLUG))

        self.loop_thread = LoopThread(node=self)
        self.loop_thread.start()

        print('started loop')
        asyncio.run_coroutine_threadsafe(request_consumer(self.queue, on_response_fn=self.received_response),
                                         self.loop_thread.loop)

    @QtCore.Slot()
    def compute(self):
        # self.start_spinner_signal.emit()
        # asyncio.run_coroutine_threadsafe(request_consumer(self.queue, on_response_fn=self.received_response),
        #                                  self.loop_thread.loop)
        print('putting on queue')
        self.queue.put('https://dog.ceo/api/breeds/image/random')
        # self.stop_spinner_signal.emit()
        super().compute()

    async def received_response(self, response):
        self.start_spinner_signal.emit()

        resp = self.get_first_param('response', pluggable=OUTPUT_PLUG)
        resp.value = response.json()['message']

        signal = self.get_first_signal('response', pluggable=OUTPUT_PLUG)
        signal.emit_event()

        self.stop_spinner_signal.emit()

    def terminate(self):
        loop = self.loop_thread.loop
        loop.call_soon_threadsafe(loop.stop)
