from PySide2 import QtCore

from .base import EventNode
from .params import StringParam, ListParam, OUTPUT_PLUG, PARAM
from .signal import Signal, OUTPUT_PLUG

import os


class DirChanged(EventNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'DirChanged'
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='directory', value='', pluggable=OUTPUT_PLUG | PARAM))
        self.params.append(ListParam(name='new', value=[], pluggable=OUTPUT_PLUG))
        self.params.append(ListParam(name='removed', value=[], pluggable=OUTPUT_PLUG))

        directory = self.get_first_param('directory').value
        self.watcher = None
        if directory:
            self.watcher = QtCore.QFileSystemWatcher([directory])
            self.watcher = QtCore.QFileSystemWatcher([directory])
            self.watcher.directoryChanged.connect(self.compute)
            self.watcher.fileChanged.connect(self.compute)

        self.current_contents = []
        self.update()

        self.description = \
            """The **DirChange node** watches the *directory* path and emits the *event* signal when a change to the directory occurs.

Parameters:

- *directory*: the directory path to watch
- *new*: the list of files in *directory* that are new
- *removed*: the list of files in *directory* that were removed
"""

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

        # TODO: I want to remove the old paths from the watcher. but if you add in a root folder like d:\ it removePaths(...) fails to remove it

        # if self.watcher.directories():
        #     self.watcher.removePath(self.watcher.directories())
        # if directory:
        #     self.watcher.addPath(directory)

        self.current_contents = []

        if os.path.isdir(directory):  # if-statement just to prevent Qt List Empty warnings
            self.watcher = QtCore.QFileSystemWatcher([directory])
            self.watcher.directoryChanged.connect(self.compute)
            self.watcher.fileChanged.connect(self.compute)
            self.current_contents = os.listdir(directory)
        else:
            self.watcher = None

    @QtCore.Slot()
    def compute(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        new = self.get_first_param('new')
        removed = self.get_first_param('removed')

        directory = self.watcher.directories()[-1]
        current = os.listdir(directory)

        new.value.clear()
        for f in set(current) - set(self.current_contents):
            new.value.append(StringParam(name='', value=f))

        removed.value.clear()
        for f in set(self.current_contents) - set(current):
            removed.value.append(StringParam(name='', value=f))

        self.current_contents = current

        signal.emit_event()

        super().compute()
