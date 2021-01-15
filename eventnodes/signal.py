from PySide2 import QtCore

INPUT_PLUG = 1
OUTPUT_PLUG = 2


class Signal(QtCore.QObject):
    computed = QtCore.Signal(str)

    def __init__(self, node, name, pluggable=OUTPUT_PLUG):
        super().__init__()
        self.node = node
        self.name = name
        self.pluggable = pluggable  # must be either input or output, cant be None

    def emit_event(self):
        self.computed.emit(self.name)

    def get_pluggable(self):
        return self.pluggable
