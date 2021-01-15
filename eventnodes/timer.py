from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import EventNode
from .params import IntParam, PARAM
from .signal import Signal, OUTPUT_PLUG


class TimerNode(EventNode):
    def __init__(self):
        super(TimerNode, self).__init__()
        self.type = 'Timer'

        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='interval', value=1000, pluggable=PARAM))

        interval = self.get_first_param('interval').value
        self.timer = QtCore.QTimer()
        self.timer.setInterval(interval)
        self.timer.start()
        self.timer.timeout.connect(self.timeout)

    def compute(self):
        for signal in self.signals:
            signal.emit_event()

    def activate(self):
        self.timer.start()
        super().activate()

    def deactivate(self):
        self.timer.stop()
        super().activate()

    @Slot()
    def timeout(self):
        self.compute()

    def set_param_value(self, param, value):
        super().set_param_value(param, value)
        self.timer.setInterval(self.get_first_param('interval').value)

    def update(self):
        interval = self.get_first_param('interval')
        self.timer.setInterval(interval.value)