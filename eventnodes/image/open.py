from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Open(BaseImageNode):
    type = 'OpenImage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='file', value='', pluggable=PARAM | INPUT_PLUG, subtype=SUBTYPE_FILEPATH))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='width', value=0, pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='height', value=0, pluggable=OUTPUT_PLUG))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        file_ = self.get_first_param('file')
        image_ = self.get_first_param('image')

        width = self.get_first_param('width')
        height = self.get_first_param('height')

        image = Image.open(file_())
        image_.value = image
        width.value = image.width
        height.value = image.height

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        self.stop_spinner_signal.emit()
        super().compute()
