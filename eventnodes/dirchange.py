from persistence import ParameterDefinition
from PySide6 import QtCore

from .base import EventNode, ComputeNode
from .params import StringParam, ListParam, OUTPUT_PLUG, PARAM, SUBTYPE_DIRPATH
from .signal import Signal, OUTPUT_PLUG

import os


class DirChanged(EventNode):
    signal_definitions = {
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'output:directory': ParameterDefinition(StringParam, {'name': 'directory', 'value': '', 'pluggable': OUTPUT_PLUG | PARAM, 'subtype': SUBTYPE_DIRPATH}, storage='stored', bind_node=False),
        'output:new': ParameterDefinition(ListParam, {'name': 'new', 'value': [], 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
        'output:removed': ParameterDefinition(ListParam, {'name': 'removed', 'value': [], 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'DirChanged'
    categories = ['Events']
    description = \
        """The **DirChange node** watches the *directory* path and emits the *event* signal when a change to the directory occurs.

Parameters:

- *directory*: the directory path to watch
- *new*: the list of files in *directory* that are new
- *removed*: the list of files in *directory* that were removed
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('output:event'))
        self.params.append(
            self.create_parameter('output:directory'))
        self.params.append(self.create_parameter('output:new'))
        self.params.append(self.create_parameter('output:removed'))

        directory = self.get_first_param('directory').value
        self.watcher = None  # QtCore.QFileSystemWatcher([directory])
        self.current_contents = []
        self.update()

    def activate(self):
        super().activate()
        self.update()

    def deactivate(self):
        super().deactivate()
        if self.watcher:
            self.watcher.directoryChanged.disconnect(self.compute)

    def update(self):
        if self.restoring:
            return
        directory = self.get_first_param('directory').value

        self.current_contents = []

        if os.path.isdir(directory):  # if-statement just to prevent Qt List Empty warnings
            self.watcher = QtCore.QFileSystemWatcher([directory])
            self.current_contents = os.listdir(directory)

            if self.is_active():
                self.watcher.directoryChanged.connect(self.compute)

    @ComputeNode.Decorators.show_ui_computation
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
