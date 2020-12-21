import sys
import pywerlines.pywerview

from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QGraphicsScene
from PySide2 import QtCore
from PySide2.QtCore import Slot

from pywerlines import pyweritems, pywerscene


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


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def disconnected_plugs(plug1, plug2):
    print('disconnected')


class Arithmetic(pywerscene.PywerScene):
    def list_node_types(self):
        return [
            'Add',
            'Subtract',
            'Multiply',
            'Divide'
        ]

    def new_node(self, type_):
        if type_ == 'Constant':
            blueprint = {
                'attribs': {
                    'type': 'Constant', 'color': (55, 150, 55, 255)
                },
                'inputs': [],
                'outputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'Value', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ]
            }
            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
        elif type_ == 'Add':
            blueprint = {
                'attribs': {
                    'type': 'Add'
                },
                'inputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'In1', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                    {'type': 'In2', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ],
                'outputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'Value', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ]
            }
            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
        elif type_ == 'Subtract':
            blueprint = {
                'attribs': {
                    'type': 'Subtract'
                },
                'inputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'In1', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                    {'type': 'In2', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ],
                'outputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'Value', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ]
            }
            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)
        elif type_ == 'Components':
            blueprint = {
                'attribs': {
                    'type': 'Components', 'color': (150, 0, 0, 255)
                }, 'inputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'In1', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ],
                'outputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'Red', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                    {'type': 'Green', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                    {'type': 'Blue', 'path': pyweritems.PywerPlug.ELLIPSE, 'color': (255, 120, 150, 255)},
                ]
            }
            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)

        elif type_ == 'Output':
            blueprint = {
                'attribs': {
                    'type': 'Output'
                }, 'inputs': [
                    {'type': '', 'path': pyweritems.PywerPlug.PENTAGON, 'color': (255, 255, 255, 255)},
                    {'type': 'Multi', 'path': pyweritems.PywerPlug.RECTANGLE, 'color': (255, 120, 150, 255)},
                ],
                'outputs': []
            }
            node = pyweritems.PywerNode.from_dict(blueprint=blueprint)

        return node

    def create_node_of_type(self, type_):
        node = self.new_node(type_)
        self.add_node(node)
        return node

    def create_edge(self, source_plug, target_plug):
        super(Arithmetic, self).create_edge(source_plug, target_plug)

    def eval(self):
        print('evaluating')


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        view = pywerlines.pywerview.PywerView()
        scene = Arithmetic()
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

        # c1 = scene.create_node_of_type('Constant')
        # c2 = scene.create_node_of_type('Constant')
        # a = scene.create_node_of_type('Add')
        # scene.create_edge(c1.outputs[1], a.inputs[1])
        # scene.create_edge(c2.outputs[1], a.inputs[2])

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_A:
            node = self.scene.create_node_of_type('Add')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_S:
            node = self.scene.create_node_of_type('Subtract')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_C:
            node = self.scene.create_node_of_type('Constant')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_R:
            node = self.scene.create_node_of_type('Components')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_O:
            node = self.scene.create_node_of_type('Output')
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
