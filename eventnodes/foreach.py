from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, ListParam, IntParam, EnumParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class ForEach(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'ForEach'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.signals.append(Signal(node=self, name='finished', pluggable=OUTPUT_PLUG))
        self.params.append(ListParam(name='items', value=[
            # StringParam('', value="D:\\projects\\python\\node2\\tmp\\sklavos.zip")
        ], pluggable=PARAM | INPUT_PLUG))

        self.params.append(StringParam(name='item', value='', pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='index', value=0, pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='count', value=0, pluggable=OUTPUT_PLUG))

        self.description = \
            """The **ForEach node** loops each value in the *items* parameter and emit an event for each value.

Parameters:

- *items*: the list of items
- *item*: the current item being emitted
- *index*: the index number of hte current item
- *count*: the total number of items in the list


Events:

- *finished*: emitted event when reached the end
"""

    @Slot()
    def compute(self):
        items = self.get_first_param('items')
        item_output = self.get_first_param('item', pluggable=OUTPUT_PLUG)
        index_output = self.get_first_param('index', pluggable=OUTPUT_PLUG)
        count_output = self.get_first_param('count', pluggable=OUTPUT_PLUG)

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        finished = self.get_first_signal('finished', pluggable=OUTPUT_PLUG)

        count = len(items.value)
        for index, item in enumerate(items.value):
            QtCore.QCoreApplication.processEvents()
            self.start_spinner_signal.emit()
            item_output.value = item.value
            count_output.value = count
            index_output.value = index
            self.stop_spinner_signal.emit()
            signal.emit_event()

        finished.emit_event()
