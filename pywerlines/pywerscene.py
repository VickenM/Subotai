from PySide2.QtWidgets import QGraphicsScene
from PySide2 import QtCore
from . import pyweritems


class PywerScene(QGraphicsScene):
    plugs_connected = QtCore.Signal(pyweritems.PywerPlug, pyweritems.PywerPlug, pyweritems.PywerEdge)
    plugs_disconnected = QtCore.Signal(pyweritems.PywerPlug, pyweritems.PywerPlug, pyweritems.PywerEdge)
    rename_item = QtCore.Signal(list)
    nodes_selected = QtCore.Signal(list)
    nodes_added = QtCore.Signal(list)
    nodes_deleted = QtCore.Signal(list)
    items_moved = QtCore.Signal(list)
    items_resized = QtCore.Signal(list)
    group_nodes = QtCore.Signal(list)
    group_added = QtCore.Signal(list)

    def __init_(self, **kwargs):
        super(PywerScene, self).__init__(**kwargs)

    def emit_selected_items(self, items):
        self.nodes_selected.emit(items)

    def emit_deleted_nodes(self, nodes):
        self.nodes_deleted.emit(nodes)

    # def emit_added_nodes(self, nodes):
    #     self.nodes_added.emit(nodes)

    def emit_connected_plugs(self, plug1, plug2, edge):
        self.plugs_connected.emit(plug1, plug2, edge)

    def emit_disconnected_plugs(self, plug1, plug2, edge):
        self.plugs_disconnected.emit(plug1, plug2, edge)

    def emit_rename_item(self, item):
        self.rename_item.emit([item])

    def addItem(self, item):
        super(PywerScene, self).addItem(item)

    def removeItem(self, item):
        super(PywerScene, self).removeItem(item)

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
        self.emit_connected_plugs(source_plug, target_plug, edge)
        return edge

    def remove_edge(self, edge):
        edge.source_plug.edges.remove(edge)
        edge.target_plug.edges.remove(edge)
        self.removeItem(edge)
        # self.emit_disconnected_plugs(edge.source_plug, edge.target_plug, edge)

    def get_selected_nodes(self):
        return [item for item in self.selectedItems() if isinstance(item, pyweritems.PywerNode)]

    def get_selected_groups(self):
        return [item for item in self.selectedItems() if isinstance(item, pyweritems.PywerGroup)]

    def get_selected_items(self):
        return self.get_selected_nodes() + self.get_selected_groups()

    def get_all_nodes(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerNode)]

    def get_all_groups(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerGroup)]

    def get_all_items(self):
        return [item for item in self.items() if
                isinstance(item, pyweritems.PywerNode) or
                isinstance(item, pyweritems.PywerGroup)]

    def remove_node(self, node):
        self._remove_node(node)
        self.emit_deleted_nodes([node])

    def remove_nodes(self, nodes):
        for node in nodes:
            self._remove_node(node)
        self.emit_deleted_nodes(nodes)

    def remove_items(self, items):
        for item in items:
            if isinstance(item, pyweritems.PywerNode):
                self._remove_node(item)
            else:
                self.removeItem(item)
        self.emit_deleted_nodes(items)

    def remove_item(self, item):
        if isinstance(item, pyweritems.PywerNode):
            self._remove_node(item)
        else:
            self.removeItem(item)
        self.emit_deleted_nodes([item])

    def remove_selected_nodes(self):
        nodes = self.get_selected_nodes()
        self._remove_nodes(nodes)
        self.emit_deleted_nodes(nodes)

    def remove_selected_groups(self):
        groups = self.get_selected_groups()
        for group in groups:
            self.removeItem(group)
        self.emit_deleted_nodes(groups)

    def remove_selected_items(self):
        items = self.get_selected_nodes() + self.get_selected_groups()
        for item in items:
            self.removeItem(item)
        self.emit_deleted_nodes(items)

    def create_group(self):

        group = pyweritems.PywerGroup()
        self.addItem(group)
        return group

    def add_group(self, group):
        self.addItem(group)
        self.nodes_added.emit([group])
        return group

    def add_node(self, node):
        self.addItem(node)
        self.nodes_added.emit([node])
        return node

    def itemsMoved(self, items):
        self.items_moved.emit(items)

    def itemsResized(self, items):
        self.items_resized.emit(items)

    def itemsSelected(self, items):
        self.nodes_selected.emit(items)

    def list_node_types(self):
        return []

    def list_nodes(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerNode)]

    def toggle_names(self):
        all_nodes = [item for item in self.items() if isinstance(item, pyweritems.PywerNode) or \
                     isinstance(item, pyweritems.PywerGroup)]
        for node in all_nodes:
            node.name.setVisible(not node.name.isVisible())

    def select_all(self):
        all_nodes = [item for item in self.items() if isinstance(item, pyweritems.PywerNode) or \
                     isinstance(item, pyweritems.PywerGroup)]
        for node in all_nodes:
            node.setSelected(True)

    def select_node(self, node):
        self.clearSelection()
        node.setSelected(True)
