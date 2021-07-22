from .base import BaseNode, ComputeNode, EventNode
from .params import IntParam, FloatParam, StringParam, ListParam, BoolParam
from .params import INPUT_PLUG, OUTPUT_PLUG, PARAM, NONE
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import Slot


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
        layout.setSizeConstraint(layout.SetNoConstraint)

        self.checkbox.stateChanged.connect(self.changed)
        self.line.textChanged.connect(self.changed)
        self.setLayout(layout)

    @Slot()
    def changed(self):
        self.line.setEnabled(self.checkbox.isChecked())
        self.promote_signal.emit()


class ParamNode(BaseNode):
    description = """**Parameters Nodes** are a convenient way to provide the same value to multiple
inputs and can be controlled from a single spot.

If the paramter is promoted, it's value can be set from the commandline interface
"""
    categories = ['Data']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.promote_control = PromoteWidget()
        self.params.append(BoolParam(name='promote state', value=False, pluggable=NONE))
        self.params.append(StringParam(name='promote name', value=None, pluggable=NONE))

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'StringParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(StringParam(name='param', value='', pluggable=OUTPUT_PLUG | PARAM))


class IntegerParameter(ParamNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'IntegerParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(IntParam(name='param', value=0, pluggable=OUTPUT_PLUG | PARAM))


class FloatParameter(ParamNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'FloatParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(FloatParam(name='param', value=0.0, pluggable=OUTPUT_PLUG | PARAM))


class BooleanParameter(ParamNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'BooleanParameter'
        self.color = (150, 150, 150, 255)
        self.params.append(BoolParam(name='param', value=True, pluggable=OUTPUT_PLUG | PARAM))
