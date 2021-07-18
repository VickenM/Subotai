from .base import ComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import asyncio
import threading


async def run_command(cmd, callback_fn):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    await callback_fn()


class LoopThread(threading.Thread):
    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()


class MultiProcess(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'MultiProcess'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='process', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='arguments', value='', pluggable=PARAM | INPUT_PLUG))

        self.loop_thread = LoopThread(node=self)
        self.loop_thread.start()

        self.count = 0

    @QtCore.Slot()
    def compute(self):
        self.start_spinner_signal.emit()

        process = self.get_first_param('process')
        arguments = self.get_first_param('arguments')
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)

        cmdline = ' '.join([process.value, arguments.value])
        print(cmdline)

        asyncio.run_coroutine_threadsafe(run_command(cmdline, callback_fn=self.job_complete), self.loop_thread.loop)
        self.count += 1

        super().compute()

    async def job_complete(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.count -= 1
        if not self.count:
            self.stop_spinner_signal.emit()

    def terminate(self):
        loop = self.loop_thread.loop
        loop.call_soon_threadsafe(loop.stop)
