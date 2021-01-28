from PySide2 import QtCore
from PySide2.QtCore import Slot, Signal

from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM
from abc import abstractmethod


class BaseNode(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = []
        self.ui_node = None
        self.obj_id = None

    def get_params(self):
        return self.params

    def get_param_value(self, param):
        return self.params[param]()

    def set_param_value(self, param, value):
        p = self.get_first_param(param)
        p.value = value

    def get_first_param(self, param, pluggable=None):
        for p in self.params:
            if p.name == param:
                if not pluggable:
                    return p
                else:
                    if p.pluggable & pluggable:
                        return p

    def update(self):
        self.ui_node.update()


class ComputeNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (35, 105, 140, 200)
        self.signals = []

    @Slot(str)
    def trigger(self, event):
        self.compute()

    @abstractmethod
    def compute(self):
        pass

    def get_signals(self):
        return self.signals

    def get_first_signal(self, signal, pluggable=None):
        for s in self.signals:
            if s.name == signal:
                if not pluggable:
                    return s
                else:
                    if s.pluggable & pluggable:
                        return s

    def map_signal(self, signal):
        if signal == 'event':
            return self.trigger

    def connect_from(self, signal, trigger=None):
        if not trigger:
            signal.connect(self.trigger)
        else:
            signal.connect(self.map_signal(trigger))

    def disconnect_from(self, signal, trigger=None):
        if not trigger:
            signal.disconnect(self.trigger)
        else:
            signal.disconnect(self.map_signal(trigger))


class EventNode(ComputeNode):
    def __init__(self):
        super().__init__()
        self.color = (150, 0, 0, 250)
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
