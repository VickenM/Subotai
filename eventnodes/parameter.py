from persistence import ParameterDefinition
from .base import BaseNode, ComputeNode, EventNode
from .params import IntParam, FloatParam, StringParam, ListParam, BoolParam
from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM, NONE
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtCore import Slot


class PromoteWidget(QtWidgets.QWidget):
    promote_signal = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.checkbox = QtWidgets.QCheckBox()
        self.line = QtWidgets.QLineEdit()
        self.line.setPlaceholderText('promoted name')
        self.line.setEnabled(self.checkbox.isChecked())

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.line)
        layout.addWidget(self.checkbox)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)

        self.checkbox.checkStateChanged.connect(self.changed)
        self.line.textChanged.connect(self.changed)
        self.setLayout(layout)

    @Slot()
    def changed(self):
        self.line.setEnabled(self.checkbox.isChecked())
        self.promote_signal.emit()


class ParamNode(BaseNode):
    def sync_restored_controls(self):
        with QtCore.QSignalBlocker(self.promote_control.checkbox), QtCore.QSignalBlocker(self.promote_control.line):
            self.update()

    parameter_definitions = {
        'property:promote state': ParameterDefinition(BoolParam, {'name': 'promote state', 'value': False, 'pluggable': NONE}, storage='stored', bind_node=False),
        'property:promote name': ParameterDefinition(StringParam, {'name': 'promote name', 'value': None, 'pluggable': NONE}, storage='stored', bind_node=False),
    }

    description = """**Parameters Nodes** are a convenient way to provide the same value to multiple
inputs and can be controlled from a single spot.

If the paramter is promoted, it's value can be set from the commandline interface
"""
    categories = ['Data']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.promote_control = PromoteWidget()
        self.params.append(self.create_parameter('property:promote state'))
        self.params.append(self.create_parameter('property:promote name'))

        self.controls.append((self.promote_control, self.sync, self.promote_control.promote_signal))

    def sync(self):
        state = self.get_first_param('promote state')
        name = self.get_first_param('promote name')
        state.value = self.promote_control.checkbox.isChecked()
        name.value = self.promote_control.line.text()

    def update(self):
        state = self.get_first_param('promote state')
        name = self.get_first_param('promote name')
        self.promote_control.checkbox.setChecked(state.value)
        self.promote_control.line.setText(name.value)
        super().update()


class StringParameter(ParamNode):
    parameter_definitions = {
        'output:param': ParameterDefinition(StringParam, {'name': 'param', 'value': '', 'pluggable': OUTPUT_PLUG | PARAM}, storage='stored', bind_node=False),
    }

    type = 'StringParameter'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (150, 150, 150, 255)
        self.params.append(self.create_parameter('output:param'))


class IntegerParameter(ParamNode):
    parameter_definitions = {
        'output:param': ParameterDefinition(IntParam, {'name': 'param', 'value': 0, 'pluggable': OUTPUT_PLUG | PARAM}, storage='stored', bind_node=False),
    }

    type = 'IntegerParameter'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (150, 150, 150, 255)
        self.params.append(self.create_parameter('output:param'))


class FloatParameter(ParamNode):
    parameter_definitions = {
        'output:param': ParameterDefinition(FloatParam, {'name': 'param', 'value': 0.0, 'pluggable': OUTPUT_PLUG | PARAM}, storage='stored', bind_node=False),
    }

    type = 'FloatParameter'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (150, 150, 150, 255)
        self.params.append(self.create_parameter('output:param'))


class BooleanParameter(ParamNode):
    parameter_definitions = {
        'output:param': ParameterDefinition(BoolParam, {'name': 'param', 'value': True, 'pluggable': OUTPUT_PLUG | PARAM}, storage='stored', bind_node=False),
    }

    type = 'BooleanParameter'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = (150, 150, 150, 255)
        self.params.append(self.create_parameter('output:param'))
