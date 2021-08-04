from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.params import StringParam, IntParam, PARAM, EnumParam
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image, ImageChops
from enum import Enum, auto


class BlendOpParam(EnumParam):
    class Operations(Enum):
        multiply = auto()
        soft_light = auto()
        hard_light = auto()
        overlay = auto()

    enum = Operations


class Blend(BaseImageNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'BlendImage'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image1', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image2', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(BlendOpParam(name='blend_mode', value=BlendOpParam.Operations.overlay, pluggable=PARAM))

    def compute(self):
        self.start_spinner_signal.emit()
        image1 = self.get_first_param('image1', pluggable=INPUT_PLUG)
        image2 = self.get_first_param('image2', pluggable=INPUT_PLUG)
        image = self.get_first_param('image', pluggable=OUTPUT_PLUG)

        blend_mode = self.get_first_param('blend_mode', pluggable=PARAM)
        if blend_mode.value == BlendOpParam.Operations.multiply:
            image.value = ImageChops.multiply(image1.value, image2.value)
        elif blend_mode.value == BlendOpParam.Operations.soft_light:
            image.value = ImageChops.soft_light(image1.value, image2.value)
        elif blend_mode.value == BlendOpParam.Operations.hard_light:
            image.value = ImageChops.hard_light(image1.value, image2.value)
        elif blend_mode.value == BlendOpParam.Operations.overlay:
            image.value = ImageChops.overlay(image1.value, image2.value)

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
