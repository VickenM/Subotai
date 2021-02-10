from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.params import StringParam, IntParam, PARAM
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Save(BaseImageNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'SaveImage'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='filename', value='', pluggable=PARAM | INPUT_PLUG))

    def compute(self):
        self.start_spinner_signal.emit()
        file_ = self.get_first_param('filename')
        image_ = self.get_first_param('image')

        img = image_()
        img.save(file_())

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
