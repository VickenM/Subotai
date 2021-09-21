from PySide2 import QtWidgets
from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Slot


class PywerItem(QtWidgets.QGraphicsItem):
    def __init__(self, *args, **kwargs):
        self.type_ = kwargs.pop('type', '')
        super(PywerItem, self).__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemNegativeZStacksBehindParent)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

        self.setAcceptHoverEvents(True)
        self.setZValue(1)

    def adjust(self):
        return

    def sceneEvent(self, event):
        return super(PywerItem, self).sceneEvent(event)

    def hoverEnterEvent(self, event):
        return super(PywerItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        return super(PywerItem, self).hoverLeaveEvent(event)

    def mouseMoveEvent(self, event):
        return super(PywerItem, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        return super(PywerItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        return super(PywerItem, self).mouseReleaseEvent(event)


class PywerEdge(PywerItem):
    def __init__(self, *args, **kwargs):
        super(PywerEdge, self).__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)

        self.arrow_size = 5.0
        self.line_width = 1.5
        self.color = (255, 120, 150, 255)

        self.source_plug = None
        self.target_plug = None
        self.target_position = None

        self.start = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setZValue(0)

    def add_plug(self, plug):
        if plug.is_input():
            self.target_plug = plug
        elif plug.is_output():
            self.source_plug = plug

    def connect_plugs(self, plug1, plug2, change_direction=False):
        source_plug, target_plug = plug1, plug2

        if not change_direction:
            if plug1.is_output():
                source_plug, target_plug = plug1, plug2
            else:
                source_plug, target_plug = plug2, plug1

        self.source_plug = source_plug
        self.target_plug = target_plug
        self.source_plug.add_edge(self)
        self.target_plug.add_edge(self)
        self.adjust()

    def disconnect(self):
        self.source_plug.remove_edge(self)
        self.target_plug.remove_edge(self)

    def adjust(self):
        if self.target_position:
            self.start = self.target_position
            self.end = self.target_position

        if self.source_plug:
            self.color = self.source_plug.color
            self.start = self.mapFromItem(self.source_plug, self.source_plug.boundingRect().center())

        if self.target_plug:
            self.color = self.target_plug.color
            self.end = self.mapFromItem(self.target_plug, self.target_plug.boundingRect().center())

        self.prepareGeometryChange()

    def boundingRect(self):
        # a little extra for the center arrow
        # should calculate this properly with trig
        penWidth = 1
        extra = (self.arrow_size + penWidth) / 2

        return QtCore.QRectF(self.start,
                             QtCore.QSizeF(self.end.x() - self.start.x(),
                                           self.end.y() - self.start.y())).normalized().adjusted(-extra, -extra, extra,
                                                                                                 extra)

    def paint(self, painter, option, widget):
        import math

        painter.setClipRect(option.exposedRect)

        center = QtCore.QPointF((self.start + self.end) / 2)
        c1 = QtCore.QPointF(center.x(), self.start.y())
        c2 = QtCore.QPointF(center.x(), self.end.y())

        shape = QtGui.QPainterPath()
        shape.moveTo(self.start)
        shape.cubicTo(c1, c2, self.end)

        percent = 0.5
        center = shape.pointAtPercent(percent)

        angle_up = math.radians(shape.angleAtPercent(percent) + 60)
        cos = math.cos(angle_up)
        sin = math.sin(angle_up)

        shape.moveTo(center)
        shape.lineTo(center.x() - self.arrow_size * sin, center.y() - self.arrow_size * cos)

        angle_down = math.radians(shape.angleAtPercent(percent) - 60)
        cos = math.cos(angle_down)
        sin = math.sin(angle_down)

        shape.moveTo(center)
        shape.lineTo(center.x() + self.arrow_size * sin, center.y() + self.arrow_size * cos)

        pen = QtGui.QPen(QtGui.QColor(*self.color))

        pen.setWidthF(self.line_width)
        painter.setPen(pen)
        painter.drawPath(shape)


ELLIPSE = QtGui.QPainterPath()
ELLIPSE.addEllipse(QtCore.QPointF(5, 5), 5, 5)

PENTAGON = QtGui.QPainterPath()
PENTAGON.addPolygon(QtGui.QPolygonF([
    QtCore.QPointF(0, 0),
    QtCore.QPointF(5, 0),
    QtCore.QPointF(10, 5),
    QtCore.QPointF(5, 10),
    QtCore.QPointF(0, 10),
    QtCore.QPointF(0, 0)
]))

RECTANGLE = QtGui.QPainterPath()
RECTANGLE.addRect(QtCore.QRect(0, 0, 10, 20))

CUBES = QtGui.QPainterPath()
CUBES.addRect(QtCore.QRect(0, 0, 5, 5))
CUBES.addRect(QtCore.QRect(0, 10, 5, 5))
CUBES.addRect(QtCore.QRect(10, 0, 5, 5))
CUBES.addRect(QtCore.QRect(10, 10, 5, 5))


class PywerPlug(PywerItem):
    ELLIPSE = ELLIPSE
    PENTAGON = PENTAGON
    RECTANGLE = RECTANGLE
    CUBES = CUBES

    def __init__(self, *args, **kwargs):
        self.plug_obj = kwargs.pop('plug_obj', None)

        self.path = kwargs.pop('path', self.ELLIPSE)
        self.color = kwargs.pop('color', (255, 150, 180, 255))

        super(PywerPlug, self).__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemNegativeZStacksBehindParent)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, enabled=False)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

        self.thickness = 1.5

        self.edges = []

    def boundingRect(self):
        return self.path.boundingRect()

    def shape(self):
        return self.path

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        pen_color = QtCore.Qt.black
        pen = QtGui.QPen(pen_color)
        pen.setWidthF(self.thickness)
        pen.setColor(QtGui.QColor(*self.color))
        painter.setPen(pen)

        painter.setBrush(QtGui.QColor(*self.color))
        path = self.shape()

        if len(self.edges):
            painter.drawPath(path)
        else:
            painter.strokePath(path, pen)

    def is_input(self):
        return self in self.parentItem().inputs

    def is_output(self):
        return self in self.parentItem().outputs

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)
        self.update()

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        self.update()

    def first_edge(self):
        if self.edges:
            return self.edges[0]
        return None


