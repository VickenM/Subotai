from PySide2 import QtCore

from .base import EventNode
from .params import StringParam, ListParam, OUTPUT_PLUG, PARAM
from .signal import Signal, OUTPUT_PLUG


class DirChanged(EventNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'DirChanged'
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='directory', value='', pluggable=OUTPUT_PLUG | PARAM))

        watch_directory = self.get_first_param('directory').value
        self.watcher = QtCore.QFileSystemWatcher([watch_directory])
        self.watcher.directoryChanged.connect(self.compute)
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
        directory = self.get_first_param('directory').value

        if self.watcher.directories():
            self.watcher.removePaths(self.watcher.directories())
        if directory:
            self.watcher.addPath(directory)

    def compute(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()

        super().compute()
