from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, FloatParam, IntParam, PARAM, EnumParam
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image, ImageChops, ImageEnhance


class Translate(BaseImageNode):
    type = 'Translate'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='x_offset', value=0, pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='y_offset', value=0, pluggable=PARAM | INPUT_PLUG))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        in_image = self.get_first_param('image', pluggable=INPUT_PLUG)
        out_image = self.get_first_param('image', pluggable=OUTPUT_PLUG)
        x_offset = self.get_first_param('x_offset', pluggable=PARAM)
        y_offset = self.get_first_param('y_offset', pluggable=PARAM)

        if in_image.value:
            a = 1
            b = 0
            c = x_offset.value  # left/right (i.e. 5/-5)
            d = 0
            e = 1
            f = y_offset.value  # up/down (i.e. 5/-5)

            img = in_image.value
            out_image.value = img.transform(img.size, Image.AFFINE, (a, b, c, d, e, f))

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
