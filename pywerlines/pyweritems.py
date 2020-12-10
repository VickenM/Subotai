from PySide2 import QtWidgets
from PySide2 import QtCore, QtGui


class PywerItem(QtWidgets.QGraphicsItem):
    def __init__(self, *args, **kwargs):
        super(PywerItem, self).__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemNegativeZStacksBehindParent)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

        self.setAcceptHoverEvents(True)
        self.setZValue(1)

    def setSelected(self, state):
        self.selected = state
        self.update()

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

        self.arrow_size = 5.0
        self.color = (255, 120, 150, 255)

        self.source_plug = None
        self.target_plug = None
        self.target_position = None

        self.start = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setZValue(0)

    def adjust(self):
        if self.target_position:
            self.start = self.target_position
            self.end = self.target_position

        if self.source_plug:
            self.start = self.mapFromItem(self.source_plug, self.source_plug.boundingRect().center())

        if self.target_plug:
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
        painter.setClipRect(option.exposedRect)

        start = self.start
        end = self.end

        center = QtCore.QPointF((start + end) / 2)
        c1 = QtCore.QPointF(center.x(), start.y())
        c2 = QtCore.QPointF(center.x(), end.y())

        shape = QtGui.QPainterPath()
        shape.moveTo(start)
        shape.cubicTo(c1, c2, end)

        percent = 0.5
        center = shape.pointAtPercent(percent)

        import math
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

        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPath(shape)


class PywerPlug(PywerItem):
    def __init__(self, *args, **kwargs):
        super(PywerPlug, self).__init__(*args, **kwargs)

        self.radius = 5
        self.thickness = 2
        self.color = (255, 120, 150, 255)

        self.edges = []

    def boundingRect(self):
        diameter = 2 * self.radius
        bbox = QtCore.QRectF(0, 0, diameter, diameter)
        bbox.adjust(-0.5, -0.5, 0.5, 0.5)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        pen_color = QtCore.Qt.black
        pen = QtGui.QPen(pen_color)
        pen.setWidthF(0.1)
        painter.setPen(pen)

        painter.setBrush(QtGui.QColor(*self.color))

        inner_radius = self.radius - self.thickness
        path = QtGui.QPainterPath()
        path.addEllipse(QtCore.QPointF(self.radius, self.radius), self.radius, self.radius)

        if not len(self.edges):
            path.addEllipse(QtCore.QPointF(self.radius, self.radius), inner_radius, inner_radius)

        painter.drawPath(path)


class PywerNode(PywerItem):
    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data', None)
        super(PywerNode, self).__init__(*args, **kwargs)

        self.width = 100
        self.height = 50
        self.radius = 5
        self.plug_spacing = 5
        self.header_height = 20
        self.base_color = (25, 25, 25, 200)
        self.header_color = (35, 105, 140, 200)

        self.setFlag(self.ItemIsMovable)

        self.inputs = []
        self.outputs = []

    def add_input(self, plug):
        y = self.header_height
        for p in self.inputs:
            y += 2 * p.radius + self.plug_spacing

        plug.setPos(QtCore.QPointF(-plug.radius, y))
        plug.setParentItem(self)
        self.inputs.append(plug)
        self.adjust()

    def add_output(self, plug):
        y = self.header_height
        for p in self.inputs + self.outputs:
            y += 2 * p.radius + self.plug_spacing

        plug.setPos(QtCore.QPointF(self.width - plug.radius, y))
        plug.setParentItem(self)
        self.outputs.append(plug)
        self.adjust()

    def adjust(self):
        total = 0
        for plug in self.inputs + self.outputs:
            total += 2 * plug.radius + self.plug_spacing
        self.height = self.header_height + total

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, self.width, self.height).adjusted(-0.5, -0.5, 0.5, 0.5)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        shape = QtGui.QPainterPath()
        shape.addRoundedRect(0, 0, self.width, self.height, self.radius, self.radius)

        color1 = QtGui.QColor(*self.header_color)
        color2 = QtGui.QColor(*self.base_color)

        gradient_amount = 10
        gradient = QtGui.QLinearGradient(50, self.header_height - gradient_amount, 50, self.header_height)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)

        painter.setBrush(gradient)
        painter.drawPath(shape)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for edge in self.inputs + self.outputs:
                edge.adjust()

        return super(PywerNode, self).itemChange(change, value)
