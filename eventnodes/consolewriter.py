from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class ConsoleWriter(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'ConsoleWriter'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='prefix', value='%m/%d/%Y, %H:%M:%S', pluggable=PARAM))
        self.params.append(StringParam(name='message', value='', pluggable=PARAM | INPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        prefix = self.get_first_param('prefix')

        from datetime import datetime

        now = datetime.now()
        date_time = now.strftime(prefix.value)

        message = self.get_first_param('message').value

        output = '{} {}'.format(date_time, message)
        print(output)

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.stop_spinner_signal.emit()
        super().compute()
