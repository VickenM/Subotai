import pywerlines.pyweritems
import eventnodes.params
import eventnodes.signal
import register

import uuid

from PySide2 import QtCore


class Plug(pywerlines.pyweritems.PywerPlug):
    @classmethod
    def from_param(cls, param_obj):
        path = pywerlines.pyweritems.PywerPlug.ELLIPSE
        plug = cls(type=param_obj.name, color=param_obj.color, path=path, plug_obj=param_obj)
        return plug


class Signal(pywerlines.pyweritems.PywerPlug):
    @classmethod
    def from_param(cls, param_obj):
        path = pywerlines.pyweritems.PywerPlug.PENTAGON
        plug = cls(type=param_obj.name, color=param_obj.color, path=path, plug_obj=param_obj)
        return plug


class Group:
    pass


class AppGroup(pywerlines.pyweritems.PywerGroup):
    @classmethod
    def from_event_node(cls, group_obj):
        node = cls()
        node.node_obj = group_obj
        node.node_obj.set_ui_node = node
        node.node_obj.obj_id = uuid.uuid4()
        return node


class AppNode(pywerlines.pyweritems.PywerNode):
    @classmethod
    def from_event_node(cls, node_obj):
        node = cls(type=node_obj.type, color=node_obj.color)
        if hasattr(node_obj, 'get_signals'):
            for signal in node_obj.get_signals():
                if signal.get_pluggable() & eventnodes.signal.INPUT_PLUG:
                    node.add_input(Signal.from_param(param_obj=signal))
                elif signal.get_pluggable() & eventnodes.signal.OUTPUT_PLUG:
                    node.add_output(Signal.from_param(param_obj=signal))

        for param in node_obj.get_params():
            if param.get_pluggable() & eventnodes.params.INPUT_PLUG:
                node.add_input(Plug.from_param(param_obj=param))

            elif param.get_pluggable() & eventnodes.params.OUTPUT_PLUG:
                node.add_output(Plug.from_param(param_obj=param))

        node.node_obj = node_obj
        node_obj.set_ui_node(node)
        node_obj.obj_id = uuid.uuid4()

        return node

    def to_dict(self):
        dict_ = {
            'node_obj': self.node_obj.__module__ + '.' + self.node_obj.type,
            'id': str(self.node_obj.obj_id),
            'position': (self.pos().x(), self.pos().y()),
            'params': {},
            'active': self.node_obj.active,
            'size': (self.width, self.height),
            'name': self.name.toPlainText()
        }

        for param in self.node_obj.params:
            pluggable = dict_['params'].setdefault(param.pluggable, {})
            pluggable[param.name] = param.to_dict()

        return dict_


def new_group(position=None):
    group_obj = Group()
    group = AppGroup.from_event_node(group_obj=group_obj)
    if position:
        group.setPos(position)
    return group


def new_node(type_, position: QtCore.QPoint = None, size: QtCore.QSize = None):
    if type_ not in register.node_registry:
        return None
    event_node = register.node_registry[type_]()
    node = AppNode.from_event_node(event_node)
    if position:
        node.setPos(position)
    if size:
        node.setSize(size.width(), size.height())
    return node


def connect_plugs(plug1, plug2):
    source = plug1.parentItem().node_obj
    target = plug2.parentItem().node_obj

    source_signal = isinstance(plug1.plug_obj, eventnodes.signal.Signal)
    target_signal = isinstance(plug2.plug_obj, eventnodes.signal.Signal)

    if all([source_signal, target_signal]):
        signal_obj = plug1.plug_obj
        target.connect_from(signal_obj.computed, trigger=plug2.type_)
    else:
        input = plug1.plug_obj
        output = plug2.plug_obj

        output.connect_(input)


def disconnect_plugs(plug1, plug2):
    source = plug1.parentItem().node_obj
    target = plug2.parentItem().node_obj

    source_signal = isinstance(plug1.plug_obj, eventnodes.signal.Signal)
    target_signal = isinstance(plug2.plug_obj, eventnodes.signal.Signal)

    if all([source_signal, target_signal]):
        signal_obj = plug1.plug_obj
        target.disconnect_from(signal_obj.computed, trigger=plug2.type_)
    else:
        input = plug1.plug_obj
        output = plug2.plug_obj

        output.disconnect_()
