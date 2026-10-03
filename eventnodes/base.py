from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtCore import Slot, Signal, QEventLoop

from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM
from abc import abstractmethod


class BaseNode(QtCore.QObject):
    def __init_subclass__(cls, **kwargs):
        """Guard built-in state transitions so snapshots cannot observe half an edit."""
        super().__init_subclass__(**kwargs)
        import functools
        import inspect
        def guarded(function):
            if inspect.iscoroutinefunction(function):
                @functools.wraps(function)
                async def async_call(self, *args, **kw):
                    with self._state_lock:
                        self._state_busy += 1
                        try:
                            return await function(self, *args, **kw)
                        finally:
                            self._state_busy -= 1
                return async_call
            @functools.wraps(function)
            def call(self, *args, **kw):
                with self._state_lock:
                    self._state_busy += 1
                    try:
                        return function(self, *args, **kw)
                    finally:
                        self._state_busy -= 1
            return call
        for name in ('compute', 'collect', 'reset', 'received_response', 'job_complete'):
            if name in cls.__dict__:
                setattr(cls, name, guarded(cls.__dict__[name]))

    parameter_definitions = {}
    signal_definitions = {}
    state_fields = {}
    type_version = 1
    type_migrations = {}
    dynamic_input_prefix = None

    @classmethod
    def persistence_type_id(cls):
        """Return the stable built-in ID or an add-on's explicit namespaced ID."""
        if cls.__module__.startswith('eventnodes.'):
            return 'subotai:' + cls.type
        return cls.persistence_type

    def create_signal(self, binding):
        """Create an event port from its class-owned declaration."""
        from eventnodes.signal import Signal
        name, flags = self.signal_definitions[binding]
        return Signal(node=self, name=name, pluggable=flags)

    @classmethod
    def describe_parameters(cls):
        """Return inherited node-owned declarations without creating a node."""
        definitions = {}
        for parent in reversed(cls.__mro__):
            definitions.update(parent.__dict__.get('parameter_definitions', {}))
        return definitions

    def create_parameter(self, binding):
        """Use the declaration as the single source of constructor defaults."""
        return self.describe_parameters()[binding].create(self)

    def save_state(self):
        """Return declared extra state; the serializer detaches and encodes it."""
        return {key: getattr(self, field.attribute) for key, field in self.state_fields.items()}

    def restore_state(self, state):
        """Restore validated extra state onto an inactive node."""
        from copy import deepcopy
        for key, field in self.state_fields.items():
            setattr(self, field.attribute, deepcopy(state[key]))

    categories = ['General']
    description = """Base Node description"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from persistence import is_restoring
        import threading
        self._state_lock = threading.RLock()
        self._state_busy = 0
        self.restoring = is_restoring()
        self.color = (150, 150, 150, 255)
        self.warning_color = (150, 100, 25, 255)
        self.error_color = (150, 50, 50, 255)

        self.controls = []
        self.params = []
        self.ui_node = None
        self.obj_id = None

        self.active = True

        self.computable = False

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

    def activate_resources(self):
        """Start non-event runtime resources after a staged graph is committed."""
        pass

    def pause_resources(self):
        """Stop transient jobs when a pasted graph is removed by undo."""
        pass

    def sync_restored_controls(self):
        """Synchronize inert UI configuration without evaluating derived outputs."""
        pass

    def connected_params(self, connected_param, this_param):
        pass

    def disconnected_params(self, this_param):
        pass

    def set_ui_node(self, ui_node):
        self.ui_node = ui_node

    def unset_ui_node(self):
        self.ui_node = None


class ComputeNode(BaseNode):
    calculate = QtCore.Signal()
    start_spinner_signal = QtCore.Signal()
    stop_spinner_signal = QtCore.Signal()
    start_glow_signal = QtCore.Signal(tuple)
    stop_glow_signal = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (35, 105, 140, 200)
        self.signals = []
        self.calculate.connect(self.compute)
        self.computable = True

    def set_ui_node(self, ui_node):
        super().set_ui_node(ui_node)
        # self.ui_node = ui_node
        self.start_spinner_signal.connect(self.ui_node.start_spinner)
        self.stop_spinner_signal.connect(self.ui_node.stop_spinner)
        self.start_glow_signal.connect(self.ui_node.show_glow)
        self.stop_glow_signal.connect(self.ui_node.clear_glow)

    def unset_ui_node(self):
        self.start_spinner_signal.disconnect(self.ui_node.start_spinner)
        self.stop_spinner_signal.disconnect(self.ui_node.stop_spinner)
        self.start_glow_signal.disconnect(self.ui_node.show_glow)
        self.stop_glow_signal.disconnect(self.ui_node.clear_glow)
        super().unset_ui_node()
        # self.ui_node = None

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

    class Decorators(object):
        @classmethod
        def show_ui_computation(cls, func):
            import functools

            @functools.wraps(func)
            def do_show_ui_computation(self):
                self.start_spinner_signal.emit()
                self.stop_glow_signal.emit()
                try:
                    func(self)
                except Exception as e:
                    print(e)
                    self.start_glow_signal.emit(self.error_color)

                self.stop_spinner_signal.emit()

            return do_show_ui_computation


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
