from PySide2 import QtCore

from .base import EventNode
from .params import StringParam, ListParam, OUTPUT_PLUG, PARAM
from .signal import Signal, OUTPUT_PLUG


class FilesChanged(EventNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'FilesChanged'
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ListParam(
            name='files',
            value=[StringParam(name='', value=''),
                   ],
            pluggable=PARAM))

        # watch_directory = self.get_first_param('files').value
        self.watcher = QtCore.QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.compute)

        self.update()

    def activate(self):
        directory = self.get_first_param('directory').value
        self.watcher.removePaths(self.watcher.directories())
        self.watcher.addPath(directory)
        super().activate()

    def deactivate(self):
        self.watcher.removePaths(self.watcher.directories())
        super().deactivate()

    def update(self):
        files_param = self.get_first_param('files')
        paths = [item.value for item in files_param.value]
        if self.watcher.files():
            self.watcher.removePaths(self.watcher.files())
        if paths:
            self.watcher.addPaths(paths)

    def compute(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()

        super().compute()
