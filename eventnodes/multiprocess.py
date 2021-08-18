from .base import ComputeNode
from .params import StringParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import asyncio
import threading

from config import path
import time
import queue


class ProcessControl(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.progress = QtWidgets.QProgressBar()

        self.view = QtWidgets.QToolButton()
        self.view.setIcon(QtGui.QIcon(path + '/icons/view.png'))
        self.view.clicked.connect(lambda: self.log.show())

        self.remove = QtWidgets.QToolButton()
        self.remove.setIcon(QtGui.QIcon(path + '/icons/remove.png'))
        self.remove.setDisabled(True)

        self.cancel = QtWidgets.QToolButton()
        self.cancel.setIcon(QtGui.QIcon(path + '/icons/cancel.png'))

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.remove)
        self.layout.addWidget(self.cancel)
        self.setLayout(self.layout)

        self.log = QtWidgets.QTextBrowser()
        self.log.resize(QtCore.QSize(1000, 500))
        self.log.hide()

        self.item = None

    def setCompleted(self):
        self.remove.setEnabled(True)
        self.item['stale'] = True

    def setTextVisible(self, visible):
        return self.progress.setTextVisible(visible)

    def setAlignment(self, alignment):
        self.progress.setAlignment(alignment)

    def setFormat(self, format_):
        self.progress.setFormat(format_)

    def setValue(self, value):
        self.progress.setValue(value)

    def setMaximum(self, maximum):
        self.progress.setMaximum(maximum)


class Progress(QtWidgets.QScrollArea):
    add_progress = QtCore.Signal(int, dict)
    update_progress = QtCore.Signal(int, str, int, int)
    set_process = QtCore.Signal(object, int)

    def __init__(self, loop_thread):
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumHeight(200)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        self.main_widget = QtWidgets.QWidget(parent=self)
        self.main_widget.setLayout(layout)

        self.setWidget(self.main_widget)

        self.processes = {}
        self.process_id = 0
        self.loop_thread = loop_thread

        self.add_progress.connect(self.do_add_process)
        self.update_progress.connect(self.do_update_process)
        self.set_process.connect(self.do_set_process)

    # Using signals/slots to add download progress bar widgets, because you cant make widgets from different threads.
    # Qt gives error related to setParent

    @QtCore.Slot()
    def do_add_process(self, process_id, item):
        progress = ProcessControl(parent=self.main_widget)
        progress.item = item
        progress.setTextVisible(True)
        progress.setAlignment(QtCore.Qt.AlignCenter)
        progress.setFormat(item.get('cmd'))
        progress.setValue(0)
        progress.remove.clicked.connect(lambda x: self.remove_process(process_id))
        progress.cancel.clicked.connect(lambda x: progress.setCompleted())
        self.processes[process_id] = progress
        # self.layout.addWidget(progress)
        count = self.main_widget.layout().count()
        self.main_widget.layout().insertWidget(count-1, progress)

    def add_process(self, item):
        self.process_id += 1
        self.add_progress.emit(self.process_id, item)
        QtCore.QCoreApplication.processEvents()
        return self.process_id

    def remove_process(self, process_id):
        progress_bar = self.processes[process_id]
        index = self.main_widget.layout().indexOf(progress_bar)
        item = self.main_widget.layout().takeAt(index)
        item.widget().deleteLater()
        del self.processes[process_id]

    @QtCore.Slot(int, int, int)
    def do_update_process(self, process_id, stdout, current, total):
        progress_bar = self.processes.get(process_id)
        if progress_bar:
            progress_bar.setMaximum(int(total))
            progress_bar.setValue(int(current))
            progress_bar.log.append(stdout)

            if current and (current == total):
                progress_bar.setCompleted()

    def update_process(self, process_id, stdout, current, total):
        self.update_progress.emit(process_id, stdout, current, total)

    async def _kill_proc(self, p):
        if p.returncode is None:
            p.terminate()
            await p.wait()

    def kill_proc(self, process):
        asyncio.run_coroutine_threadsafe(self._kill_proc(process), loop=self.loop_thread.loop)

    @QtCore.Slot()
    def do_set_process(self, process, process_id):
        progress_bar = self.processes.get(process_id)
        if progress_bar:
            progress_bar.cancel.clicked.connect(lambda x: self.kill_proc(process))

    def set_proc(self, proc, process_id):
        self.set_process.emit(proc, process_id)


class ConcurrencyControl(QtWidgets.QWidget):
    def __init__(self, queuethread):
        super().__init__()
        self.queuethread = queuethread

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.concurrency = QtWidgets.QSpinBox()
        self.concurrency.setValue(1)
        self.layout.addWidget(self.concurrency)


