import sys
import pywerlines.pywerview

from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QGraphicsScene

from pywerlines import pyweritems, pywerscene

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()


        view = pywerlines.pywerview.PywerView()
        scene = pywerscene.PywerScene()
        scene.setSceneRect(0, 0, 5000, 5000)
        scene.setItemIndexMethod(scene.NoIndex)
        view.setScene(scene)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        self.setLayout(layout)

        node = pyweritems.PywerNode()
        node.setPos(2250, 2500)
        scene.addItem(node)

        node.add_input(plug=pyweritems.PywerPlug())
        node.add_input(plug=pyweritems.PywerPlug())
        p1 = pyweritems.PywerPlug()
        node.add_output(plug=p1)

        node = pyweritems.PywerNode()
        node.setPos(2500, 2500)
        scene.addItem(node)

        node.add_input(plug=pyweritems.PywerPlug())
        node.add_input(plug=pyweritems.PywerPlug())
        p2 = pyweritems.PywerPlug()
        node.add_input(plug=p2)
        node.add_output(plug=pyweritems.PywerPlug())

        # view.create_edge(p1, p2)

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
