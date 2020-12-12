import sys
import pywerlines.pywerview

from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QGraphicsScene
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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        view = pywerlines.pywerview.PywerView()
        scene = pywerscene.PywerScene()
        scene.setSceneRect(0, 0, 1000, 1000)
        scene.setItemIndexMethod(scene.NoIndex)
        view.setScene(scene)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        self.setLayout(layout)

        node = pyweritems.PywerNode()
        node.setPos(250, 500)
        scene.addItem(node)
        node.add_input(plug=pyweritems.PywerPlug())
        node.add_input(plug=pyweritems.PywerPlug())
        p1 = pyweritems.PywerPlug()
        node.add_output(plug=p1)

        node = pyweritems.PywerNode()
        node.setPos(500, 500)
        scene.addItem(node)
        node.add_input(plug=pyweritems.PywerPlug())
        node.add_input(plug=pyweritems.PywerPlug())
        p2 = pyweritems.PywerPlug()
        node.add_input(plug=p2)
        node.add_output(plug=pyweritems.PywerPlug())

        node = pyweritems.PywerNode()
        node.setPos(750, 500)
        scene.addItem(node)
        node.add_input(plug=pyweritems.PywerPlug())
        node.add_input(plug=pyweritems.PywerPlug())
        node.add_output(plug=pyweritems.PywerPlug())
        node.add_output(plug=pyweritems.PywerPlug())

        scene.nodes_selected.connect(selected_nodes)
        scene.nodes_deleted.connect(deleted_nodes)
        scene.plugs_connected.connect(connected_plugs)
        scene.plugs_disconnected.connect(disconnected_plugs)


        edge = scene.create_edge(p1, p2)
        scene.remove_edge(edge)

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
