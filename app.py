import sys
import pywerlines.pywerview

from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QGraphicsScene
from PySide2 import QtCore
from PySide2.QtCore import Slot

from pywerlines import pyweritems, pywerscene

import nodes


@Slot(list)
def selected_nodes(data):
    print(data)


@Slot(list)
def added_nodes(data):
    pass


@Slot(list)
def deleted_nodes(data):
    print(data)


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def connected_plugs(plug1, plug2):
    print('connecting {}.{} {}.{}'.format(plug1.parentItem().type_, plug1.type_, plug2.parentItem().type_, plug2.type_))

    source = plug1.parentItem().node_obj
    target = plug2.parentItem().node_obj

    if plug1.type_ == 'event' and plug2.type_ == 'event':
        target.connect_from(source.computed)
    else:
        output = plug1.type_
        input_ = plug2.type_

        # TODO: this condition is hack. just doing for proof of concept.
        #       To allow for the ItemList items input plug that allows multiple input connections
        if type(target.inputs[input_]) == list:
            print('appending')
            target.inputs[input_].append(source.get_output(output))
            print(len(target.inputs[input_]))

        else:
            target.inputs[input_] = source.get_output(output)


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def disconnected_plugs(plug1, plug2):
    print('disconnected')


class EventFlow(pywerscene.PywerScene):
    def list_node_types(self):
        return nodes.list_nodes()

    def new_node(self, type_):
        if type_ == 'DirChanged':
            mnode = nodes.DirChanged()
            mnode.set_param('directory', 'D:\\projects\\python\\node2\\tmp\\src')
            blueprint = {
                'attribs': {
                    'type': 'DirChanged', 'color': (150, 0, 0, 255)
                },
                'inputs': [],
                'outputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)}
                ]
            }

            for output in mnode.get_output_names():
                blueprint['outputs'].append(
                    {'type': output, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            for input in mnode.get_input_names():
                blueprint['inputs'].append(
                    {'type': input, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
            node.node_obj = mnode
        elif type_ == 'Zip':
            mnode = nodes.Zip()
            mnode.set_param('zipfile', 'D:\\projects\\python\\node2\\tmp\\output.zip')
            blueprint = {
                'attribs': {
                    'type': 'Zip', 'color': (35, 105, 140, 200)
                },
                'inputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                ],
                'outputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)}
                ]
            }

            for output in mnode.get_output_names():
                blueprint['outputs'].append(
                    {'type': output, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            for input in mnode.get_input_names():
                blueprint['inputs'].append(
                    {'type': input, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
            node.node_obj = mnode
        elif type_ == 'CopyFile':
            mnode = nodes.CopyFile()
            mnode.set_param('destfile', 'D:\\projects\\python\\node2\\tmp\\output2.zip')
            blueprint = {
                'attribs': {
                    'type': 'CopyFile', 'color': (35, 105, 140, 200)
                },
                'inputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                ],
                'outputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)}
                ]
            }

            for output in mnode.get_output_names():
                blueprint['outputs'].append(
                    {'type': output, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            for input in mnode.get_input_names():
                blueprint['inputs'].append(
                    {'type': input, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
            node.node_obj = mnode
        elif type_ == 'Email':
            mnode = nodes.Email()
            mnode.set_param('sender', 'vicken.mavlian@gmail.com')
            mnode.set_param('recipients', ['vicken.mavlian@gmail.com'])
            mnode.set_param('subject', "wicked zip file")
            mnode.set_param('message', "whats up man, take this file")
            mnode.set_param('server', "smtp.gmail.com")
            mnode.set_param('port', 587)
            mnode.set_param('username', 'vicken.mavlian@gmail.com')
            mnode.set_param('password', '22 acacia avenue')
            mnode.set_param('use_tls', True)
            blueprint = {
                'attribs': {
                    'type': 'Email', 'color': (35, 105, 140, 200)
                },
                'inputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                ],
                'outputs': [
                    {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)}
                ]
            }

            for output in mnode.get_output_names():
                blueprint['outputs'].append(
                    {'type': output, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            for input in mnode.get_input_names():
                blueprint['inputs'].append(
                    {'type': input, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
            node.node_obj = mnode
        elif type_ == 'ItemList':
            mnode = nodes.ItemList()
            blueprint = {
                'attribs': {
                    'type': 'ItemList', 'color': (55, 150, 55, 255)
                },
                'inputs': [
                    # {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                ],
                'outputs': [
                    # {'type': 'event', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)}
                ]
            }

            for output in mnode.get_output_names():
                blueprint['outputs'].append(
                    {'type': output, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            for input in mnode.get_input_names():
                blueprint['inputs'].append(
                    {'type': input, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
            node.node_obj = mnode
        elif type_ == 'Parameter':
            mnode = nodes.Parameter()
            blueprint = {
                'attribs': {
                    'type': 'Parameter', 'color': (150, 150, 150, 255)
                },
                'inputs': [
                ],
                'outputs': [
                ]
            }

            for output in mnode.get_output_names():
                blueprint['outputs'].append(
                    {'type': output, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            for input in mnode.get_input_names():
                blueprint['inputs'].append(
                    {'type': input, 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)})

            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
            node.node_obj = mnode

        return node

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

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        self.setLayout(layout)

        scene.nodes_selected.connect(selected_nodes)
        scene.nodes_deleted.connect(deleted_nodes)
        scene.nodes_added.connect(added_nodes)
        scene.plugs_connected.connect(connected_plugs)
        scene.plugs_disconnected.connect(disconnected_plugs)

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


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    return app, main_window


if __name__ == "__main__":
    app, main_window = main()
    sys.exit(app.exec_())
