from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Slot, Signal, QEventLoop

from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM
from abc import abstractmethod


class BaseNode(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controls = []
        self.params = []
        self.ui_node = None
        self.obj_id = None

        self.active = True

        self.computable = False

        self.description = ''

    def is_computable(self):
        return self.computable

    def activate(self):
        self.active = True
        if self.ui_node:
            self.ui_node.update()  # need to call update() on ui node to cause repaint

    def deactivate(self):
        self.active = False
        if self.ui_node:
            self.ui_node.update()  # need to call update() on ui node to cause repaint

    def set_active(self, state):
        self.active = state

    def is_active(self):
        return self.active

    def get_controls(self):
        return self.controls

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

    def terminate(self):
        pass

    def connected_params(self, connected_param, this_param):
        pass

    def disconnected_params(self, this_param):
        pass


class Worker(QtCore.QThread):
    def __init__(self, parent):
        super().__init__(parent=parent)


class ComputeNode(BaseNode):
    calculate = QtCore.Signal()
    start_spinner_signal = QtCore.Signal()
    stop_spinner_signal = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (35, 105, 140, 200)
        self.signals = []
        self.calculate.connect(self.compute)
        self.computable = True

    def set_ui_node(self, ui_node):
        self.ui_node = ui_node
        self.start_spinner_signal.connect(self.ui_node.start_spinner)
        self.stop_spinner_signal.connect(self.ui_node.stop_spinner)

    def unset_ui_node(self):
        self.start_spinner_signal.disconnect(self.ui_node.start_spinner)
        self.stop_spinner_signal.disconnect(self.ui_node.stop_spinner)
        self.ui_node = None

    @Slot()
    def trigger(self):
        self.compute()

    @Slot()
    def compute(self):
        pass

    ##################################
    # TODO: I dont know why. I have to define the specific slots for subclasses! otherwise they wont get triggered when loading from cmdline for background mode
    # this is VERY inconvenient!!

    @Slot()
    def reset(self):
        pass

    @Slot()
    def collect(self):
        pass

    ##################################

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
            signal.connect(self.trigger)  # , type=QtCore.Qt.QueuedConnection)
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

        self.activate_button = QtWidgets.QPushButton()
        self.activate_button.setCheckable(True)
        self.controls.append((self.activate_button, self.toggle_active, self.activate_button.clicked))

        if self.is_active():
            self.activate_button.setText('Deactivate')
        else:
            self.activate_button.setText('Activate')

    def set_active(self, state):
        if state:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        super().activate()
        self.activate_button.setText('Deactivate')
        if self.ui_node:
            self.ui_node.update()

    def deactivate(self):
        super().deactivate()
        self.activate_button.setText('Activate')
        if self.ui_node:
            self.ui_node.update()

    @Slot()
    def toggle_active(self):
        if self.active:
            self.deactivate()
        else:
            self.activate()
            # self.set_active(not self.active)
