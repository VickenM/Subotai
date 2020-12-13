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
    print(data)


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

    def add_node(self, type_):
        node = super(Arithmetic, self).add_node()
        node.label = type_
        if type_ == 'Constant':
            node.add_output(plug=pyweritems.PywerPlug())
            return node

        node.add_input(plug=pyweritems.PywerPlug())
        node.add_input(plug=pyweritems.PywerPlug())
        node.add_output(plug=pyweritems.PywerPlug())
        return node


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        view = pywerlines.pywerview.PywerView()
        scene = Arithmetic() #pywerscene.PywerScene()
        scene.setSceneRect(0, 0, 1000, 1000)
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
            node = self.scene.add_node('Add')
        elif event.key() == QtCore.Qt.Key_S:
            node = self.scene.add_node('Subtract')
        elif event.key() == QtCore.Qt.Key_X:
            node = self.scene.add_node('Multiple')
        elif event.key() == QtCore.Qt.Key_D:
            node = self.scene.add_node('Divide')
        elif event.key() == QtCore.Qt.Key_C:
            node = self.scene.add_node('Constant')
        else:
            return

        position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
        node.setPos(position)


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
