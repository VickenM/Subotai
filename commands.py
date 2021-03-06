from PySide2 import QtWidgets
from pywerlines import pyweritems
import appnode


class SelectItems(QtWidgets.QUndoCommand):
    def __init__(self, context, items):
        super().__init__()
        self.items = items
        self.scene = context.get('scene')
        self.prev_items = context.get('current_selection')

    def redo(self):
        self.scene.clearSelection()
        for item in self.items:
            item.setSelected(True)

    def undo(self):
        self.scene.clearSelection()
        for item in self.prev_items:
            item.setSelected(True)


class MoveItem(QtWidgets.QUndoCommand):
    def __init__(self, context, item):
        super().__init__()
        self.item = item
        self.new_position = item.pos()
        self.prev_scene_data = context.get('scene_data')
        self.old_position = self.item.get_old_position()

    # TODO: the isinstance stuff for move_children is really gross

    def redo(self):
        if isinstance(self.item, pyweritems.PywerGroup):
            self.item.move_children = False
        self.item.setPos(self.new_position)
        if isinstance(self.item, pyweritems.PywerGroup):
            self.item.move_children = True

    def undo(self):
        if isinstance(self.item, pyweritems.PywerGroup):
            self.item.move_children = False
        self.item.setPos(self.old_position)
        if isinstance(self.item, pyweritems.PywerGroup):
            self.item.move_children = True


class RenameItem(QtWidgets.QUndoCommand):
    def __init__(self, context, item):
        super().__init__()
        self.item = item
        self.new_name = item.name.toPlainText()
        self.scene = context.get('scene')
        self.prev_scene_data = context.get('scene_data')

        if isinstance(self.item, pyweritems.PywerNode):
            for node in self.prev_scene_data['nodes']:
                if str(node['id']) == str(self.item.node_obj.obj_id):
                    self.prev_name = node['name']

        elif isinstance(self.item, pyweritems.PywerGroup):
            for group in self.prev_scene_data['groups']:
                if str(group['id']) == str(self.item.node_obj.obj_id):
                    self.prev_name = group['name']

    def redo(self):
        self.item.name.setPlainText(self.new_name)

    def undo(self):
        self.item.name.setPlainText(self.prev_name)


class ResizeItem(QtWidgets.QUndoCommand):
    def __init__(self, context, item):
        super().__init__()
        self.item = item
        self.scene = context.get('scene')
        self.prev_scene_data = context.get('scene_data')
        self.new_size = item.size()
        self.old_size = item.get_old_size()
        self.prev_items = context.get('current_selection')

    def redo(self):
        self.item.setSize(*self.new_size)
        self.item.setSelected(True)

    def undo(self):
        self.item.setSize(*self.old_size)
        self.item.setSelected(False)
        for item in self.prev_items:
            item.setSelected(True)


class AddNode(QtWidgets.QUndoCommand):
    def __init__(self, context, item, position=None, size=None):
        super().__init__()
        self.scene = context.get('scene')
        self.worker = context.get('worker')
        self.prev_selection = self.scene.get_selected_items()
        self.node = appnode.new_node(item, position=position, size=size)

        self.node.node_obj.moveToThread(self.worker)

    def redo(self):
        self.scene.add_node(self.node)
        self.scene.clearSelection()
        self.node.setSelected(True)

    def undo(self):
        self.scene.remove_node(self.node)
        self.scene.clearSelection()
        for item in self.prev_selection:
            item.setSelected(True)


class AddGroup(QtWidgets.QUndoCommand):
    def __init__(self, context, position, size):
        super().__init__()
        self.scene = context.get('scene')
        self.worker = context.get('worker')
        self.prev_selection = self.scene.get_selected_items()
        self.group = appnode.new_group(position=position)
        self.group.width = size.width()
        self.group.height = size.height()
        self.group.adjust()

    def redo(self):
        self.scene.add_group(self.group)
        self.scene.clearSelection()
        self.group.setSelected(True)

    def undo(self):
        self.scene.remove_item(self.group)
        self.scene.clearSelection()
        for item in self.prev_selection:
            item.setSelected(True)


class RemoveItem(QtWidgets.QUndoCommand):
    def __init__(self, context, item):
        super().__init__()
        self.item = item
        self.scene = context.get('scene')
        self.prev_selection = self.scene.get_selected_items()
        self.prev_scene_data = context.get('scene_data')
        self.prev_edges = self.get_edges()

    def get_edges(self):
        edges = []
        if not isinstance(self.item, pyweritems.PywerNode):
            return edges

        for plug in self.item.inputs + self.item.outputs:
            for e in plug.edges:
                edges.append((e, e.source_plug, e.target_plug))

        return edges

    def redo(self):
        self.scene.remove_item(self.item)
        self.scene.clearSelection()

        for edge in self.prev_edges:
            e, source_plug, target_plug = edge
            appnode.disconnect_plugs(source_plug, target_plug)

    def undo(self):
        self.scene.addItem(self.item)
        self.scene.clearSelection()
        for item in self.prev_selection:
            item.setSelected(True)

        for edge in self.prev_edges:
            e, source_plug, target_plug = edge
            e.connect_plugs(source_plug, target_plug)
            self.scene.addItem(e)
            appnode.connect_plugs(source_plug, target_plug)


class ConnectPlugs(QtWidgets.QUndoCommand):
    def __init__(self, context, source_plug, target_plug):
        super().__init__()
        self.source_plug = source_plug
        self.target_plug = target_plug
        self.scene = context.get('scene')
        self.edge = pyweritems.PywerEdge()
        self.prev_selection = context.get('current_selection')

    def redo(self):
        self.scene.addItem(self.edge)
        self.edge.connect_plugs(self.source_plug, self.target_plug)
        appnode.connect_plugs(self.source_plug, self.target_plug)

        self.scene.clearSelection()

    def undo(self):
        self.scene.remove_item(self.edge)
        self.edge.disconnect()
        appnode.disconnect_plugs(self.source_plug, self.target_plug)

        self.scene.clearSelection()
        for item in self.prev_selection:
            item.setSelected(True)


class Disconnect(QtWidgets.QUndoCommand):
    def __init__(self, context, source_plug, target_plug):
        super().__init__()
        self.source_plug = source_plug
        self.target_plug = target_plug
        self.scene = context.get('scene')
        self.edge = self._find_edge(self.source_plug)

    def _find_edge(self, plug):
        for edge in plug.edges:
            if edge.target_plug == self.target_plug:
                return edge

    def redo(self):
        self.scene.removeItem(self.edge)
        self.edge.disconnect()
        appnode.disconnect_plugs(self.source_plug, self.target_plug)

    def undo(self):
        self.scene.addItem(self.edge)
        self.edge.connect_plugs(self.source_plug, self.target_plug)
        appnode.connect_plugs(self.source_plug, self.target_plug)


class ParamValue(QtWidgets.QUndoCommand):
    def __init__(self, context, node, param):
        super().__init__()
        self.node = node
        self.param = param
        self.value = self.param.value
        self.old_value = self.param._old_value

    def redo(self):
        self.param.value = self.value
        self.node.update()

    def undo(self):
        self.param.value = self.old_value
        self.node.update()
