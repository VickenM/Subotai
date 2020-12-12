from PySide2.QtWidgets import QGraphicsScene
from PySide2 import QtCore
from . import pyweritems


class PywerScene(QGraphicsScene):
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
        edge.add_plug(source_plug)
        edge.add_plug(target_plug)

        source_plug.add_edge(edge)
        target_plug.add_edge(edge)
        self.addItem(edge)
        edge.adjust()
        return edge

    def remove_edge(self, edge):
        edge.source_plug.edges.remove(edge)
        edge.target_plug.edges.remove(edge)
        self.removeItem(edge)

    def get_selected_nodes(self):
        return [item for item in self.selectedItems() if isinstance(item, pyweritems.PywerNode)]

    def remove_node(self, node):
        for plug in node.inputs + node.outputs:
            for edge in plug.edges:
                self.remove_edge(edge)

                all_items = self.items()
                if edge.source_plug in all_items:
                    edge.source_plug.update()
                if edge.target_plug in all_items:
                    edge.target_plug.update()
        self.removeItem(node)

    def remove_nodes(self, nodes):
        for node in nodes:
            self.remove_node(node)
