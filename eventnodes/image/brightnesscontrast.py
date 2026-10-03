from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, FloatParam, IntParam, PARAM, EnumParam
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image, ImageChops, ImageEnhance


class BrightnessContrast(BaseImageNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': INPUT_PLUG}, storage='transient', bind_node=False),
        'output:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': OUTPUT_PLUG}, storage='transient', bind_node=False),
        'property:brightness': ParameterDefinition(FloatParam, {'name': 'brightness', 'value': 1.0, 'pluggable': PARAM}, storage='stored', bind_node=False),
        'property:contrast': ParameterDefinition(FloatParam, {'name': 'contrast', 'value': 1.0, 'pluggable': PARAM}, storage='stored', bind_node=False),
    }

    type = 'Brightness/Contrast'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(self.create_parameter('property:brightness'))
        self.params.append(self.create_parameter('property:contrast'))

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