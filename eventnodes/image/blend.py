from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, IntParam, PARAM, EnumParam
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image, ImageChops
from enum import Enum, auto


class BlendOpParam(EnumParam):
    class Operations(int, Enum):
        multiply = auto()
        soft_light = auto()
        hard_light = auto()
        overlay = auto()

    enum = Operations


class Blend(BaseImageNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:image1': ParameterDefinition(ImageParam, {'name': 'image1', 'pluggable': INPUT_PLUG}, storage='transient', bind_node=False),
        'input:image2': ParameterDefinition(ImageParam, {'name': 'image2', 'pluggable': INPUT_PLUG}, storage='transient', bind_node=False),
        'output:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': OUTPUT_PLUG}, storage='transient', bind_node=False),
        'property:blend_mode': ParameterDefinition(BlendOpParam, {'name': 'blend_mode', 'value': BlendOpParam.Operations.overlay, 'pluggable': PARAM}, storage='stored', bind_node=False),
    }

    type = 'BlendImage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(ImageParam(name='image1', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image2', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(self.create_parameter('property:blend_mode'))

    @ComputeNode.Decorators.show_ui_computation
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
