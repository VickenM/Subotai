from PySide2 import QtCore

from pywerlines import pywerview


class AppView(pywerview.PywerView):
    node_dropped_signal = QtCore.Signal(str, int, int)
    context_menu_signal = QtCore.Signal(int, int)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragMoveEvent(self, event):
        # needed to include this function for the drops to work
        pass

    def dragLeaveEvent(self, event):
        event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().data('application/x-node'):
            if event.source():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        node = event.mimeData().data('application/x-node')
        position = event.pos()

        if node:
            self.node_dropped_signal.emit(bytes(node).decode(), position.x(), position.y())
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setDragMode(self.NoDrag)
            return
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(self.RubberBandDrag)
        if event.button() == QtCore.Qt.RightButton:
            self.context_menu_signal.emit(event.pos().x(), event.pos().y())

        return super().mouseReleaseEvent(event)
