import pywerlines.pyweritems
import eventnodes.params
import eventnodes.signal

from PIL import Image


def plug_color(param):
    if param.type == str:
        return (255, 120, 150, 255)
    elif param.type == float:
        return (120, 255, 120, 255)
    elif param.type == int:
        return (120, 150, 255, 255)
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
        return node


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
        node_obj.ui_node = node
        return node
