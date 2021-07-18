from .base import ComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import asyncio
import threading


class Progress(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def add_download(self):
        progress = QtWidgets.QProgressBar()
        self.layout.addWidget(progress)
        return progress

    def remove_download(self, progress):
        index = self.layout.indexOf(progress)
        item = self.layout.takeAt(index)
        item.widget().deleteLater()


async def download(url, filename, progress_bar, callback_fn):
    import requests
    with requests.get(url, stream=True) as r:
        total = r.headers.get('content-length')

        r.raise_for_status()
        with open(filename, 'wb') as f:
            accum = 0
            for chunk in r.iter_content(chunk_size=8192 * 2):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                if chunk:
                    f.write(chunk)
                    accum += len(chunk)
                    if int(accum) != int(total):
                        if progress_bar:
                            progress_bar.setMaximum(int(total))
                            progress_bar.setValue(int(accum))

    if callback_fn and progress_bar:
        await callback_fn(progress_bar)


class LoopThread(threading.Thread):
    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()


class Download(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Download'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='url', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='filename', value='', pluggable=PARAM | INPUT_PLUG))

        self.progress_widget = Progress()
        self.controls.append((self.progress_widget, None, None))

        self.loop_thread = LoopThread(node=self)
        self.loop_thread.start()

        self.count = 0

    @QtCore.Slot()
    def compute(self):
        self.start_spinner_signal.emit()

        url = self.get_first_param('url')
        filename = self.get_first_param('filename')

        if url.value and filename.value:
            url = url.value
            filename = filename.value
            progress_bar = self.progress_widget.add_download()

            asyncio.run_coroutine_threadsafe(
                download(url, filename, progress_bar=progress_bar, callback_fn=self.job_complete),
                self.loop_thread.loop)
            self.count += 1

        super().compute()

    async def job_complete(self, progress_bar):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.progress_widget.remove_download(progress_bar)
        self.count -= 1
        if not self.count:
            self.stop_spinner_signal.emit()

    def terminate(self):
        loop = self.loop_thread.loop
        loop.call_soon_threadsafe(loop.stop)
