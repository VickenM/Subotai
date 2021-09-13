from PySide2 import QtGui, QtCore, QtWidgets
from . import pyweritems


class PywerView(QtWidgets.QGraphicsView):
    nodes_selected = QtCore.Signal(list)
    nodes_deleted = QtCore.Signal(list)

    def __init__(self):
        super().__init__()

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

    def setScene(self, scene):
        super().setScene(scene)

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

    def get_node_at(self, position):
        items = self.items(position) or []
        items = [i for i in items if isinstance(i, pyweritems.PywerNode)]
        if not items:
            return None
        return items[0]

    def get_plug_at(self, position):
        items = self.items(position) or []
        items = [i for i in items if isinstance(i, pyweritems.PywerPlug)]
        if not items:
            return None
        return items[0]

    def scaleView(self, scaleFactor):
        self.scale(scaleFactor, scaleFactor)

    def _is_selection_event(self, event):
        return event.button() == QtCore.Qt.LeftButton

    def _is_change_event(self, event):
        return event.button() == QtCore.Qt.LeftButton

    def _begin_select_items(self, event):
        for item in self.scene().get_all_items():
            item.set_old_selection(item.isSelected())

    def _end_select_items(self, event):
        select_changed_items = [item for item in self.scene().get_all_items() if
                                item.get_old_selection() != item.isSelected()]
        if select_changed_items:
            self.scene().itemsSelected(select_changed_items)

    def _begin_move_items(self, event):
        for item in self.scene().get_all_items():
            item.set_old_position(item.pos())

    def _end_move_items(self, event):
        moved_items = [item for item in self.scene().get_all_items() if item.get_old_position() != item.pos()]
        if moved_items:
            self.scene().itemsMoved(moved_items)

    def _is_drag_event(self, event):
        return event.button() == QtCore.Qt.LeftButton

    def _is_drop_event(self, event):
        return event.button() == QtCore.Qt.LeftButton

    def _drag_edge(self, position):
        drag_edge = None

        plug = self.get_plug_at(position=position)
        if plug and plug.edges and (plug == plug.edges[0].target_plug):
            edge = plug.edges[0]
            if plug == edge.target_plug:
                drag_edge = edge
                drag_edge.target_plug = None
                self.disconnected_plug = plug
                plug.remove_edge(edge)
                plug.update()
        elif plug:
            drag_edge = pyweritems.PywerEdge()
            plug.add_edge(drag_edge)
            drag_edge.add_plug(plug)
            self.scene().addItem(drag_edge)

        return drag_edge

    def _drop_edge(self, drag_edge, position):
        if not drag_edge:
            return

        dragged_from_plug = drag_edge.source_plug or drag_edge.target_plug
        mouse_over_plug = self.get_plug_at(position=position)
        if self.scene().can_connect(dragged_from_plug, mouse_over_plug):
            drag_edge.connect_plugs(dragged_from_plug, mouse_over_plug)
            if mouse_over_plug != self.disconnected_plug:
                if dragged_from_plug in dragged_from_plug.parentItem().outputs:
                    source_plug = dragged_from_plug
                    target_plug = mouse_over_plug
                else:
                    source_plug = mouse_over_plug
                    target_plug = dragged_from_plug
                self.scene().emit_connected_plugs(source_plug, target_plug)
        else:
            dragged_from_plug.remove_edge(drag_edge)
            self.scene().removeItem(drag_edge)

        if self.disconnected_plug and (mouse_over_plug != self.disconnected_plug):
            self.scene().emit_disconnected_plugs(dragged_from_plug, self.disconnected_plug)
        self.disconnected_plug = None

    def _is_zoom_event(self, event):
        return event.modifiers() & QtCore.Qt.ControlModifier

    def _zoom(self, event):
        zoomInFactor = 1.1
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

    def wheelEvent(self, event):
        if self._is_zoom_event(event):
            return self._zoom(event)
        return super().wheelEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        mouse_position = event.pos()
        if self.drag_edge:
            self.drag_edge.target_position = self.mapToScene(mouse_position)
            self.drag_edge.adjust()

    def mousePressEvent(self, event):

        if self._is_drag_event(event):
            self.drag_edge = self._drag_edge(event.pos())

        if self._is_change_event(event):
            self.changing_items = self.scene().get_selected_items()
            self._begin_move_items(event)
            self._begin_select_items(event)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        if self._is_drop_event(event):
            self._drop_edge(drag_edge=self.drag_edge, position=event.pos())
            self.drag_edge = None

        if self._is_change_event(event):
            self._end_move_items(event)
            self._end_select_items(event)

        super().mouseReleaseEvent(event)
