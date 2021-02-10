import pywerlines.pyweritems
import eventnodes.params
import eventnodes.signal

from PIL import Image

import uuid


def plug_color(param):
    if param.type == str:
        return (255, 120, 150, 255)
    elif param.type == float:
        return (200, 120, 255, 255)
    elif param.type == int:
        return (80, 80, 255, 255)
    elif param.type == list:
        return (255, 255, 120, 255)
    elif param.type == Image:
        return (120, 255, 120, 255)
    else:
        return (200, 200, 200, 255)


class ParamNode(pywerlines.pyweritems.PywerNode):
    @classmethod
    def from_event_node(cls, node_obj):
        node = cls(type=node_obj.type, color=node_obj.color)

        for param in node_obj.get_params():
            if param.get_pluggable() & eventnodes.params.INPUT_PLUG:
                i = {'type': param.name, 'path': pywerlines.pyweritems.PywerPlug.ELLIPSE, 'color': plug_color(param),
                     'plug_obj': param}
                node.add_input(pywerlines.pyweritems.PywerPlug(**i))
            elif param.get_pluggable() & eventnodes.params.OUTPUT_PLUG:
                i = {'type': param.name, 'path': pywerlines.pyweritems.PywerPlug.ELLIPSE, 'color': plug_color(param),
                     'plug_obj': param}
                node.add_output(pywerlines.pyweritems.PywerPlug(**i))

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

        for signal in node_obj.get_signals():
            if signal.get_pluggable() & eventnodes.signal.INPUT_PLUG:
                i = {'type': signal.name, 'path': pywerlines.pyweritems.PywerPlug.PENTAGON,
                     'color': (255, 255, 255, 255), 'plug_obj': signal}
                node.add_input(pywerlines.pyweritems.PywerPlug(**i))
            elif signal.get_pluggable() & eventnodes.signal.OUTPUT_PLUG:
                i = {'type': signal.name, 'path': pywerlines.pyweritems.PywerPlug.PENTAGON,
                     'color': (255, 255, 255, 255), 'plug_obj': signal}
                node.add_output(pywerlines.pyweritems.PywerPlug(**i))

        for param in node_obj.get_params():
            if param.get_pluggable() & eventnodes.params.INPUT_PLUG:
                i = {'type': param.name, 'path': pywerlines.pyweritems.PywerPlug.ELLIPSE, 'color': plug_color(param),
                     'plug_obj': param}
                node.add_input(pywerlines.pyweritems.PywerPlug(**i))
            elif param.get_pluggable() & eventnodes.params.OUTPUT_PLUG:
                i = {'type': param.name, 'path': pywerlines.pyweritems.PywerPlug.ELLIPSE, 'color': plug_color(param),
                     'plug_obj': param}
                node.add_output(pywerlines.pyweritems.PywerPlug(**i))

        node.node_obj = node_obj
        node_obj.set_ui_node(node)
        node_obj.obj_id = uuid.uuid4()

        return node

    def to_dict(self):
        dict_ = {
            'node_obj': self.node_obj.__module__ + '.' + self.node_obj.type,
            'id': str(self.node_obj.obj_id),
            'position': (self.pos().x(), self.pos().y()),
            'params': {}
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
