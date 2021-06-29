from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore



class SystemNotification(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'SystemNotification'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.params.append(StringParam(name='title', value='', pluggable=PARAM))
        self.params.append(StringParam(name='message', value='', pluggable=PARAM | INPUT_PLUG))

    def compute(self):
        title = self.get_first_param('title').value
        message = self.get_first_param('message').value
        self.start_spinner_signal.emit()

        qApp = QtWidgets.QApplication.instance()
        icon = qApp.windowIcon()

        # TODO: hacky stuff just so that Qt doesnt give warning about non 32x32 icon sizes
        pixmap = icon.pixmap(QtCore.QSize(32, 32)).scaled(32, 32)

        # main_window = qApp.activeWindow()
        qApp.trayIcon.showMessage(
            title,
            message,
            QtGui.QIcon(pixmap),
            5 * 1000,
        )

        self.stop_spinner_signal.emit()
        super().compute()
