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

import time


class InputListener(QThread):
    def __init__(self, parent=None, node=None):
        super().__init__(parent)
        self.hotkey = None
        self.listener = None
        self.node = node

        self.hotkey = None

        self.stopRunning = True

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
        self.stopRunning = False
        return super().start()

    def stop(self):
        self.stopRunning = True

    def run(self):
        def for_canonical(f):
            return lambda k: f(self.listener.canonical(k))

        while not self.stopRunning:
            if self.hotkey:
                with keyboard.Listener(on_press=for_canonical(self.hotkey.press),
                                       on_release=for_canonical(self.hotkey.release)) as self.listener:
                    self.listener.join()
            time.sleep(1)


class HotkeyNode(EventNode):
    def __init__(self):
        super(HotkeyNode, self).__init__()

        self.type = 'Hotkey'

        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='hotkey', value='', pluggable=PARAM))
        self.t = InputListener(node=self)
        self.t.start()

        self.description = \
            """
            ex. <ctrl>+<alt>+h
"""

    def update(self):
        self.t.set_hotkey(self.get_first_param('hotkey').value)

    def terminate(self):
        self.t.stop()

    @Slot()
    def compute(self):
        signal = self.get_first_signal('event')
        signal.emit_event()
