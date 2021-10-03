from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import EventNode, ComputeNode
from .params import IntParam, PARAM
from .signal import Signal, OUTPUT_PLUG


class TimerNode(EventNode):
    type = 'Timer'
    categories = ['Events']
    description = \
        """The **Timer node** emits an event at periodically, specified by the *interval* parameter (in miliseconds).


Parameters:

- *interval*: The timeout interval (miliseconds)
        """

    def __init__(self):
        super(TimerNode, self).__init__()
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='interval', value=1000, pluggable=PARAM))

        interval = self.get_first_param('interval').value
        self.timer = QtCore.QTimer()
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.compute)

        self.deactivate()

    @ComputeNode.Decorators.show_ui_computation
    @Slot()
    def compute(self):
        for signal in self.signals:
            signal.emit_event()

    def set_active(self, state):
        super().set_active(state)
        if self.active:
            self.timer.start()
        else:
            self.timer.stop()

    def activate(self):
        self.timer.start()
        super().activate()

    def deactivate(self):
        self.timer.stop()
        super().deactivate()

    def toggle_active(self):
        if self.timer.isActive():
            self.deactivate()
        else:
            self.activate()

    def set_param_value(self, param, value):
        super().set_param_value(param, value)
        self.timer.setInterval(self.get_first_param('interval').value)

    def update(self):
        interval = self.get_first_param('interval')
        self.timer.setInterval(interval.value)