from PySide2 import QtGui, QtCore, QtWidgets
from . import pyweritems


class PywerView(QtWidgets.QGraphicsView):
    def __init__(self):
        super(PywerView, self).__init__()

        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.scale(1.0, 1.0)

        self.new_edge = None

    def setScene(self, scene):
        super(PywerView, self).setScene(scene)
        self.new_edge = pyweritems.PywerEdge()
        self.scene().addItem(self.new_edge)

    def drawBackground(self, painter, rect):
        sceneRect = self.sceneRect()

        painter.fillRect(sceneRect, QtGui.QColor(50, 50, 50))

        bottom_left = sceneRect.bottomLeft()
        top_right = sceneRect.topRight()

        painter.setPen(QtGui.QColor(75, 75, 75))
        for x in range(int(bottom_left.x()), int(top_right.x()), 25):
            painter.drawLine(x, bottom_left.y(), x, top_right.y())

        for y in range(int(top_right.y()), int(bottom_left.y()), 25):
            painter.drawLine(bottom_left.x(), y, top_right.x(), y)

        painter.setPen(QtGui.QColor(25, 25, 25))
        for x in range(int(bottom_left.x()), int(top_right.x()), 250):
            painter.drawLine(x, bottom_left.y(), x, top_right.y())

        for y in range(int(top_right.y()), int(bottom_left.y()), 250):
            painter.drawLine(bottom_left.x(), y, top_right.x(), y)

    def drag_edge_from(self, plug):
        if not plug:
            return None

        self.new_edge.source_plug = plug
        self.new_edge.show()

    def get_plug_at(self, position):
        if not position:
            return None

        items = self.items(position) or []
        items = [i for i in items if isinstance(i, pyweritems.PywerPlug)]
        if not items:
            return None
        return items[0]

    def perform_new_connection(self):
        if not self.new_edge.target_position:
            return

        position = self.new_edge.target_position.toPoint()
        plug = self.get_plug_at(position=self.mapFromScene(position))

        if self.new_edge.source_plug:
            self.scene().create_edge(self.new_edge.source_plug, plug)
        elif self.new_edge.target_plug:
            self.scene().create_edge(plug, self.new_edge.target_plug)

        self.new_edge.source_plug = None
        self.new_edge.target_plug = None
        self.new_edge.target_position = None
        self.new_edge.start = QtCore.QPoint()
        self.new_edge.end = QtCore.QPoint()
        self.new_edge.adjust()
        self.new_edge.hide()

    def scaleView(self, scaleFactor):
        # abs_factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        # if abs_factor < 0.25 or abs_factor > 5.0:
        #    return
        self.scale(scaleFactor, scaleFactor)

    def mouseMoveEvent(self, event):
        mouse_position = event.pos()
        self.new_edge.target_position = self.mapToScene(mouse_position)
        self.new_edge.adjust()
        super(PywerView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            mouse_position = event.pos()
            plug = self.get_plug_at(position=mouse_position)
            if plug and plug.edges:
                edge = plug.edges[0]
                if plug == edge.target_plug:
                    self.scene().remove_edge(edge)
                    edge.source_plug.update()
                    edge.target_plug.update()

                    plug = edge.source_plug
                    self.new_edge.source_plug = plug
                    self.new_edge.target_plug = None
                    self.new_edge.target_position = self.mapToScene(mouse_position)
                    self.new_edge.adjust()
                    self.new_edge.show()

            self.drag_edge_from(plug=plug)
        super(PywerView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            self.perform_new_connection()
        self.update()
        if button == QtCore.Qt.RightButton:
            self.scene().remove_node(self.scene().get_selected_nodes())
        super(PywerView, self).mouseReleaseEvent(event)
