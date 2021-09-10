import appnode
import register

from pywerlines import (pywerscene, pyweritems)


class AppScene(pywerscene.PywerScene):
    def new_node(self, type_):
        if type_ not in register.node_registry:
            return None
        event_node = register.node_registry[type_]
        node = appnode.EventNode.from_event_node(event_node())
        return node

    def can_connect(self, source_plug, target_plug):
        if not super().can_connect(source_plug, target_plug):
            return False

        import eventnodes.signal
        source_signal = isinstance(source_plug.plug_obj, eventnodes.signal.Signal)
        target_signal = isinstance(target_plug.plug_obj, eventnodes.signal.Signal)
        if source_signal and target_signal:
            return True

        # if any is a signal but all are not, then only one of them is
        if any([source_signal, target_signal]) and not all([source_signal, target_signal]):
            return False

        # only one connection allowed to param plugs
        import eventnodes.params
        if (source_plug.plug_obj.get_pluggable() & eventnodes.params.INPUT_PLUG):
            input_plug = source_plug
        else:
            input_plug = target_plug

        if len(input_plug.edges):
            drag_edge = [e for e in input_plug.edges if not all([e.source_plug, e.target_plug])]
            if not drag_edge:
                return False

        return source_plug.plug_obj.type == target_plug.plug_obj.type

    def create_node_of_type(self, type_):
        node = self.new_node(type_)
        if node:
            self.add_node(node)
        return node

    def create_edge(self, source_plug, target_plug):
        super().create_edge(source_plug, target_plug)

    def get_node_by_id(self, obj_id):
        nodes = self.get_all_nodes()
        for node in nodes:
            if node.node_obj.obj_id == obj_id:
                return node

    def get_all_edges(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerEdge)]

    def get_all_nodes(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerNode)]

    def get_all_groups(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerGroup)]

    def remove_selected_nodes(self):
        nodes = self.get_selected_nodes()
        for node in nodes:
            node.node_obj.terminate()
        return super().remove_selected_nodes()

    def clear(self):
        for node in self.get_all_nodes():
            node.node_obj.terminate()
        return super().clear()

    def eval(self):
        selected_nodes = self.get_selected_nodes()
        if not selected_nodes:
            print('No nodes selected')
            return

        selected_node = selected_nodes[0]

        mnode = selected_node.node_obj
        if mnode.computable:
            mnode.calculate.emit()
