from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import EventNode
from .params import StringParam, PARAM
from .signal import Signal, OUTPUT_PLUG

import sys

sys.path.append('D:\\projects\\python\\node2\\pynput')

from pynput import keyboard

from PySide2.QtCore import QThread


class InputListener(QThread):
    def __init__(self, parent=None, node=None):
        super().__init__(parent)
        self.hotkey = None
        self.listener = None
        self.node = node

    def key_press(self):
        if self.node:
            self.node.compute()

    def set_hotkey(self, hk):
        self.update_hotkey(hk)

    def update_hotkey(self, hk):
        try:
            self.hotkey = keyboard.HotKey(keyboard.HotKey.parse(hk), self.key_press)
        except:
            self.hotkey = None
            if self.listener and self.listener.running:
                self.listener.stop()

    def for_canonical(self, f):
        def func(k):
            return f(self.listener.canonical(k))

        return func

    def start(self):
        return super().start()

    def stop(self):
        if self.listener and self.listener.running:
            self.listener.stop()

    def run(self):
        def for_canonical(f):
            return lambda k: f(self.listener.canonical(k))

        with keyboard.Listener(on_press=for_canonical(self.hotkey.press),
                               on_release=for_canonical(self.hotkey.release)) as self.listener:
            self.listener.join()


class ValidExpressionIndicator(QtWidgets.QWidget):
    def __init__(self):
        self.super().__init__()

        self.label = QtWidgets.QLabel()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(0)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def set_valid(self):
        self.label.setText('Valid Expression')

    def set_invalid(self):
        self.label.setText('Invalid Expression')


class HotkeyNode(EventNode):
    def __init__(self):
        super(HotkeyNode, self).__init__()

        self.type = 'Hotkey'

        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='hotkey', value='', pluggable=PARAM))
        self.controls()

        self.expression_indicator = ValidExpressionIndicator()
        self.controls.append((self.expression_indicator, self.toggle_viewer, self.show_viewer_button.clicked))

        self.t = InputListener(node=self)

        self.deactivate()

        self.description = \
            """
            ex. <ctrl>+<alt>+h
"""

    def update(self):
        hk = self.get_first_param('hotkey').value
        self.terminate()

        # If there's no exception, it means we can parse the hotkey string, so Pass it on to the Listener thread.
        # Otherwise, early exit
        # TODO: maybe there's a more elegant way of testing for this
        try:
            keyboard.HotKey(keyboard.HotKey.parse(hk), lambda x: x)
        except:
            return

        self.t = InputListener(node=self)
        self.t.set_hotkey(hk)
        if self.is_active():
            self.t.start()

    @Slot()
    def compute(self):
        signal = self.get_first_signal('event')
        signal.emit_event()

    def terminate(self):
        self.t.stop()

    def activate(self):
        super().activate()
        self.update()

    def deactivate(self):
        super().deactivate()
        self.terminate()
