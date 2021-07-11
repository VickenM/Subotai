from PySide2 import QtGui, QtCore, QtWidgets
from . import pyweritems


class PywerView(QtWidgets.QGraphicsView):
    nodes_selected = QtCore.Signal(list)
    nodes_deleted = QtCore.Signal(list)

    def __init__(self):
        super(PywerView, self).__init__()

        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)

        # self.setTransformationAnchor(self.NoAnchor)
        # self.setResizeAnchor(self.NoAnchor)

        self._scale = 1.0
        self.scale(1.0, 1.0)

        self.drag_edge = None
        self.disconnected_plug = None

        self.mouse_position = None

    def setScene(self, scene):
        super(PywerView, self).setScene(scene)

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

    def get_plug_at(self, position):
        items = self.items(position) or []
        items = [i for i in items if isinstance(i, pyweritems.PywerPlug)]
        if not items:
            return None
        return items[0]

    def scaleView(self, scaleFactor):
        self.scale(scaleFactor, scaleFactor)

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            zoomInFactor = 1.10
            zoomOutFactor = 1 / zoomInFactor

            # Save the scene pos
            oldPos = self.mapToScene(event.pos())

            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)

            # Get the new position
            newPos = self.mapToScene(event.pos())

            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())
            return
            # amount = event.angleDelta().y() / 10
            # amount = amount / 360
            # self._scale = self._scale + amount
            #
            # self.resetMatrix()
            # self.scale(self._scale, self._scale)
            # return
        return super(PywerView, self).wheelEvent(event)

    def _drag_edge(self, position):
        plug = self.get_plug_at(position=position)
        if plug and plug.edges and (plug == plug.edges[0].target_plug):
            edge = plug.edges[0]
            if plug == edge.target_plug:
                self.drag_edge = edge
                self.drag_edge.target_plug = None
                self.disconnected_plug = plug
                plug.remove_edge(edge)
                plug.update()
        elif plug:
            self.drag_edge = pyweritems.PywerEdge()
            plug.add_edge(self.drag_edge)
            self.drag_edge.add_plug(plug)
            self.scene().addItem(self.drag_edge)

    def _drop_edge(self, position):
        if self.drag_edge:
            dragged_from_plug = self.drag_edge.source_plug or self.drag_edge.target_plug
            mouse_over_plug = self.get_plug_at(position=position)
            if self.scene().can_connect(dragged_from_plug, mouse_over_plug):
                self.drag_edge.connect_plugs(dragged_from_plug, mouse_over_plug)
                if mouse_over_plug != self.disconnected_plug:
                    if dragged_from_plug in dragged_from_plug.parentItem().outputs:
                        source_plug = dragged_from_plug
                        target_plug = mouse_over_plug
                    else:
                        source_plug = mouse_over_plug
                        target_plug = dragged_from_plug
                    self.scene().emit_connected_plugs(source_plug, target_plug)
            else:
                dragged_from_plug.remove_edge(self.drag_edge)
                self.scene().removeItem(self.drag_edge)

            if self.disconnected_plug and (mouse_over_plug != self.disconnected_plug):
                self.scene().emit_disconnected_plugs(dragged_from_plug, self.disconnected_plug)
            self.disconnected_plug = None
            self.drag_edge = None

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_position = event.pos()
        mouse_position = event.pos()
        if self.drag_edge:
            self.drag_edge.target_position = self.mapToScene(mouse_position)
            self.drag_edge.adjust()
        super(PywerView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        button = event.button()
        if (button == QtCore.Qt.LeftButton) and (self.dragMode() == self.RubberBandDrag):
            self._drag_edge(position=event.pos())
        # elif button == QtCore.Qt.RightButton:
        #     self.setDragMode(self.ScrollHandDrag)
        #     press_event = QtGui.QMouseEvent(QtCore.QEvent.GraphicsSceneMousePress,
        #                                     event.pos(), QtCore.Qt.MouseButton.LeftButton,
        #                                     QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier
        #                                     )
        #     self.mousePressEvent(press_event)
        super(PywerView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            self._drop_edge(position=event.pos())
            self.scene().emit_selected_nodes()
        elif button == QtCore.Qt.RightButton:
            self.setDragMode(self.RubberBandDrag)

        super(PywerView, self).mouseReleaseEvent(event)