class PywerSpinner(PywerItem):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.color = QtGui.QColor(0, 0, 0)
        self.timeline = QtCore.QTimeLine()
        self.timeline.setLoopCount(0)
        self.timeline.setDuration(500)
        self.timeline.setFrameRange(0, 255)
        self.timeline.setEasingCurve(QtCore.QEasingCurve(QtCore.QEasingCurve.SineCurve))
        self.timeline.valueChanged.connect(self.next_frame)

    def next_frame(self, frame):
        self.color = QtGui.QColor(0, 255 * frame, 0, 255 * frame)
        self.update()

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, 20, 20)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        shape = QtGui.QPainterPath()
        shape.addEllipse(QtCore.QPointF(10, 10, ), 5, 5)

        painter.setBrush(self.color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawPath(shape)


class Glow(QtWidgets.QGraphicsDropShadowEffect):
    def __init__(self):
        super().__init__()
        self.setColor(QtGui.QColor(150, 25, 25, 200))
        self.setXOffset(0)
        self.setYOffset(0)
        self.setBlurRadius(0)

        self.timeline = QtCore.QTimeLine()
        self.timeline.setLoopCount(0)
        self.timeline.setDuration(1000)
        self.timeline.setFrameRange(100, 105)
        self.timeline.setEasingCurve(QtCore.QEasingCurve(QtCore.QEasingCurve.SineCurve))
        self.timeline.valueChanged.connect(self.next_frame)

    def next_frame(self, frame):
        self.setBlurRadius(frame * 100)


class PywerNode(PywerItem):
    name_ = 'name'

    def __init__(self, *args, **kwargs):
        self.node_obj = kwargs.pop('node_obj', None)
        self.header_color = kwargs.pop('color', (35, 105, 140, 200))
        super(PywerNode, self).__init__(*args, **kwargs)

        self.width = 100
        self.height = 50
        self.corner_radius = 5
        self.plug_spacing = 8
        self.header_height = 20

        self.old_position = None
        self.old_selection = None

        self.active_text_color = QtCore.Qt.white
        self.inactive_text_color = QtCore.Qt.gray
        self.base_color = (25, 25, 25, 200)
        self.selected_color = (255, 165, 0, 255)

        self.setFlag(self.ItemIsMovable)

        self.inputs = []
        self.outputs = []

        self.active = True

        self.name = QtWidgets.QGraphicsTextItem(parent=self)
        font = self.name.font()
        font.setPointSize(8)
        self.name.setFont(font)
        self.name.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.name.setPlainText(self.name_)
        self.name.setDefaultTextColor(QtCore.Qt.white)
        self.name.setPos(self.pos().x(), self.pos().y() - 20)

        self.spinner = PywerSpinner(parent=self)
        self.spinner.hide()

        self.drop_shadow = Glow()

        self.resizer = Resizer(parent=self)
        self.resizer.setConstrainY(True)
        self.resizer.resize_signal.connect(self.resize)
        self.adjust()

    def set_old_position(self, position):
        self.old_position = position

    def get_old_position(self):
        return self.old_position

    def set_old_selection(self, selection):
        self.old_selection = selection

    def get_old_selection(self):
        return self.old_selection

    @Slot()
    def start_spinner(self):
        self.spinner.show()
        if not self.spinner.timeline.state():
            self.spinner.timeline.start()

    @Slot()
    def stop_spinner(self):
        self.spinner.hide()
        if self.spinner.timeline.state():
            self.spinner.timeline.stop()

    @Slot(int)
    def show_glow(self, color):
        if not self.drop_shadow.timeline.state():
            self.drop_shadow = Glow()
            self.drop_shadow.setColor(QtGui.QColor(*color))
            self.setGraphicsEffect(self.drop_shadow)
            self.drop_shadow.timeline.start()

    @Slot()
    def clear_glow(self):
        if self.drop_shadow.timeline.state():
            self.drop_shadow.timeline.stop()
        self.setGraphicsEffect(None)

    @Slot(QtCore.QPointF)
    def resize(self, change):
        rect = QtCore.QRectF(0, 0, self.width, self.height).adjusted(0, 0, change.x(), change.y())
        self.width = rect.width()
        self.height = rect.height()
        self.prepareGeometryChange()
        self.adjust()
        self.updateEdges()

    @classmethod
    def from_dict(cls, blueprint):
        attribs = blueprint.get('attribs', {})
        node = cls(**attribs)

        for i in blueprint.get('inputs', []):
            node.add_input(PywerPlug(**i))
        for i in blueprint.get('outputs', []):
            node.add_output(PywerPlug(**i))
        return node

    def is_active(self):
        return self.node_obj.is_active()

    def set_active(self, state):
        self.active = state
        self.update()

    def add_input(self, plug):
        plug.setParentItem(self)
        self.inputs.append(plug)
        self.adjust()
        self.resizer.setMinSize(QtCore.QPointF(100, self.height))

    def remove_input(self, plug):
        self.inputs.remove(plug)
        plug.setParentItem(None)
        self.adjust()
        self.resizer.setMinSize(QtCore.QPointF(100, self.height))

    def add_output(self, plug):
        plug.setParentItem(self)
        self.outputs.append(plug)
        self.adjust()
        self.resizer.setMinSize(QtCore.QPointF(100, self.height))

    def adjust(self):
        y = self.plug_spacing + self.header_height
        for p in self.inputs:
            p.setPos(QtCore.QPointF(0.5 * p.boundingRect().width(), y))
            y += p.boundingRect().height() + self.plug_spacing

        y = self.plug_spacing + self.header_height
        for p in self.outputs:
            p.setPos(QtCore.QPointF(self.width - (1.5 * p.boundingRect().width()), y))
            y += p.boundingRect().height() + self.plug_spacing

        if self.inputs + self.outputs:
            self.height = max(
                [plug.y() + plug.boundingRect().height() + self.plug_spacing for plug in self.inputs + self.outputs])

        # self.height = max([self.height, self.resizer.pos().y() + self.resizer.rect.height()])

        resizer_width = self.resizer.rect.width()
        resizer_offset = QtCore.QPointF(resizer_width, resizer_width)
        rect = QtCore.QRectF(0, 0, self.width, self.height)
        self.resizer.setFlag(self.resizer.ItemSendsGeometryChanges, False)
        self.resizer.setPos(rect.bottomRight() - resizer_offset)
        self.resizer.setFlag(self.resizer.ItemSendsGeometryChanges, True)

        self.spinner.setPos(QtCore.QPointF(self.width - 20, 0))

    def setSize(self, width, height):
        self.width, self.height = width, height
        self.adjust()
        self.update()

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, self.width, self.height).adjusted(-0.5, -0.5, 0.5, 0.5)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        shape = QtGui.QPainterPath()
        shape.addRoundedRect(0, 0, self.width, self.height, self.corner_radius, self.corner_radius)

        color1 = QtGui.QColor(*self.header_color)
        color2 = QtGui.QColor(*self.base_color)

        gradient_amount = self.header_height
        gradient = QtGui.QLinearGradient(50, self.header_height - gradient_amount, 50, self.header_height)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)

        if self.isSelected():
            pen = QtGui.QPen(QtGui.QColor(*self.selected_color), 1.5)
            painter.setPen(pen)

        # for plug in self.inputs + self.outputs:
        #     cshape = plug.shape()
        #     cshape = cshape.translated(plug.pos())
        #
        #     shape = shape.subtracted(cshape)

        painter.setBrush(gradient)
        painter.drawPath(shape)

        font = QtGui.QFont()
        font.setPointSize(10)
        font_metrics = QtGui.QFontMetrics(font)
        font_height = font_metrics.height()
        painter.setFont(font)

        text_color = self.active_text_color
        if not self.is_active():
            text_color = self.inactive_text_color
        pen = QtGui.QPen(text_color)
        pen.setWidthF(0.1)
        painter.setPen(pen)
        painter.drawText(10, font_height, self.type_)

        pen.setColor(QtCore.Qt.white)
        painter.setPen(pen)

        for plug in self.inputs:
            rect = plug.boundingRect()
            pos = plug.pos()
            x, y = pos.x() + rect.right() + 5, pos.y() + rect.bottom()
            painter.drawText(x, y, plug.type_)

        for plug in self.outputs:
            width = font_metrics.width(plug.type_)
            rect = plug.boundingRect()
            pos = plug.pos()
            x, y = pos.x() - width - 5, pos.y() + rect.bottom()
            painter.drawText(x, y, plug.type_)

    def updateEdges(self):
        for plug in self.inputs + self.outputs:
            for edge in plug.edges:
                edge.adjust()

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            self.updateEdges()

        return super(PywerNode, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.old_position = self.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        return super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        return super().hoverMoveEvent(event)

    def hoverEnterEvent(self, event):
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        return super().hoverLeaveEvent(event)


class Resizer(QtWidgets.QGraphicsObject):
    resize_signal = QtCore.Signal(QtCore.QPointF)

    def __init__(self, rect=QtCore.QRectF(0, 0, 10, 10), parent=None):
        super().__init__(parent)
        self.rect = rect

        self._constrainX = False
        self._constrainY = False

        self._min_size = QtCore.QPointF(0, 0)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

    def setMinSize(self, size):
        self._min_size = size

    def setConstrainX(self, value):
        self._constrainX = value

    def setConstrainY(self, value):
        self._constrainY = value

    def constrainX(self):
        return self._constrainX

    def constrainY(self):
        return self._constrainY

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setClipRect(option.exposedRect)

        width = self.rect.width()
        height = self.rect.height()

        painter.setBrush(QtGui.QColor(100, 100, 100))
        painter.setPen(QtGui.QColor(150, 150, 150))
        for i in range(0, int(width / 3) * 3, int(width / 3)):
            painter.drawLine(i, height - 2, width - 2, i)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            width = self.boundingRect().width()
            height = self.boundingRect().height()
            if self.isSelected():
                if self.constrainY():
                    value.setY(self.pos().y())
                if self.constrainX():
                    value.setX(self.pos().x())
                if value.x() < self._min_size.x() - width:
                    value.setX(self._min_size.x() - width)
                if value.y() < self._min_size.y() - height:
                    value.setY(self._min_size.y() - height)
                self.resize_signal.emit(value - self.pos())
                # self.scene().itemMoved()
        return value

    def hoverEnterEvent(self, event):
        QApplication.setOverrideCursor(QtCore.Qt.SizeFDiagCursor)
        return super(Resizer, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        QApplication.restoreOverrideCursor()
        return super(Resizer, self).hoverLeaveEvent(event)


class PywerGroup(PywerItem):
    name_ = 'name'

    def __init__(self, *args, **kwargs):
        super(PywerGroup, self).__init__(*args, **kwargs)

        self.type_ = 'Group'
        self.width = 100
        self.height = 100
        self.header_height = 20
        self.header_color = (200, 200, 200, 155)
        self.base_color = (75, 75, 75, 100)
        self.selected_color = (255, 165, 0, 255)

        self.old_position = None
        self.old_selection = None

        self.setFlag(self.ItemIsMovable)

        self.name = QtWidgets.QGraphicsTextItem(parent=self)
        font = self.name.font()
        font.setPointSize(8)
        self.name.setFont(font)
        self.name.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.name.setPlainText(self.name_)
        self.name.setDefaultTextColor(QtCore.Qt.white)
        self.name.setPos(self.pos().x(), self.pos().y() - 20)

        self.resizer = Resizer(parent=self)
        self.resizer.resize_signal.connect(self.resize)
        self.adjust()

        self.setZValue(-1)

        self.contained_nodes = []

        self.move_children = True

    def set_old_position(self, position):
        self.old_position = position

    def get_old_position(self):
        return self.old_position

    def set_old_selection(self, selection):
        self.old_selection = selection

    def get_old_selection(self):
        return self.old_selection

    @Slot(QtCore.QPointF)
    def resize(self, change):
        rect = QtCore.QRectF(0, 0, self.width, self.height).adjusted(0, 0, change.x(), change.y())
        self.width = rect.width()
        self.height = rect.height()
        self.prepareGeometryChange()
        self.update()

    def adjust(self):
        resizer_width = self.resizer.rect.width() / 2
        resizer_offset = QtCore.QPointF(resizer_width * 2, resizer_width * 2)
        rect = QtCore.QRectF(0, 0, self.width, self.height)
        self.resizer.setPos(rect.bottomRight() - resizer_offset)

    def setSize(self, width, height):
        self.width, self.height = width, height
        self.adjust()
        self.update()

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, self.width, self.height)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        shape = QtGui.QPainterPath()
        shape.addRect(0, 0, self.width, self.height)

        color1 = QtGui.QColor(*self.header_color)
        color2 = QtGui.QColor(*self.base_color)

        gradient_amount = self.header_height
        gradient = QtGui.QLinearGradient(50, self.header_height - gradient_amount, 50, self.header_height)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)

        if self.isSelected():
            pen = QtGui.QPen(QtGui.QColor(*self.selected_color))
            painter.setPen(pen)

        painter.setBrush(gradient)
        painter.drawPath(shape)

        font = QtGui.QFont()
        font.setPointSize(10)
        font_metrics = QtGui.QFontMetrics(font)
        font_height = font_metrics.height()
        painter.setFont(font)

        pen = QtGui.QPen(QtCore.Qt.white)
        pen.setWidthF(0.1)
        painter.setPen(pen)

        painter.drawText(10, font_height, self.type_)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange and self.scene() and self.move_children:
            pos = value
            for node in self.contained_nodes:
                diff = pos - self.pos()
                node.moveBy(diff.x(), diff.y())
            # self.scene().itemMoved(self)
            return value

        return super(PywerGroup, self).itemChange(change, value)

    def mouseReleaseEvent(self, event):
        for node in self.contained_nodes:
            if isinstance(node, PywerGroup):
                node.move_children = True
        return super(PywerGroup, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        self.contained_nodes = []
        bounding_rect = self.sceneBoundingRect()

        all_nodes = [item for item in self.scene().items() if isinstance(item, PywerNode) or \
                     (isinstance(item, PywerGroup) and item != self)
                     ]
        for node in all_nodes:
            if bounding_rect.contains(node.sceneBoundingRect()):
                self.contained_nodes.append(node)

                if isinstance(node, PywerGroup):
                    node.move_children = False
        return super(PywerGroup, self).mousePressEvent(event)
