from PySide2.QtWidgets import QGraphicsScene
from PySide2 import QtCore
from . import pyweritems


class PywerScene(QGraphicsScene):
    nodes_selected = QtCore.Signal(list)
    nodes_added = QtCore.Signal(list)
    nodes_deleted = QtCore.Signal(list)
    items_moved = QtCore.Signal(list)
    plugs_connected = QtCore.Signal(pyweritems.PywerPlug, pyweritems.PywerPlug)
    plugs_disconnected = QtCore.Signal(pyweritems.PywerPlug, pyweritems.PywerPlug)
    group_nodes = QtCore.Signal(list)
    group_added = QtCore.Signal(list)

    def __init_(self, **kwargs):
        super(PywerScene, self).__init__(**kwargs)

    def emit_selected_nodes(self, items):
        # selected_nodes = self.get_selected_nodes()
        # self.nodes_selected.emit(selected_nodes)
        self.nodes_selected.emit(items)

    def emit_deleted_nodes(self, nodes):
        self.nodes_deleted.emit(nodes)

    def emit_connected_plugs(self, plug1, plug2):
        self.plugs_connected.emit(plug1, plug2)

    def emit_disconnected_plugs(self, plug1, plug2):
        self.plugs_disconnected.emit(plug1, plug2)

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

    def remove_selected_nodes(self):
        nodes = self.get_selected_nodes()
        self.remove_nodes(nodes)

    def remove_selected_groups(self):
        for group in self.get_selected_groups():
            self.removeItem(group)

    def create_group(self):
        group = pyweritems.PywerGroup()
        self.addItem(group)
        return group

    def group_selected_nodes(self):
        nodes = self.get_selected_nodes()
        if not nodes:
            return

        top = left = float("inf")
        bottom = right = 0
        for node in nodes:
            pos = node.pos()
            if pos.y() < top:
                top = pos.y()
            if pos.y() + node.height > bottom:
                bottom = pos.y() + node.height
            if pos.x() < left:
                left = pos.x()
            if pos.x() + node.width > right:
                right = pos.x() + node.width

        group = pyweritems.PywerGroup()
        top -= group.header_height
        left -= 10
        bottom += 10
        right += 10

        position = QtCore.QPointF(left, top)
        group.width = right - left
        group.height = abs(bottom - top)
        group.adjust()
        group.setPos(position)
        self.addItem(group)
        return group

    def add_node(self, node):
        self.addItem(node)
        self.nodes_added.emit([node])
        return node

    # abstract
    def create_node_of_type(self, type_):
        pass

    def itemsMoved(self, items):
        self.items_moved.emit(items)

    def itemsSelected(self, items):
        print(items)
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
