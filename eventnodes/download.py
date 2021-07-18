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

        self.downloads = {}

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def add_download(self, filename):
        progress = QtWidgets.QProgressBar(parent=self)
        self.downloads[filename] = progress
        self.layout.addWidget(progress)

    def remove_download(self, filename):
        progress = self.downloads[filename]
        index = self.layout.indexOf(progress)
        item = self.layout.takeAt(index)
        item.widget().deleteLater()
        del self.downloads[filename]

    def update_download(self, filename, retrieved, total):
        progress = self.downloads[filename]
        if total:
            progress.setMaximum(int(total))

        if int(retrieved) != int(total):
            progress.setValue(int(retrieved))


async def download(url, filename, progress_fn, callback_fn):
    import requests
    with requests.get(url, stream=True) as r:
        total = r.headers.get('content-length')

        r.raise_for_status()
        with open(filename, 'wb') as f:
            accum = 0
            for chunk in r.iter_content(chunk_size=8192*2):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                if chunk:
                    f.write(chunk)
                    accum += len(chunk)
                    await progress_fn(filename, accum, total)

    await callback_fn(filename)


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
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)

        if url.value and filename.value:
            if filename not in self.progress_widget.downloads.keys():
                url = url.value
                filename = filename.value

                asyncio.run_coroutine_threadsafe(
                    download(url, filename, progress_fn=self.progress, callback_fn=self.job_complete),
                    self.loop_thread.loop)
                self.count += 1
                self.progress_widget.add_download(filename=filename)

        super().compute()

    async def progress(self, filename, retrieved, total):
        # print('{filename} {retrieved}/{total}'.format(filename=filename, retrieved=retrieved, total=total))
        self.progress_widget.update_download(filename, retrieved, total)

    async def job_complete(self, filename):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.progress_widget.remove_download(filename)
        self.count -= 1
        if not self.count:
            self.stop_spinner_signal.emit()

    def terminate(self):
        loop = self.loop_thread.loop
        loop.call_soon_threadsafe(loop.stop)
