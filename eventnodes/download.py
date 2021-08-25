from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, PARAM
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import asyncio
import threading
import requests


# class TextProgressBar(QtWidgets.QProgressBar):
#     def __init__(self, text=''):
#         super().__init__()
#         self.text_ = text
#
#     def setText(self, text):
#         self.text_ = text
#
#     def paintEvent(self, paintevent):
#         super().paintEvent(paintevent)
#
#         painter = QtGui.QPainter(self)
#         rect = self.rect()
#
#         painter.setPen(QtGui.QPen(QtGui.Qt.black))
#         rect = painter.boundingRect(rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter, self.text_)
#         painter.drawText(self.rect().adjusted(0, 0, -36, 0), int(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter),
#                          self.text_)


class Progress(QtWidgets.QWidget):
    add_progress = QtCore.Signal(int, str)
    update_progress = QtCore.Signal(str, int, int, int)

    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.add_progress.connect(self.do_add_download)
        self.update_progress.connect(self.do_update_download)

        self.downloads = {}
        self.download_id = 0

    # Using signals/slots to add download progress bar widgets, because you cant make widgets from different threads.
    # Qt gives error related to setParent

    @QtCore.Slot()
    def do_add_download(self, download_id, filename):
        progress = QtWidgets.QProgressBar()  # TextProgressBar()
        progress.setTextVisible(True)
        progress.setAlignment(QtCore.Qt.AlignCenter)
        progress.setFormat(filename + '... waiting')
        progress.setValue(0)
        self.downloads[download_id] = progress
        self.layout.addWidget(progress)

    def add_download(self, filename):
        self.download_id += 1
        self.add_progress.emit(self.download_id, filename)
        return self.download_id

    def remove_download(self, download_id):
        progress_bar = self.downloads[download_id]
        index = self.layout.indexOf(progress_bar)
        item = self.layout.takeAt(index)
        item.widget().deleteLater()
        del self.downloads[download_id]

    @QtCore.Slot(str, int, int, int)
    def do_update_download(self, filename, download_id, received, total):
        if int(received) < int(total):
            progress_bar = self.downloads.get(download_id)
            if progress_bar:
                percent = int(100 * (int(received) / int(total)))
                text = filename + '... ' + str(percent) + '%'
                progress_bar.setFormat(text)
                progress_bar.setMaximum(int(total))
                progress_bar.setValue(int(received))

    def update_download(self, filename, download_id, received, total):
        self.update_progress.emit(filename, download_id, received, total)


async def download(url, filename, progress_id, progress_fn, callback_fn):
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
                    await progress_fn(filename, progress_id, int(accum), int(total))

    await callback_fn(filename, progress_id)


class LoopThread(threading.Thread):
    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()


class Download(ComputeNode):
    type = 'Download'
    categories = ['I/O']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='url', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='filename', value='', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='filename', value='', pluggable=OUTPUT_PLUG))

        self.progress_widget = Progress()
        self.controls.append((self.progress_widget, None, None))

        self.loop_thread = LoopThread(node=self)
        self.loop_thread.start()

        self.count = 0

    @QtCore.Slot()
    def compute(self):
        self.start_spinner_signal.emit()
        self.stop_glow_signal.emit()
        url = self.get_first_param('url')
        filename = self.get_first_param('filename', pluggable=INPUT_PLUG)

        if url.value and filename.value:
            self.start_spinner_signal.emit()

            url = url.value
            filename = filename.value
            progress_id = self.progress_widget.add_download(filename)

            asyncio.run_coroutine_threadsafe(
                download(url, filename, progress_id=progress_id, progress_fn=self.job_progress,
                         callback_fn=self.job_complete),
                self.loop_thread.loop)
            self.count += 1

        super().compute()

    async def job_progress(self, filename, progress_id, received, total):
        self.progress_widget.update_download(filename, progress_id, received, total)

    async def job_complete(self, filename, progress_id):
        filename_ = self.get_first_param('filename', pluggable=OUTPUT_PLUG)
        filename_.value = filename

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.progress_widget.remove_download(progress_id)
        self.count -= 1
        if not self.count:
            self.stop_spinner_signal.emit()

    def terminate(self):
        loop = self.loop_thread.loop
        loop.call_soon_threadsafe(loop.stop)
