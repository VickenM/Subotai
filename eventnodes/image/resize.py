from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, IntParam, PARAM
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Resize(BaseImageNode):
    type = 'ResizeImage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='width', value=0, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='height', value=0, pluggable=PARAM | INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | OUTPUT_PLUG))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        width = self.get_first_param('width', pluggable=INPUT_PLUG)
        height = self.get_first_param('height', pluggable=INPUT_PLUG)

        image_ = self.get_first_param('image', pluggable=INPUT_PLUG)
        out_image_ = self.get_first_param('image', pluggable=OUTPUT_PLUG)

        img = image_()
        img = img.resize((int(width()), int(height())))
        out_image_.value = img

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
