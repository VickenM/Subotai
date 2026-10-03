from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, IntParam, PARAM
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Crop(BaseImageNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': PARAM | INPUT_PLUG}, storage='transient', bind_node=False),
        'input:left': ParameterDefinition(IntParam, {'name': 'left', 'value': 0, 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:upper': ParameterDefinition(IntParam, {'name': 'upper', 'value': 0, 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:right': ParameterDefinition(IntParam, {'name': 'right', 'value': 0, 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'input:lower': ParameterDefinition(IntParam, {'name': 'lower', 'value': 0, 'pluggable': PARAM | INPUT_PLUG}, storage='stored', bind_node=False),
        'output:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': PARAM | OUTPUT_PLUG}, storage='transient', bind_node=False),
    }

    type = 'CropImage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | INPUT_PLUG))
        self.params.append(self.create_parameter('input:left'))
        self.params.append(self.create_parameter('input:upper'))
        self.params.append(self.create_parameter('input:right'))
        self.params.append(self.create_parameter('input:lower'))
        self.params.append(ImageParam(name='image', value='', pluggable=PARAM | OUTPUT_PLUG))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        left = self.get_first_param('left', pluggable=INPUT_PLUG)
        right = self.get_first_param('right', pluggable=INPUT_PLUG)
        lower = self.get_first_param('lower', pluggable=INPUT_PLUG)
        upper = self.get_first_param('upper', pluggable=INPUT_PLUG)

        image_ = self.get_first_param('image', pluggable=INPUT_PLUG)
        out_image_ = self.get_first_param('image', pluggable=OUTPUT_PLUG)

        img = image_()
        img = img.crop((left(), upper(), right(), lower()))
        out_image_.value = img

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
