import pywerlines.pyweritems
import eventnodes.params
import eventnodes.signal

import uuid


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


class ParamNode(pywerlines.pyweritems.PywerNode):
    @classmethod
    def from_event_node(cls, node_obj):
        node = cls(type=node_obj.type, color=node_obj.color)
        for param in node_obj.get_params():
            if param.get_pluggable() & eventnodes.params.INPUT_PLUG:
                node.add_input(Plug.from_param(param_obj=param))
            elif param.get_pluggable() & eventnodes.params.OUTPUT_PLUG:
                node.add_output(Plug.from_param(param_obj=param))

        node.node_obj = node_obj
        node_obj.ui_node = node
        node_obj.obj_id = uuid.uuid4()
        return node

    def to_dict(self):
        dict_ = {
            'node_obj': self.node_obj.__module__ + '.' + self.node_obj.__class__.__name__,
            'id': str(self.node_obj.obj_id),
            'position': (self.pos().x(), self.pos().y()),
            'params': {}
        }
        for param in self.node_obj.params:
            from enum import Enum
            if param._type not in [list, int, bool, float, str, type(None), Enum]:
                continue

            if issubclass(param.value.__class__, Enum):
                value = param._value.value
            elif param._type == list:
                value = [v._value for v in param._value]
            else:
                value = param._value

            pluggable = dict_['params'].setdefault(param.pluggable, {})
            pluggable[param.name] = value

        return dict_


class EventNode(pywerlines.pyweritems.PywerNode):
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
            'size': (self.width, self.height)
        }

        for param in self.node_obj.params:
            from enum import Enum
            if param._type not in [list, int, bool, float, str, type(None)]:
                continue

            if param._type == list:
                value = [v._value for v in param._value]
            else:
                value = param._value

            pluggable = dict_['params'].setdefault(param.pluggable, {})
            pluggable[param.name] = value

        return dict_
