from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtGui
from PySide2.QtCore import Slot

from functools import partial


class DescriptionWidget(QtWidgets.QWidget):
    def __init__(self, text):
        super().__init__()
        self.text = text

        # textarea = QtWidgets.QTextEdit()
        textarea = QtWidgets.QTextBrowser()
        textarea.setOpenExternalLinks(True)
        textarea.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        textarea.setMarkdown(self.text)
        textarea.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(textarea)
        self.setLayout(layout)


class ListWidget(QtWidgets.QWidget):
    def __init__(self, node_obj, param):
        super().__init__()
        self.node_obj = node_obj
        self.param = param

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.widget = QtWidgets.QListWidget()
        self.widget.itemChanged.connect(self.item_changed)
        self.widget.setFixedHeight(100)
        for item in param.value:
            i = QtWidgets.QListWidgetItem(item.value)
            i.setFlags(i.flags() | QtCore.Qt.ItemIsEditable)
            self.widget.addItem(i)

        ctrl_layout = QtWidgets.QVBoxLayout()
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_layout.setSpacing(0)

        button_add = QtWidgets.QPushButton('+')
        button_add.pressed.connect(self.add_item)
        button_add.setFixedWidth(20)

        button_del = QtWidgets.QPushButton('-')
        button_del.pressed.connect(self.del_item)
        button_del.setFixedWidth(20)

        ctrl_layout.addWidget(button_add)
        ctrl_layout.addWidget(button_del)
        ctrl_layout.addStretch()

        self.layout.addWidget(self.widget)
        self.layout.addLayout(ctrl_layout)

    def add_item(self):
        i = QtWidgets.QListWidgetItem('')
        i.setFlags(i.flags() | QtCore.Qt.ItemIsEditable)
        self.widget.addItem(i)
        self.update_param()

    def del_item(self):
        for item in self.widget.selectedItems():
            index = self.widget.row(item)
            self.widget.takeItem(index)
        self.update_param()

    def item_changed(self, changed_item):
        self.update_param()

    def update_param(self):
        items = []
        for i in range(self.widget.count()):
            items.append(self.widget.item(i).text())

        from eventnodes.params import StringParam
        self.param.value = [StringParam(name='', value=i) for i in items]
        self.node_obj.update()


