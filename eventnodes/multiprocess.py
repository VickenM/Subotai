from .base import ComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import asyncio
import threading

from config import path


class ProcessControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
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

    def setCompleted(self):
        self.remove.setEnabled(True)

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


class Progress(QtWidgets.QWidget):
    add_progress = QtCore.Signal(int, str)
    update_progress = QtCore.Signal(int, str, int, int)
    set_process = QtCore.Signal(object, int)

    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.add_progress.connect(self.do_add_process)
        self.update_progress.connect(self.do_update_process)
        self.set_process.connect(self.do_set_process)

        self.processes = {}
        self.process_id = 0

    # Using signals/slots to add download progress bar widgets, because you cant make widgets from different threads.
    # Qt gives error related to setParent

    @QtCore.Slot()
    def do_add_process(self, process_id, cmdline):
        progress = ProcessControl()
        progress.setTextVisible(True)
        progress.setAlignment(QtCore.Qt.AlignCenter)
        progress.setFormat(cmdline)
        progress.setValue(0)
        progress.remove.clicked.connect(lambda x: self.remove_process(process_id))
        self.processes[process_id] = progress
        self.layout.addWidget(progress)

    def add_process(self, cmdline):
        self.process_id += 1
        self.add_progress.emit(self.process_id, cmdline)
        QtCore.QCoreApplication.processEvents()
        return self.process_id

    def remove_process(self, process_id):
        progress_bar = self.processes[process_id]
        index = self.layout.indexOf(progress_bar)
        item = self.layout.takeAt(index)
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

    @QtCore.Slot()
    def do_set_process(self, process, process_id):
        def kill_proc(p):
            if p.returncode is None:
                p.terminate()

        progress_bar = self.processes.get(process_id)
        if progress_bar:
            progress_bar.cancel.clicked.connect(lambda: kill_proc(process))

    def set_proc(self, proc, process_id):
        self.set_process.emit(proc, process_id)


async def run_command(cmd, callback_start, callback_progress, callback_end, callback_error, process_id):
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
        print(c)
        await callback_progress(process_id, c)

    await proc.wait()
    await callback_end(process_id, proc.returncode)


class LoopThread(threading.Thread):
    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()


class MultiProcess(ComputeNode):
    categories = ['I/O']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'MultiProcess'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='process', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='arguments', value='', pluggable=PARAM | INPUT_PLUG))

        self.progress_widget = Progress()
        self.controls.append((self.progress_widget, None, None))

        self.loop_thread = LoopThread(node=self)
        self.loop_thread.start()

        self.count = 0

    @QtCore.Slot()
    def compute(self):
        async def process_error(process_id, exception):
            self.progress_widget.update_process(process_id, '', 100, 100)

            self.count -= 1
            if not self.count:
                self.stop_spinner_signal.emit()
            print(exception)
            self.start_glow_signal.emit(self.error_color)

        async def process_start(proc, process_id):
            self.progress_widget.set_proc(proc, process_id)

        async def process_progress(process_id, stdout):
            self.progress_widget.update_process(process_id, stdout, 0, 0)

        async def process_complete(process_id, returncode):
            self.progress_widget.update_process(process_id, '', 100, 100)

            if returncode == 0:
                signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
                signal.emit_event()

            self.count -= 1
            if not self.count:
                self.stop_spinner_signal.emit()

        self.start_spinner_signal.emit()

        process = self.get_first_param('process')
        arguments = self.get_first_param('arguments')
        cmdline = ' '.join([process.value, arguments.value])
        process_id = self.progress_widget.add_process(cmdline)

        print(cmdline)

        self.count += 1
        asyncio.run_coroutine_threadsafe(
            run_command(cmdline, callback_start=process_start, callback_progress=process_progress,
                        callback_end=process_complete, callback_error=process_error, process_id=process_id),
            self.loop_thread.loop)

        super().compute()

    def terminate(self):
        loop = self.loop_thread.loop
        loop.call_soon_threadsafe(loop.stop)
