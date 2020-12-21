from PySide2.QtWidgets import QGraphicsScene
from PySide2 import QtCore
from . import pyweritems


class PywerScene(QGraphicsScene):
    nodes_selected = QtCore.Signal(list)
    nodes_added = QtCore.Signal(list)
    nodes_deleted = QtCore.Signal(list)
    plugs_connected = QtCore.Signal(pyweritems.PywerPlug, pyweritems.PywerPlug)
    plugs_disconnected = QtCore.Signal(pyweritems.PywerPlug, pyweritems.PywerPlug)

    def __init_(self, **kwargs):
        super(PywerScene, self).__init__(**kwargs)

    def addItem(self, item):
        super(PywerScene, self).addItem(item)

    def removeItem(self, item):
        for child_item in item.childItems():
            super().removeItem(child_item)
        super().removeItem(item)

    def can_connect(self, source_plug, target_plug):
        if not (source_plug and target_plug):
            return False

        if source_plug.parentItem() == target_plug.parentItem():
            return False
        return True

    def create_edge(self, source_plug, target_plug):
        if not self.can_connect(source_plug=source_plug, target_plug=target_plug):
            return

        edge = pyweritems.PywerEdge()
        edge.connect_plugs(source_plug, target_plug)
        edge.add_plug(source_plug)
        edge.add_plug(target_plug)

        source_plug.add_edge(edge)
        target_plug.add_edge(edge)
        self.addItem(edge)
        edge.adjust()
        self.emit_connected_plugs(source_plug, target_plug)
        return edge

    def remove_edge(self, edge):
        edge.source_plug.edges.remove(edge)
        edge.target_plug.edges.remove(edge)
        self.removeItem(edge)
        self.emit_disconnected_plugs(edge.source_plug, edge.target_plug)

    def get_selected_nodes(self):
        return [item for item in self.selectedItems() if isinstance(item, pyweritems.PywerNode)]

    def get_selected_groups(self):
        return [item for item in self.selectedItems() if isinstance(item, pyweritems.PywerGroup)]

    def _remove_node(self, node):
        for plug in node.inputs + node.outputs:
            while len(plug.edges):
                edge = plug.edges[0]
                self.remove_edge(edge)

                all_items = self.items()
                if edge.source_plug in all_items:
                    edge.source_plug.update()
                if edge.target_plug in all_items:
                    edge.target_plug.update()
        self.removeItem(node)

    def remove_node(self, node):
        self._remove_node(node)
        self.emit_deleted_nodes([node])

    def remove_nodes(self, nodes):
        for node in nodes:
            self._remove_node(node)
        self.emit_deleted_nodes(nodes)

    def remove_selected_groups(self):
        for group in self.get_selected_groups():
            self.removeItem(group)

    def remove_selected_nodes(self):
        nodes = self.get_selected_nodes()
        self.remove_nodes(nodes)

    def add_node(self, node):
        self.addItem(node)
        self.nodes_added.emit([node])
        return node

    def list_node_types(self):
        return []

    def toggle_labels(self):
        all_nodes = [item for item in self.items() if isinstance(item, pyweritems.PywerNode) or \
                     isinstance(item, pyweritems.PywerGroup)]
        for node in all_nodes:
            # print(node.label.isVisible())
            # node.label.setVisible(False)
            node.label.setVisible(not node.label.isVisible())

    def emit_selected_nodes(self):
        selected_nodes = self.get_selected_nodes()
        if selected_nodes:
            self.nodes_selected.emit(selected_nodes)

    def emit_deleted_nodes(self, nodes):
        self.nodes_deleted.emit(nodes)

    def emit_connected_plugs(self, plug1, plug2):
        self.plugs_connected.emit(plug1, plug2)

    def emit_disconnected_plugs(self, plug1, plug2):
        self.plugs_disconnected.emit(plug1, plug2)
