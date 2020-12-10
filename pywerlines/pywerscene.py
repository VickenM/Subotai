from PySide2.QtWidgets import QGraphicsScene
from PySide2 import QtCore
from . import pyweritems


class PywerScene(QGraphicsScene):
    def __init_(self, **kwargs):
        super(PywerScene, self).__init__(**kwargs)

    def addItem(self, item):
        super(PywerScene, self).addItem(item)

    def removeItem(self, item):
        super(PywerScene, self).removeItem(item)

    def can_connect(self, source_plug, target_plug):
        if source_plug.parentItem() == target_plug.parentItem():
            return False
        return True

    def create_edge(self, source_plug, target_plug):
        if not (source_plug and target_plug):
            return False

        if not self.can_connect(source_plug=source_plug, target_plug=target_plug):
            return

        edge = pyweritems.PywerEdge()
        edge.source_plug = source_plug
        edge.target_plug = target_plug
        edge.source_plug.parentItem().outputs.append(edge)
        edge.target_plug.parentItem().inputs.append(edge)

        edge.source_plug.edges.append(edge)
        edge.target_plug.edges.append(edge)
        edge.adjust()
        self.addItem(edge)

        edge.source_plug.update()
        edge.target_plug.update()

    def remove_edge(self, edge):
        edge.source_plug.edges.remove(edge)
        edge.target_plug.edges.remove(edge)
        self.removeItem(edge)

        print('hack: hiding, dont know why')
        edge.hide()
