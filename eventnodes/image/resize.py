from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.params import StringParam, IntParam, PARAM
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Resize(BaseImageNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'ResizeImage'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='width', value=0, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='height', value=0, pluggable=PARAM | INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | OUTPUT_PLUG))

    def compute(self):
        width = self.get_first_param('width', pluggable=INPUT_PLUG)
        height = self.get_first_param('height', pluggable=INPUT_PLUG)


        image_ = self.get_first_param('image', pluggable=INPUT_PLUG)
        out_image_ = self.get_first_param('image', pluggable=OUTPUT_PLUG)

        img = image_()
        img = img.resize((int(width()), int(height())))
        out_image_.value = img

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        signal.emit_event()
        super().compute()
