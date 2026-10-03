"""Editor helpers using the shared versioned graph reconstruction pipeline."""
from copy import deepcopy
import uuid
from PySide6 import QtCore, QtGui
import graph_document
from pywerlines import pyweritems


def get_scene_data(scene, selection=None):
    return graph_document.snapshot(scene, selection)


def _prepare(data, pos=None, fresh_ids=False):
    document = graph_document.migrate(data)
    if fresh_ids:
        mapping = {item['id']: str(uuid.uuid4()) for key in ('nodes', 'groups', 'edges') for item in document[key]}
        for key in ('nodes', 'groups', 'edges'):
            for item in document[key]:
                item['id'] = mapping[item['id']]
        for edge in document['edges']:
            for end in ('source', 'target'):
                edge[end]['node_id'] = mapping[edge[end]['node_id']]
    items = document['nodes'] + document['groups']
    if pos is not None and items:
        x, y = items[0]['position']
        for item in items:
            item['position'] = [item['position'][0] + pos.x() - x, item['position'][1] + pos.y() - y]
    return document


class InsertGraph(QtGui.QUndoCommand):
    """Keep reconstructed graph objects alive across clipboard history."""
    def __init__(self, context, document):
        super().__init__()
        self.scene = context['scene']
        graph_document.check_collisions(self.scene, document)
        self.staged = graph_document.stage(document)
        self.items = [item for item in self.staged.items() if item.parentItem() is None]
        self.nodes = self.staged.get_all_nodes()
        self.enabled = {n: n.node_obj.active for n in self.nodes}
        self.result = {n: record for n in self.nodes for record in document['nodes'] if str(n.node_obj.obj_id) == record['id']}
        self.result.update({g: record for g in self.staged.get_all_groups() for record in document['groups'] if str(g.node_obj.obj_id) == record['id']})

    def redo(self):
        for item in self.items:
            self.scene.addItem(item)
        for node in self.nodes:
            node.node_obj.active = self.enabled[node]
        graph_document.activate_nodes(self.nodes)
        self.scene.clearSelection()
        for item in self.result:
            item.setSelected(True)

    def undo(self):
        for node in self.nodes:
            node.node_obj.set_active(False)
            node.node_obj.pause_resources()
        for item in self.items:
            self.scene.removeItem(item)
            self.staged.addItem(item)


def load_macro(context, undo_stack, data, pos=None):
    document = _prepare(data, pos)
    command = InsertGraph(context, document)
    undo_stack.push(command)
    return command.result


def paste_macro(context, undo_stack, data, pos=None):
    document = _prepare(data, pos, fresh_ids=True)
    command = InsertGraph(context, document)
    undo_stack.push(command)
    return command.result


def load_scene_data(scene, data, pos=None):
    document = _prepare(data, pos, fresh_ids=True)
    staged = graph_document.stage(document)
    result = {n: record for n in staged.get_all_nodes() for record in document['nodes'] if str(n.node_obj.obj_id) == record['id']}
    result.update({g: record for g in staged.get_all_groups() for record in document['groups'] if str(g.node_obj.obj_id) == record['id']})
    graph_document.install(scene, staged)
    graph_document.activate_nodes([n for n in result if isinstance(n, pyweritems.PywerNode)])
    return result


def create_group(scene, position):
    group = scene.create_group()
    group.setPos(position)


def group_selected_nodes(scene):
    scene.group_selected_nodes()


def delete_selected(scene):
    scene.remove_selected_items()


def select_all(scene):
    scene.select_all()


def select(scene, items=None):
    if items is None:
        items = []

    scene.clearSelection()
    for item in items:
        item.setSelected(True)
