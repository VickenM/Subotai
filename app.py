import sys
import pywerlines.pywerview

from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QDockWidget, QWidget, QHBoxLayout, QGraphicsScene, \
    QSplitter
from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtCore import Slot

from toolbox import ToolBox, ToolItem
from parameters import Parameters
from pywerlines import pyweritems, pywerscene

import nodes

import eventnodes.parameter
import eventnodes.inttostr
import eventnodes.math
import eventnodes.timer
import eventnodes.zipfile
import eventnodes.copyfile
import eventnodes.listdir
import eventnodes.dirchange
import eventnodes.fileschanged
import eventnodes.email
import eventnodes.consolewriter
import eventnodes.foreach
import eventnodes.condition
import eventnodes.collector
import appnode


@Slot(list)
def selected_nodes(data):
    pass
    # print(data)


@Slot(list)
def added_nodes(data):
    pass


@Slot(list)
def deleted_nodes(data):
    pass
    # print(data)


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def connected_plugs(plug1, plug2):
    source = plug1.parentItem().node_obj
    target = plug2.parentItem().node_obj

    from eventnodes import signal
    source_signal = isinstance(plug1.plug_obj, signal.Signal)
    target_signal = isinstance(plug2.plug_obj, signal.Signal)

    # if plug1.type_ == 'event' and plug2.type_ == 'event':
    if all([source_signal, target_signal]):
        signal_obj = plug1.plug_obj
        target.connect_from(signal_obj.computed, trigger=plug2.type_)
    else:
        input = plug1.plug_obj
        output = plug2.plug_obj

        output.connect(input)


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def disconnected_plugs(plug1, plug2):
    source = plug1.parentItem().node_obj
    target = plug2.parentItem().node_obj

    from eventnodes import signal
    source_signal = isinstance(plug1.plug_obj, signal.Signal)
    target_signal = isinstance(plug2.plug_obj, signal.Signal)

    # if plug1.type_ == 'event' and plug2.type_ == 'event':
    if all([source_signal, target_signal]):
        signal_obj = plug1.plug_obj
        target.disconnect_from(signal_obj.computed, trigger=plug2.type_)
    else:
        input = plug1.plug_obj
        output = plug2.plug_obj

        output.disconnect()


class EventFlow(pywerscene.PywerScene):
    def list_node_types(self):
        return nodes.list_nodes()

    def new_node(self, type_):
        if type_ == 'Parameter':
            node = appnode.ParamNode.from_event_node(eventnodes.parameter.Parameter())
        elif type_ == 'IntToStr':
            node = appnode.ParamNode.from_event_node(eventnodes.inttostr.IntToStr())
        elif type_ == 'Math':
            node = appnode.ParamNode.from_event_node(eventnodes.math.Math())
        elif type_ == 'Timer':
            node = appnode.EventNode.from_event_node(eventnodes.timer.TimerNode())
        elif type_ == 'DirChanged':
            node = appnode.EventNode.from_event_node(eventnodes.dirchange.DirChanged())
        elif type_ == 'FilesChanged':
            node = appnode.EventNode.from_event_node(eventnodes.fileschanged.FilesChanged())
        elif type_ == 'ConsoleWriter':
            node = appnode.EventNode.from_event_node(eventnodes.consolewriter.ConsoleWriter())
        elif type_ == 'Zip':
            node = appnode.EventNode.from_event_node(eventnodes.zipfile.ZipFile())
        elif type_ == 'CopyFile':
            node = appnode.EventNode.from_event_node(eventnodes.copyfile.CopyFile())
        elif type_ == 'ListDir':
            node = appnode.EventNode.from_event_node(eventnodes.listdir.ListDir())
        elif type_ == 'Email':
            node = appnode.EventNode.from_event_node(eventnodes.email.Email())
        elif type_ == 'Collector':
            node = appnode.EventNode.from_event_node(eventnodes.collector.Collector())
        elif type_ == 'ForEach':
            node = appnode.EventNode.from_event_node(eventnodes.foreach.ForEach())
        elif type_ == 'Condition':
            node = appnode.EventNode.from_event_node(eventnodes.condition.Condition())
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

        return source_plug.plug_obj.type == target_plug.plug_obj.type

    def create_node_of_type(self, type_):
        node = self.new_node(type_)
        self.add_node(node)
        return node

    def create_edge(self, source_plug, target_plug):
        super(EventFlow, self).create_edge(source_plug, target_plug)

    def eval(self):
        selected_node = self.get_selected_nodes()[0]
        mnode = selected_node.node_obj
        mnode.compute()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        view = pywerlines.pywerview.PywerView()
        scene = EventFlow()
        scene.setSceneRect(0, 0, 5000, 5000)
        scene.setItemIndexMethod(scene.NoIndex)
        view.setScene(scene)

        toolbox = ToolBox()
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="DirChanged", sections=['Events']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="FilesChanged", sections=['Events']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Timer", sections=['Events']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="CopyFile", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="ListDir", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Zip", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Email", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Parameter", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="IntToStr", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Math", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="ForEach", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Condition", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="Collector", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon('./icons/flow.png'), label="ConsoleWriter", sections=['I/O']))
        toolbox.itemClicked.connect(self.toolbox_item_selected)

        self.parameters = Parameters()

        splitter = QSplitter(parent=self)
        splitter.addWidget(toolbox)
        splitter.addWidget(view)
        splitter.addWidget(self.parameters)
        splitter.setSizes([100, 400, 100])

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        self.setLayout(layout)

        scene.nodes_selected.connect(selected_nodes)
        scene.nodes_deleted.connect(deleted_nodes)
        scene.nodes_added.connect(added_nodes)
        scene.plugs_connected.connect(connected_plugs)
        scene.plugs_disconnected.connect(disconnected_plugs)

        scene.nodes_selected.connect(self.selected_nodes)

        self.scene = scene
        self.view = view

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_D:
            node = self.scene.create_node_of_type('DirChanged')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_Z:
            node = self.scene.create_node_of_type('Zip')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_C:
            node = self.scene.create_node_of_type('CopyFile')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_E:
            node = self.scene.create_node_of_type('Email')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_I:
            node = self.scene.create_node_of_type('ItemList')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_P:
            node = self.scene.create_node_of_type('Parameter')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_G:
            if (event.modifiers() and QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier:
                self.scene.group_selected_nodes()
            else:
                group = self.scene.create_group()
                position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
                group.setPos(position)
        elif event.key() == QtCore.Qt.Key_Period:
            self.scene.toggle_labels()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.scene.remove_selected_nodes()
            self.scene.remove_selected_groups()
        elif event.key() == QtCore.Qt.Key_Space:
            self.scene.eval()

    @Slot(str)
    def toolbox_item_selected(self, item):
        node = self.scene.create_node_of_type(item)
        position = QtCore.QPointF(self.view.mapToScene(100, 100))
        # position = QtCore.QPointF(100, 100)
        node.setPos(position)

    @Slot(list)
    def selected_nodes(self, nodes):
        if nodes:
            self.parameters.set_node_obj(nodes[0].node_obj)
        else:
            self.parameters.set_node_obj(None)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    return app, main_window


if __name__ == "__main__":
    app, main_window = main()
    sys.exit(app.exec_())
