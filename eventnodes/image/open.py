from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Open(BaseImageNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:file': ParameterDefinition(StringParam, {'name': 'file', 'value': '', 'pluggable': PARAM | INPUT_PLUG, 'subtype': SUBTYPE_FILEPATH}, storage='stored', bind_node=False),
        'output:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': OUTPUT_PLUG}, storage='transient', bind_node=False),
        'output:width': ParameterDefinition(IntParam, {'name': 'width', 'value': 0, 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
        'output:height': ParameterDefinition(IntParam, {'name': 'height', 'value': 0, 'pluggable': OUTPUT_PLUG}, storage='stored', bind_node=False),
    }

    type = 'OpenImage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(self.create_parameter('input:file'))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(self.create_parameter('output:width'))
        self.params.append(self.create_parameter('output:height'))

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
