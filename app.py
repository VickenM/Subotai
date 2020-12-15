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
    print('connected')
    # print(plug1, plug2)


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def disconnected_plugs(plug1, plug2):
    # print(plug1, plug2)
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
            bluepint = {
                'type': 'Constant',
                'inputs': [],
                'outputs': ['value']
            }
            node = pyweritems.PywerNode.from_dict(blueprint=bluepint)
        elif type_ == 'Add':
            bluepint = {
                'type': 'Add',
                'inputs': ['in1', 'in2'],
                'outputs': ['value']
            }
            node = pyweritems.PywerNode.from_dict(blueprint=bluepint)
        elif type_ == 'Subtract':
            bluepint = {
                'type': 'Subtract',
                'inputs': ['in1', 'in2'],
                'outputs': ['value']
            }
            node = pyweritems.PywerNode.from_dict(blueprint=bluepint)
        elif type_ == 'Components':
            bluepint = {
                'type': 'Components',
                'inputs': ['RGB', ],
                'outputs': ['Red', 'Green', 'Blue']
            }
            node = pyweritems.PywerNode.from_dict(blueprint=bluepint)

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
        scene = Arithmetic()  # pywerscene.PywerScene()
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
        if event.key() == QtCore.Qt.Key_A:
            node = self.scene.new_node('Add')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_S:
            node = self.scene.new_node('Subtract')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_C:
            node = self.scene.new_node('Constant')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_R:
            node = self.scene.new_node('Components')
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            node.setPos(position)
        elif event.key() == QtCore.Qt.Key_G:
            group = pyweritems.PywerGroup()
            position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
            group.setPos(position)
            self.scene.addItem(group)
        elif event.key() == QtCore.Qt.Key_Period:
            self.scene.toggle_labels()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.scene.remove_selected_nodes()
            self.scene.remove_selected_groups()
        elif event.key() == QtCore.Qt.Key_Space:
            self.scene.eval()


if __name__ == "__main__":
    def main():
        app = QApplication(sys.argv)
        app_prototype = MainWindow()
        app_prototype.show()

        sys.exit(app.exec_())


    if __name__ == "__main__":
        if len(sys.argv) == 1:
            main()
        else:
            import cProfile

            cProfile.run('main()')