class Parameters(QtWidgets.QWidget):
    # todo: self.controls_info is a cache for the control parameters from the node.
    # I need this cache so that I can connect/disconnect the signal and slots.

    def __init__(self, parent=None):
        super(Parameters, self).__init__(parent=parent)
        self.node_obj = None

        self.flayout = QtWidgets.QFormLayout()
        self.description_layout = QtWidgets.QVBoxLayout()

        mlayout = QtWidgets.QVBoxLayout()
        mlayout.addLayout(self.flayout)
        mlayout.addLayout(self.description_layout)
        mlayout.addStretch(1)

        self.central = QtWidgets.QWidget()
        self.central.setLayout(mlayout)
        self.scrollarea = QtWidgets.QScrollArea(self)
        self.scrollarea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.scrollarea.setWidget(self.central)
        self.scrollarea.setWidgetResizable(True)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.scrollarea)
        self.setLayout(self.layout)

        self.controls_info = {}

    def set_node_obj(self, node_obj):
        from eventnodes.params import INPUT_PLUG, OUTPUT_PLUG, PARAM, SUBTYPE_PASSWORD, SUBTYPE_FILEPATH, \
            SUBTYPE_DIRPATH
        from enum import Enum

        self.node_obj = node_obj

        item = self.description_layout.takeAt(0)
        if item:
            widget = item.layout() or item.widget()
            widget.setParent(None)

        while self.flayout.rowCount():
            # I want to keep controls from the previous node around without destroying them
            # Have to do extra work of removing items because removeRow(...) destroys the widget
            # and PySide2 doesnt have takeAt(...) implemented for QForLayout
            label_item = self.flayout.itemAt(0, self.flayout.LabelRole)
            field_item = self.flayout.itemAt(0, self.flayout.FieldRole)
            if not label_item:
                field = field_item.layout() or field_item.widget()
                if not isinstance(field, DescriptionWidget):
                    self.flayout.removeItem(field_item)
                    field.setParent(None)

                    if self.controls_info.get(field):
                        signal, call = self.controls_info.pop(field)
                        signal.disconnect(call)

            self.flayout.removeRow(0)

        if node_obj:

            header = QtWidgets.QLabel(self.node_obj.type)
            self.flayout.addRow('', header)

            for control_ in self.node_obj.get_controls():
                control, func, signal = control_
                call_fn = lambda x: func()
                signal.connect(call_fn)

                self.flayout.addWidget(control)
                self.controls_info[control] = (signal, call_fn)

            for param in self.node_obj.get_params():
                if not param.get_pluggable() & PARAM:
                    continue

                if param.type == str:
                    widget = QtWidgets.QLineEdit(param.value)
                    widget.textChanged.connect(partial(self.set_param_value, node_obj, param))
                    if param.subtype == SUBTYPE_PASSWORD:
                        widget.setEchoMode(widget.Password)
                    elif (param.subtype == SUBTYPE_FILEPATH) or (param.subtype == SUBTYPE_DIRPATH):
                        if param.subtype == SUBTYPE_FILEPATH:
                            button = QtWidgets.QToolButton(self)
                            button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                            button.clicked.connect(partial(
                                lambda text: text.setText(QtWidgets.QFileDialog.getOpenFileName(self, "Open File")[0]),
                                widget)
                            )
                        else:
                            button = QtWidgets.QToolButton(self)
                            button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
                            button.clicked.connect(partial(
                                lambda text: text.setText(
                                    QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory") or text.text()),
                                widget)
                            )
                        w = QtWidgets.QWidget()
                        layout = QtWidgets.QHBoxLayout()
                        layout.setContentsMargins(0, 0, 0, 0)
                        layout.setSpacing(0)
                        layout.addWidget(widget)
                        layout.addWidget(button)
                        w.setLayout(layout)
                        widget = w

                elif param.type == int:
                    widget = QtWidgets.QSpinBox()
                    widget.setMinimum(-10000)
                    widget.setMaximum(10000)
                    widget.setValue(param.value)
                    widget.valueChanged.connect(partial(self.set_param_value, node_obj, param))
                elif param.type == float:
                    widget = QtWidgets.QDoubleSpinBox()
                    widget.setMinimum(-10000)
                    widget.setMaximum(10000)
                    widget.setValue(param.value)
                    widget.valueChanged.connect(partial(self.set_param_value, node_obj, param))
                elif param.type == list:
                    widget = ListWidget(node_obj=node_obj, param=param)
                elif param.type == Enum:
                    widget = QtWidgets.QComboBox()
                    widget.addItems(list(param.Operations.__members__))
                    widget.setCurrentText(param.value.name)
                    widget.currentTextChanged.connect(partial(self.set_enum_param_value, node_obj, param))
                elif param.type == bool:
                    widget = QtWidgets.QCheckBox()
                    widget.setChecked(param.value)
                    widget.stateChanged.connect(partial(self.set_bool_param_value, node_obj, param))
                else:
                    print('parameters.py: unknown param.type', param.type)
                    continue
                    # widget = QtWidgets.QLineEdit(str(param.value))
                self.flayout.addRow(param.name, widget)

            # self.flayout.addWidget(DescriptionWidget(self.node_obj.description))
            self.description_layout.addWidget(DescriptionWidget(self.node_obj.description))

    def set_enum_param_value(self, node_obj, param, value):
        param.value = param.Operations.__members__[value]
        node_obj.update()

    def set_param_value(self, node_obj, param, value):
        param.value = value
        node_obj.update()

    def set_bool_param_value(self, node_obj, param, value):
        if value == QtCore.Qt.Checked:
            param.value = True
        elif value == QtCore.Qt.Unchecked:
            param.value = False
        node_obj.update()
