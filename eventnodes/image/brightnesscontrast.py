from PySide2 import QtCore
from PySide2.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, FloatParam, IntParam, PARAM, EnumParam
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image, ImageChops, ImageEnhance


class BrightnessContrast(BaseImageNode):
    type = 'Brightness/Contrast'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(FloatParam(name='brightness', value=1.0, pluggable=PARAM))
        self.params.append(FloatParam(name='contrast', value=1.0, pluggable=PARAM))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        in_image = self.get_first_param('image', pluggable=INPUT_PLUG)
        brightness = self.get_first_param('brightness', pluggable=PARAM)
        contrast = self.get_first_param('contrast', pluggable=PARAM)
        out_image = self.get_first_param('image', pluggable=OUTPUT_PLUG)

        if in_image.value:
            enhancer = ImageEnhance.Brightness(in_image.value)
            im = enhancer.enhance(brightness.value)

            enhancer = ImageEnhance.Contrast(im)
            im = enhancer.enhance(contrast.value)

            out_image.value = im

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()