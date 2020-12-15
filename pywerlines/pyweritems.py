from PySide2 import QtWidgets
from PySide2 import QtCore, QtGui


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

        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPath(shape)


class PywerPlug(PywerItem):
    def __init__(self, *args, **kwargs):
        super(PywerPlug, self).__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemNegativeZStacksBehindParent)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, enabled=False)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

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


class PywerNode(PywerItem):
    def __init__(self, *args, **kwargs):
        self.node_obj = kwargs.pop('node_obj', None)
        super(PywerNode, self).__init__(*args, **kwargs)

        self.width = 100
        self.height = 50
        self.radius = 5
        self.plug_spacing = 8
        self.header_height = 20
        self.header_color = (35, 105, 140, 200)

        self.base_color = (25, 25, 25, 200)
        self.selected_color = (190, 190, 0, 255)

        self.setFlag(self.ItemIsMovable)

        self.inputs = []
        self.outputs = []

        self.label = QtWidgets.QGraphicsTextItem(parent=self)
        font = self.label.font()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.label.setPlainText('name')
        self.label.setDefaultTextColor(QtCore.Qt.white)
        self.label.setPos(self.pos().x(), self.pos().y() - 20)

    @classmethod
    def from_dict(cls, blueprint):
        node = cls()
        node.type_ = blueprint.get('type', '')

        for i in blueprint.get('inputs', []):
            node.add_input(PywerPlug(type=i))
        for i in blueprint.get('outputs', []):
            node.add_output(PywerPlug(type=i))
        return node

    def add_input(self, plug):
        y = self.header_height + self.plug_spacing
        for p in self.inputs:
            y += 2 * p.radius + self.plug_spacing

        plug.setPos(QtCore.QPointF(-plug.radius, y))
        plug.setParentItem(self)
        self.inputs.append(plug)
        self.adjust()

    def add_output(self, plug):
        y = self.header_height
        if not self.inputs:
            y += self.plug_spacing
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
        if not self.inputs:
            total += self.plug_spacing
        self.height = total + self.header_height

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, self.width, self.height).adjusted(-0.5, -0.5, 0.5, 0.5)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        shape = QtGui.QPainterPath()
        shape.addRoundedRect(0, 0, self.width, self.height, self.radius, self.radius)

        color1 = QtGui.QColor(*self.header_color)
        color2 = QtGui.QColor(*self.base_color)

        gradient_amount = 2
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

        for plug in self.inputs:
            rect = plug.boundingRect()
            pos = plug.pos()
            x, y = pos.x() + rect.right(), pos.y() + rect.bottom()
            painter.drawText(x, y, plug.type_)

        for plug in self.outputs:
            width = font_metrics.width(plug.type_)
            rect = plug.boundingRect()
            pos = plug.pos()
            x, y = pos.x() - width, pos.y() + rect.bottom()
            painter.drawText(x, y, plug.type_)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for plug in self.inputs + self.outputs:
                for edge in plug.edges:
                    edge.adjust()

        return super(PywerNode, self).itemChange(change, value)


class Grip(QtWidgets.QGraphicsItem):
    def __init__(self, *args, **kwargs):
        super(Grip, self).__init__(*args, **kwargs)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setFlag(self.ItemIsFocusable)
        self.setFlag(self.ItemIsSelectable)

        self.width = 10
        self.height = 10

        parent = self.parentItem()

        self.setFlag(self.ItemSendsGeometryChanges, False)
        self.setPos(parent.width - self.width, parent.height - self.height)
        self.setFlag(self.ItemSendsGeometryChanges, True)

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, self.width, self.height).adjusted(-0.1, -0.1, 0.1, 0.1)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        painter.setBrush(QtGui.QColor(100, 100, 100))
        painter.setPen(QtGui.QColor(150, 150, 150))

        # shape = QtGui.QPainterPath()
        # shape.addRect(0, 0, self.width, self.height)
        # painter.drawPath(shape)

        for i in range(0, int(self.width / 3) * 3, int(self.width / 3)):
            painter.drawLine(i, self.height - 2, self.width - 2, i)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            newPos = value
            newPos.setX(max(self.width, newPos.x()))
            newPos.setY(max(self.height, newPos.y()))

            parent = self.parentItem()

            # method 1
            # diff = newPos - self.lastPos
            # parent.width += diff.x()
            # parent.height += diff.y()
            # self.lastPos = newPos

            # method 2
            scene_pos = self.mapToScene(newPos)
            parent.width = (scene_pos.x() - parent.x()) / 2 + self.width
            parent.height = (scene_pos.y() - parent.y()) / 2 + self.height
            parent.update()

            return newPos

        return super(Grip, self).itemChange(change, value)


class PywerGroup(PywerItem):
    def __init__(self, *args, **kwargs):
        super(PywerGroup, self).__init__(*args, **kwargs)

        self.width = 100
        self.height = 100
        self.header_height = 20
        self.header_color = (35, 105, 140, 200)

        self.base_color = (125, 125, 125, 100)
        self.selected_color = (190, 190, 0, 255)

        self.setFlag(self.ItemIsMovable)

        self.label = QtWidgets.QGraphicsTextItem(parent=self)
        font = self.label.font()
        font.setPointSize(8)
        self.label.setFont(font)
        self.label.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.label.setPlainText('group name')
        self.label.setDefaultTextColor(QtCore.Qt.white)
        self.label.setPos(self.pos().x(), self.pos().y() - 20)

        self.grip = Grip(parent=self)

        self.setZValue(-1)

    def boundingRect(self):
        bbox = QtCore.QRectF(0, 0, self.width, self.height)  # .adjusted(-0.5, -0.5, 0.5, 0.5)
        return bbox

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)

        shape = QtGui.QPainterPath()
        shape.addRect(0, 0, self.width, self.height)

        color1 = QtGui.QColor(*self.header_color)
        color2 = QtGui.QColor(*self.base_color)

        gradient_amount = 2
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
        painter.setFont(font)

        pen = QtGui.QPen(QtCore.Qt.white)
        pen.setWidthF(0.1)
        painter.setPen(pen)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange and self.scene():
            pos = value
            # print(pos, self.pos())
            all_nodes = [item for item in self.scene().items() if isinstance(item, PywerNode)]
            bounding_rect = self.sceneBoundingRect()
            for node in all_nodes:
                if bounding_rect.contains(node.sceneBoundingRect()):
                    diff = pos - self.pos()
                    node.moveBy(diff.x(), diff.y())

            return value

        return super(PywerGroup, self).itemChange(change, value)
