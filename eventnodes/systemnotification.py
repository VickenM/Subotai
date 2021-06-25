from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets

# void QSystemTrayIcon::showMessage(const QString &title, const QString &message, QSystemTrayIcon::MessageIcon icon = QSystemTrayIcon::Information, int millisecondsTimeoutHint = 10000

class SystemNotification(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'SystemNotification'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.params.append(StringParam(name='message', value='', pluggable=PARAM | INPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        print('NOT IMPLEMENTED YET')

        # message = self.get_first_param('message').value
        # msg = QtWidgets.QWidget()
        # layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(QtWidgets.QLabel(message))
        # msg.setLayout(layout)
        # msg.show()

        self.stop_spinner_signal.emit()
        super().compute()
