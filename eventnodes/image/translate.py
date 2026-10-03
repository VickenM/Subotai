from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, FloatParam, IntParam, PARAM, EnumParam
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image, ImageChops, ImageEnhance


class Translate(BaseImageNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': INPUT_PLUG}, storage='transient', bind_node=False),
        'output:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': OUTPUT_PLUG}, storage='transient', bind_node=False),
        'input:x_offset': ParameterDefinition(IntParam, {'name': 'x_offset', 'value': 0, 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:y_offset': ParameterDefinition(IntParam, {'name': 'y_offset', 'value': 0, 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'Translate'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(self.create_parameter('input:x_offset'))
        self.params.append(self.create_parameter('input:y_offset'))

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