async def run_command(item, process_id):
    cmd, callback_start, callback_progress, callback_end, callback_error, stale = item.values()
    import shlex
    cmd_parts = [c.encode() for c in shlex.split(cmd)]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
    except Exception as e:
        await callback_error(process_id, e)
        return

    await callback_start(proc, process_id)

    c = None
    while c != '':
        c = await proc.stdout.readline()
        c = c.decode().strip('\n')

        # print(c)
        await callback_progress(process_id, c)

    await proc.wait()
    await callback_end(process_id, proc.returncode)


async def safe_run_command(**args):
    queuethread = args.pop('queuethread')
    await(run_command(**args))


class LoopThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()

    def run(self):
        self.loop.run_forever()


class QueueThread(threading.Thread):
    def __init__(self, queue, concurrency, loop_thread):
        self.concurrency_param = concurrency
        self.queue = queue
        self.loop_thread = loop_thread

        self.count = 0
        self.concurrent = 1
        self._kill = False
        super().__init__()

    def kill(self):
        self._kill = True

    def run(self):
        while True:
            if self._kill:
                return

            if self.count >= self.concurrency_param.value:
                time.sleep(0.1)
                continue

            if self.queue.empty():
                time.sleep(0.1)
                continue

            item_and_process_id = self.queue.get()

            if item_and_process_id['item']['stale']:
                continue

            self.count += 1
            item_and_process_id['queuethread'] = self
            asyncio.run_coroutine_threadsafe(safe_run_command(**item_and_process_id), self.loop_thread.loop)


procs = []


class MultiProcess(ComputeNode):
    categories = ['I/O']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'MultiProcess'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='process', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='arguments', value='', pluggable=PARAM | INPUT_PLUG))
        concurrency = IntParam(name='concurrency', value=0, pluggable=PARAM)
        self.params.append(concurrency)

        self.queue = queue.Queue()

        self.loop_thread = LoopThread()
        self.loop_thread.start()

        self.queue_thread = QueueThread(queue=self.queue, concurrency=concurrency, loop_thread=self.loop_thread)

        self.progress_widget = Progress(loop_thread=self.loop_thread)
        self.concurrency_widget = ConcurrencyControl(self.queue_thread)

        self.queue_thread.concurrent = self.concurrency_widget.concurrency.value()
        self.controls.append((self.progress_widget, None, None))
        self.queue_thread.start()

    @QtCore.Slot()
    def compute(self):
        async def process_error(process_id, exception):
            self.progress_widget.update_process(process_id, str(exception), 100, 100)

            self.queue_thread.count -= 1
            if not self.queue_thread.count:
                self.stop_spinner_signal.emit()

            print(exception)
            self.start_glow_signal.emit(self.error_color)

        async def process_start(proc, process_id):
            procs.append(proc)

            self.progress_widget.set_proc(proc, process_id)
            self.start_spinner_signal.emit()

        async def process_progress(process_id, stdout):
            self.progress_widget.update_process(process_id, stdout, 0, 0)

        async def process_complete(process_id, returncode):
            if returncode == 0:
                self.progress_widget.update_process(process_id, '', 100, 100)
                signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
                signal.emit_event()
            else:
                self.progress_widget.update_process(process_id, '', 0, 100)

            self.queue_thread.count -= 1
            if not self.queue_thread.count:
                self.stop_spinner_signal.emit()

        self.start_spinner_signal.emit()
        self.stop_glow_signal.emit()

        process = self.get_first_param('process')
        arguments = self.get_first_param('arguments')
        cmdline = ' '.join([process.value, arguments.value])

        item = dict(cmd=cmdline, callback_start=process_start, callback_progress=process_progress,
                    callback_end=process_complete, callback_error=process_error, stale=False)
        process_id = self.progress_widget.add_process(item)

        print(cmdline)

        # item = dict(cmd=cmdline, callback_start=process_start, callback_progress=process_progress,
        #             callback_end=process_complete, callback_error=process_error, process_id=process_id, stale=False)
        self.queue.put(dict(item=item, process_id=process_id))

        super().compute()

    def terminate(self):
        # for process_id, progress_bar in self.progress_widget.processes.items():
        #     progress_bar.cancel.clicked.emit()
        # QtCore.QCoreApplication.processEvents()

        loop = self.loop_thread.loop
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.call_soon_threadsafe(loop.stop)

        for p in procs:
            if p.returncode is None:
                p.terminate()

        self.queue_thread.kill()

