from persistence import ParameterDefinition
import os
from PySide6 import QtCore

from .base import EventNode, ComputeNode
from .params import StringParam, ListParam, OUTPUT_PLUG, PARAM
from .signal import Signal, OUTPUT_PLUG


class FilesChanged(EventNode):
    signal_definitions = {
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'property:files': ParameterDefinition(ListParam, {'name': 'files', 'value': [StringParam(name='', value='')], 'pluggable': PARAM}, storage='stored', bind_node=False),
    }

    type = 'FilesChanged'
    categories = ['Events']
    description = \
        """The **FilesChange node** watches the *files* path and emits the *event* signal when a change to one of the files occurs.

Parameters:

- *files*: the list of files to watch
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('property:files'))

        self.watcher = QtCore.QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.compute)

        self.update()

    def activate(self):
        super().activate()
        self.update()

    def deactivate(self):
        super().deactivate()
        if self.watcher:
            self.watcher.fileChanged.disconnect(self.compute)

    def update(self):
        if self.restoring:
            return
        files_param = self.get_first_param('files')
        paths = [item.value for item in files_param.value if os.path.isfile(item.value)]

        if paths:
            self.watcher = QtCore.QFileSystemWatcher()
            self.watcher.addPaths(paths)
            if self.is_active():
                self.watcher.fileChanged.connect(self.compute)

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()

        super().compute()
