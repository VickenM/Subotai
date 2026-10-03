from persistence import ParameterDefinition
from PySide6 import QtCore
from PySide6.QtCore import Slot

from .baseimage import BaseImageNode
from eventnodes.base import ComputeNode
from eventnodes.params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH
from eventnodes.signal import Signal, INPUT_PLUG, OUTPUT_PLUG
from .imageparam import ImageParam

from PIL import Image


class Save(BaseImageNode):
    signal_definitions = {
        'input:event': ('event', INPUT_PLUG),
        'output:event': ('event', OUTPUT_PLUG),
    }

    parameter_definitions = {
        'input:image': ParameterDefinition(ImageParam, {'name': 'image', 'pluggable': PARAM | INPUT_PLUG}, storage='transient', bind_node=False),
        'input:filename': ParameterDefinition(StringParam, {'name': 'filename', 'value': '', 'pluggable': PARAM | INPUT_PLUG, 'subtype': SUBTYPE_FILEPATH}, storage='stored', bind_node=False),
    }

    type = 'SaveImage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals.append(self.create_signal('input:event'))
        self.signals.append(self.create_signal('output:event'))
        self.params.append(ImageParam(name='image', value=None, pluggable=PARAM | INPUT_PLUG))
        self.params.append(
            self.create_parameter('input:filename'))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        file_ = self.get_first_param('filename')
        image_ = self.get_first_param('image')

        img = image_()
        img.save(file_())

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
